"""Master orchestrator for HouseGen — mirrors TunnelGen's tunnel.py.

Calls each pipeline stage in order and collects results into a HouseScene.
"""

import random

import modules.rng as rng
import modules.layout   as layout
import modules.walls    as walls
import modules.furniture as furniture
import modules.lights   as lights
import modules.materials as materials

from modules.types import HouseSpec, HouseScene


def generate_scene(spec: HouseSpec) -> HouseScene:
    """Run the full generation pipeline and return a HouseScene.

    Parameters
    ----------
    spec : HouseSpec
        The scene specification built by a scenes/ preset.

    Returns
    -------
    HouseScene
        All generated objects, grouped by type.
    """
    cfg = spec.features
    wall_height = cfg.get("wall_height", 2.8)

    scene = HouseScene(
        name=spec.name,
        seed=spec.seed,
        config=cfg,
        scene_name=spec.scene_name,
    )

    # ── 1. Floor plan layout ───────────────────────────────────
    rng.seed_stage(spec.seed, "layout")
    rooms = layout.generate_layout(cfg.get("layout", {}))
    scene.rooms = rooms
    print(f"[house] Layout: {len(rooms)} rooms — "
          + ", ".join(f"{r['name']}({r['width']:.1f}x{r['depth']:.1f}m)"
                      for r in rooms))

    # ── 2. Walls, floor, ceiling ───────────────────────────────
    rng.seed_stage(spec.seed, "walls")
    wall_objs = walls.generate_walls(
        spec.name, rooms, wall_height, cfg.get("walls", {}))
    scene.add("walls", wall_objs)
    print(f"[house] Walls: {len(wall_objs)} segments")

    # ── 3. Furniture ───────────────────────────────────────────
    rng.seed_stage(spec.seed, "furniture")
    furn_objs = furniture.generate_furniture(
        spec.name, rooms, cfg.get("furniture", {}))
    scene.add("furniture", furn_objs)
    print(f"[house] Furniture: {len(furn_objs)} pieces")

    # ── 4. Lights ──────────────────────────────────────────────
    rng.seed_stage(spec.seed, "lights")
    lamps = lights.generate_lights(
        spec.name, rooms, wall_height, cfg.get("lights", {}))
    scene.lamps = lamps
    scene.add("fixtures", [l["mesh_obj"] for l in lamps])
    print(f"[house] Lights: {len(lamps)}")

    # ── 5. Materials ───────────────────────────────────────────
    try:
        materials.apply_all(wall_objs, furn_objs, cfg.get("materials", {}))
        print("[house] Materials applied")
    except Exception as e:
        print(f"[house] Materials skipped: {e}")

    print(scene.summary())
    return scene
