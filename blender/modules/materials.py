"""Procedural material assignment for HouseGen.

Assigns Principled BSDF materials to wall, floor, and ceiling objects
based on their name tags. Mirrors TunnelGen's materials.py approach.
"""

import bpy
from modules.types import Config


# ── Material presets ──────────────────────────────────────────────────────

PRESETS: dict[str, dict] = {
    "wall": {
        "color":     (0.92, 0.91, 0.88),
        "roughness": 0.85,
        "metallic":  0.0,
    },
    "floor": {
        "color":     (0.60, 0.50, 0.38),
        "roughness": 0.70,
        "metallic":  0.0,
    },
    "ceiling": {
        "color":     (0.98, 0.98, 0.97),
        "roughness": 0.90,
        "metallic":  0.0,
    },
    "door": {
        "color":     (0.60, 0.42, 0.25),
        "roughness": 0.60,
        "metallic":  0.0,
    },
}


def _make_material(name: str, preset: dict) -> bpy.types.Material:
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        c = preset["color"]
        bsdf.inputs["Base Color"].default_value = (*c, 1.0)
        bsdf.inputs["Roughness"].default_value  = preset.get("roughness", 0.8)
        bsdf.inputs["Metallic"].default_value   = preset.get("metallic", 0.0)
    return mat


def apply_all(
    wall_objs:      list[bpy.types.Object],
    furniture_objs: list[bpy.types.Object],
    config:         Config,
) -> None:
    """Apply procedural materials to all house objects.

    Parameters
    ----------
    wall_objs : list
        All wall/floor/ceiling objects.
    furniture_objs : list
        Furniture objects (already have materials from furniture.py).
    config : dict
        The ``materials`` sub-dict from features.
    """
    # Build shared materials once
    mats = {k: _make_material(f"house_{k}", v) for k, v in PRESETS.items()}

    for obj in wall_objs:
        n = obj.name.lower()
        if "floor" in n:
            key = "floor"
        elif "ceiling" in n:
            key = "ceiling"
        else:
            key = "wall"

        mat = mats[key]
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
