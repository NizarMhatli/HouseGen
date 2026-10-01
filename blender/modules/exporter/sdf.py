"""SDF writers for HouseGen — adapted from TunnelGen's exporter/sdf.py.

Produces:
  <export_dir>/<model_name>/model.sdf       — static house link
  <export_dir>/<model_name>/model.config    — model metadata
  <export_dir>/worlds/house_world.sdf       — world file
  <export_dir>/worlds/house_meta.json       — spawn poses + room centers
"""

import os
import json
import xml.etree.ElementTree as ET

from modules.types import Config, LampDict, RoomDict, HouseScene
from .xml_helpers import _pretty_xml, _sub, _pose_str, _quat_to_rpy


def _build_visual(parent, name, mesh_uri, color):
    vis = _sub(parent, "visual", name=name)
    geom = _sub(vis, "geometry")
    mesh = _sub(geom, "mesh")
    _sub(mesh, "uri", mesh_uri)
    mat = _sub(vis, "material")
    r, g, b = color
    _sub(mat, "ambient",  f"{r:.3f} {g:.3f} {b:.3f} 1")
    _sub(mat, "diffuse",  f"{r:.3f} {g:.3f} {b:.3f} 1")
    _sub(mat, "specular", "0.05 0.05 0.05 1")
    return vis


def _build_collision(parent, name, mesh_uri):
    col = _sub(parent, "collision", name=name)
    geom = _sub(col, "geometry")
    mesh = _sub(geom, "mesh")
    _sub(mesh, "uri", mesh_uri)
    surface = _sub(col, "surface")
    friction = _sub(surface, "friction")
    ode = _sub(friction, "ode")
    _sub(ode, "mu",  "0.8")
    _sub(ode, "mu2", "0.8")
    return col


def write_model_sdf(
    export_dir: str,
    model_name: str,
    visual_meshes: dict[str, tuple[str, tuple]],
    collision_meshes: dict[str, str],
) -> str:
    """Write model.sdf for the house.

    Parameters
    ----------
    visual_meshes : dict
        name -> (filename, (r,g,b))
    collision_meshes : dict
        name -> filename
    """
    sdf = ET.Element("sdf", version="1.9")
    model = _sub(sdf, "model", name=model_name)
    _sub(model, "static", "true")
    link = _sub(model, "link", name="house_link")

    for name, (fname, color) in visual_meshes.items():
        _build_visual(link, f"visual_{name}", f"meshes/{fname}", color)

    for name, fname in collision_meshes.items():
        _build_collision(link, f"collision_{name}", f"meshes/{fname}")

    path = os.path.join(export_dir, model_name, "model.sdf")
    with open(path, "w") as f:
        f.write(_pretty_xml(sdf))
    print(f"[exporter] model.sdf → {path}")
    return path


def write_model_config(export_dir: str, model_name: str) -> str:
    model_el = ET.Element("model")
    _sub(model_el, "name", model_name)
    _sub(model_el, "version", "1.0")
    _sub(model_el, "sdf", "model.sdf", version="1.9")
    author = _sub(model_el, "author")
    _sub(author, "name", "HouseGen")
    _sub(model_el, "description", f"Procedural house model: {model_name}")

    path = os.path.join(export_dir, model_name, "model.config")
    with open(path, "w") as f:
        f.write(_pretty_xml(model_el))
    return path


def write_world_sdf(
    export_dir: str,
    model_name: str,
    scene: HouseScene,
    config: Config,
) -> str:
    """Write worlds/house_world.sdf."""
    world_name = config.get("export", {}).get("world_name", f"house_{scene.seed}")

    sdf = ET.Element("sdf", version="1.9")
    world = _sub(sdf, "world", name=world_name)

    # Physics — match jig_world.sdf settings
    physics = _sub(world, "physics", name="1ms", type="ignored")
    _sub(physics, "max_step_size", "0.004")
    _sub(physics, "real_time_factor", "1.0")
    _sub(physics, "real_time_update_rate", "250")

    # Plugins
    for fname, pname in [
        ("gz-sim-physics-system",          "gz::sim::systems::Physics"),
        ("gz-sim-user-commands-system",    "gz::sim::systems::UserCommands"),
        ("gz-sim-scene-broadcaster-system","gz::sim::systems::SceneBroadcaster"),
    ]:
        _sub(world, "plugin", filename=fname, name=pname)

    sensors_plugin = _sub(world, "plugin",
                          filename="gz-sim-sensors-system",
                          name="gz::sim::systems::Sensors")
    _sub(sensors_plugin, "render_engine", "ogre2")

    # Sun
    sun = _sub(world, "light", name="sun", type="directional")
    _sub(sun, "cast_shadows", "true")
    _sub(sun, "pose", "0 0 10 0 0 0")
    _sub(sun, "diffuse",  "0.85 0.85 0.80 1")
    _sub(sun, "specular", "0.2 0.2 0.2 1")
    _sub(sun, "direction", "-0.3 0.1 -0.9")

    # Room lights
    for i, lamp in enumerate(scene.lamps):
        sdf_data = lamp.get("sdf", {})
        wp = lamp["world_pos"]
        light = _sub(world, "light", name=f"room_light_{i}", type="point")
        _sub(light, "pose", _pose_str(wp.x, wp.y, wp.z, 0, 0, 0))
        diff = sdf_data.get("diffuse", [1, 1, 1, 1])
        spec = sdf_data.get("specular", [0.2, 0.2, 0.2, 1])
        _sub(light, "diffuse",  " ".join(f"{v:.3f}" for v in diff))
        _sub(light, "specular", " ".join(f"{v:.3f}" for v in spec))
        att = sdf_data.get("attenuation", {})
        att_el = _sub(light, "attenuation")
        _sub(att_el, "range",    str(att.get("range", 8)))
        _sub(att_el, "constant", str(att.get("constant", 0.5)))
        _sub(att_el, "linear",   str(att.get("linear", 0.1)))
        _sub(att_el, "quadratic",str(att.get("quadratic", 0.01)))
        _sub(light, "cast_shadows", "true")

    # House model include
    inc = _sub(world, "include")
    _sub(inc, "uri", f"model://{model_name}")
    _sub(inc, "name", model_name)

    # Jig spawn point (living room center)
    living = next((r for r in scene.rooms if r["type"] == "living"), scene.rooms[0])
    spawn = _sub(world, "frame", name="jig_spawn")
    _sub(spawn, "pose", _pose_str(living["cx"], living["cy"], 0.05, 0, 0, 0))

    path = os.path.join(export_dir, "worlds", f"{world_name}.sdf")
    with open(path, "w") as f:
        f.write(_pretty_xml(sdf))
    print(f"[exporter] world → {path}")
    return path


def write_meta_json(
    export_dir: str,
    scene: HouseScene,
    config: Config,
) -> str:
    """Write worlds/house_meta.json — room centers + spawn for ROS."""
    world_name = config.get("export", {}).get("world_name", f"house_{scene.seed}")

    living = next((r for r in scene.rooms if r["type"] == "living"), scene.rooms[0])
    meta = {
        "world_name": world_name,
        "seed": scene.seed,
        "spawn": {"x": living["cx"], "y": living["cy"], "z": 0.05, "yaw": 0.0},
        "rooms": [
            {
                "name":  r["name"],
                "type":  r["type"],
                "center": {"x": r["cx"], "y": r["cy"]},
                "bounds": {
                    "x_min": r["x_min"], "x_max": r["x_max"],
                    "y_min": r["y_min"], "y_max": r["y_max"],
                },
            }
            for r in scene.rooms
        ],
    }

    path = os.path.join(export_dir, "worlds", f"house_meta_{scene.seed}.json")
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[exporter] meta → {path}")
    return path
