"""Gazebo SDF + OBJ export for HouseGen.

Mirrors TunnelGen's exporter/__init__.py structure.
Entry point: export_gazebo(scene, output_dir).
"""

import os
import bpy

from modules.types import HouseScene, Config
from .mesh import _export_mesh, _extract_base_color
from .sdf  import write_model_sdf, write_model_config, write_world_sdf, write_meta_json


def export_gazebo(scene: HouseScene, output_dir: str) -> None:
    """Export the house scene to Gazebo SDF + OBJ.

    Output layout (mirrors TunnelGen)::

        <output_dir>/
          <model_name>/
            model.sdf
            model.config
            meshes/
              walls.obj
              furniture.obj
              fixtures.obj
          worlds/
            <world_name>.sdf
            house_meta.json

    Parameters
    ----------
    scene : HouseScene
        The generated scene.
    output_dir : str
        Root export directory (absolute).
    """
    config     = scene.config
    model_name = config.get("export", {}).get("model_name", scene.name.lower())

    # ── Directory setup ────────────────────────────────────────
    model_dir  = os.path.join(output_dir, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    worlds_dir = output_dir
    for d in (model_dir, meshes_dir, worlds_dir):
        os.makedirs(d, exist_ok=True)

    visual_meshes:    dict[str, tuple[str, tuple]] = {}
    collision_meshes: dict[str, str]               = {}

    # ── Walls ──────────────────────────────────────────────────
    wall_objs = scene.objects("walls")
    if wall_objs:
        wall_path = os.path.join(meshes_dir, "walls.obj")
        _export_mesh(wall_objs, wall_path)
        color = _extract_base_color(wall_objs[0])
        visual_meshes["walls"]    = ("walls.obj", color)
        collision_meshes["walls"] = "walls.obj"  # same mesh for collision
        print(f"[exporter] walls.obj — {len(wall_objs)} objects")

    # ── Furniture ──────────────────────────────────────────────
    furn_objs = scene.objects("furniture")
    if furn_objs:
        furn_path = os.path.join(meshes_dir, "furniture.obj")
        _export_mesh(furn_objs, furn_path)
        color = _extract_base_color(furn_objs[0])
        visual_meshes["furniture"] = ("furniture.obj", color)
        # Furniture gets collision too (robots should bump into it)
        collision_meshes["furniture"] = "furniture.obj"
        print(f"[exporter] furniture.obj — {len(furn_objs)} objects")

    # ── Light fixtures ─────────────────────────────────────────
    fix_objs = scene.objects("fixtures")
    if fix_objs:
        fix_path = os.path.join(meshes_dir, "fixtures.obj")
        _export_mesh(fix_objs, fix_path)
        visual_meshes["fixtures"] = ("fixtures.obj", (0.9, 0.9, 0.85))
        print(f"[exporter] fixtures.obj — {len(fix_objs)} objects")

    # ── SDF files ──────────────────────────────────────────────
    write_model_sdf(output_dir, model_name, visual_meshes, collision_meshes)
    write_model_config(output_dir, model_name)
    write_world_sdf(output_dir, model_name, scene, config)
    write_meta_json(output_dir, scene, config)

    print(f"\n✅ HouseGen export complete → {output_dir}")
    print(f"   Model : {model_dir}")
    print(f"   World : {worlds_dir}")
    print(f"   Seed  : {scene.seed}")
    print(f"\nLaunch in Gazebo:")
    world_name = config.get("export", {}).get("world_name", f"house_{scene.seed}")
    print(f"   gz sim {worlds_dir}/{world_name}.sdf")
