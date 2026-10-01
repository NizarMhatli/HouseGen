"""Furniture placement for HouseGen.

Places room-appropriate furniture in each room using a catalogue of
parametric box-based proxies. Placement is margin-aware and
deterministic given a seed.

Catalogue entry shape
---------------------
Each entry is a dict with:
    name        : str   base object name
    sx, sy, sz  : float dimensions (before randomisation)
    rand_s      : float ±fraction to randomise each dimension
    z_offset    : float how much to lift above floor (sz/2 normally)
    margin      : float clearance from walls
    weight      : float relative spawn probability
    colors      : list of (r,g,b) tuples to pick from
"""

import random
import math
import bpy

from modules.types import Config, RoomDict
from modules.geometry import make_box


# ── Furniture catalogue ────────────────────────────────────────────────────

def _rand_dim(base: float, frac: float) -> float:
    return base * random.uniform(1 - frac, 1 + frac)


CATALOGUE: dict[str, list[dict]] = {

    "living": [
        dict(name="sofa",        sx=2.0, sy=0.85, sz=0.75, rand_s=0.15,
             margin=0.3, colors=[(0.3,0.35,0.6),(0.5,0.3,0.2),(0.7,0.7,0.65)]),
        dict(name="armchair",    sx=0.75, sy=0.75, sz=0.70, rand_s=0.1,
             margin=0.25, colors=[(0.4,0.3,0.5),(0.6,0.4,0.2)]),
        dict(name="coffee_table",sx=1.0, sy=0.55, sz=0.40, rand_s=0.15,
             margin=0.1, colors=[(0.55,0.35,0.15),(0.3,0.3,0.3)]),
        dict(name="tv_stand",    sx=1.5, sy=0.45, sz=0.50, rand_s=0.1,
             margin=0.05, colors=[(0.2,0.2,0.2),(0.55,0.35,0.15)]),
        dict(name="bookshelf",   sx=0.9, sy=0.35, sz=1.8,  rand_s=0.1,
             margin=0.05, colors=[(0.55,0.35,0.15),(0.4,0.4,0.4)]),
        dict(name="rug",         sx=2.0, sy=1.5,  sz=0.02, rand_s=0.2,
             margin=0.4, colors=[(0.6,0.4,0.3),(0.3,0.4,0.5),(0.5,0.5,0.4)]),
        dict(name="plant",       sx=0.3, sy=0.3,  sz=0.8,  rand_s=0.3,
             margin=0.15, colors=[(0.2,0.5,0.2)]),
    ],

    "kitchen": [
        dict(name="counter",     sx=0.6, sy=2.5,  sz=0.9,  rand_s=0.2,
             margin=0.05, colors=[(0.75,0.75,0.75),(0.9,0.85,0.8)]),
        dict(name="island",      sx=1.0, sy=0.7,  sz=0.9,  rand_s=0.2,
             margin=0.5, colors=[(0.8,0.8,0.8),(0.6,0.55,0.5)]),
        dict(name="fridge",      sx=0.7, sy=0.65, sz=1.8,  rand_s=0.05,
             margin=0.05, colors=[(0.92,0.92,0.92),(0.3,0.3,0.3)]),
        dict(name="stove",       sx=0.6, sy=0.6,  sz=0.9,  rand_s=0.05,
             margin=0.05, colors=[(0.3,0.3,0.3),(0.7,0.7,0.7)]),
        dict(name="dining_table",sx=1.2, sy=0.8,  sz=0.75, rand_s=0.15,
             margin=0.5, colors=[(0.55,0.35,0.15),(0.3,0.25,0.2)]),
        dict(name="chair",       sx=0.45, sy=0.45,sz=0.45, rand_s=0.1,
             margin=0.1, colors=[(0.55,0.35,0.15),(0.8,0.8,0.8)]),
    ],

    "bedroom": [
        dict(name="bed",         sx=2.0, sy=1.6,  sz=0.55, rand_s=0.1,
             margin=0.3, colors=[(0.8,0.6,0.6),(0.6,0.7,0.8),(0.85,0.85,0.8)]),
        dict(name="wardrobe",    sx=0.6, sy=1.4,  sz=2.0,  rand_s=0.1,
             margin=0.05, colors=[(0.55,0.35,0.15),(0.4,0.4,0.4)]),
        dict(name="desk",        sx=0.6, sy=1.2,  sz=0.75, rand_s=0.1,
             margin=0.1, colors=[(0.55,0.35,0.15),(0.3,0.3,0.3)]),
        dict(name="desk_chair",  sx=0.5, sy=0.5,  sz=0.45, rand_s=0.1,
             margin=0.2, colors=[(0.3,0.3,0.3),(0.6,0.4,0.2)]),
        dict(name="nightstand",  sx=0.45,sy=0.4,  sz=0.50, rand_s=0.1,
             margin=0.05, colors=[(0.55,0.35,0.15)]),
        dict(name="dresser",     sx=0.5, sy=1.0,  sz=0.9,  rand_s=0.1,
             margin=0.05, colors=[(0.55,0.35,0.15),(0.4,0.4,0.4)]),
    ],

    "bathroom": [
        dict(name="toilet",      sx=0.4, sy=0.65, sz=0.75, rand_s=0.05,
             margin=0.1, colors=[(0.95,0.95,0.95)]),
        dict(name="sink",        sx=0.5, sy=0.4,  sz=0.85, rand_s=0.05,
             margin=0.05, colors=[(0.92,0.92,0.92)]),
        dict(name="bathtub",     sx=0.8, sy=1.6,  sz=0.55, rand_s=0.05,
             margin=0.1, colors=[(0.92,0.92,0.95)]),
        dict(name="towel_rack",  sx=0.6, sy=0.1,  sz=0.8,  rand_s=0.1,
             margin=0.05, colors=[(0.7,0.7,0.7)]),
    ],

    "hallway": [
        dict(name="shoe_rack",   sx=0.9, sy=0.35, sz=0.5,  rand_s=0.2,
             margin=0.05, colors=[(0.55,0.35,0.15)]),
        dict(name="umbrella_stand",sx=0.2,sy=0.2, sz=0.6,  rand_s=0.2,
             margin=0.05, colors=[(0.3,0.3,0.3)]),
    ],
}


def generate_furniture(
    name: str,
    rooms: list[RoomDict],
    config: Config,
) -> list[bpy.types.Object]:
    """Place furniture in all rooms.

    Parameters
    ----------
    name : str
        Object name prefix.
    rooms : list of dict
        Room layout from modules.layout.
    config : dict
        The ``furniture`` sub-dict from features.

    Returns
    -------
    list of bpy.types.Object
    """
    density = config.get("density", 1.0)   # 0-2, scales how many pieces
    objs = []

    for room in rooms:
        rtype = room["type"]
        items = CATALOGUE.get(rtype, [])
        if not items:
            continue

        n_items = max(1, int(len(items) * density * random.uniform(0.6, 1.0)))
        chosen = random.sample(items, min(n_items, len(items)))

        placed = []  # list of (cx, cy, sx, sy) for collision checking

        for item in chosen:
            sx = _rand_dim(item["sx"], item.get("rand_s", 0.1))
            sy = _rand_dim(item["sy"], item.get("rand_s", 0.1))
            sz = _rand_dim(item["sz"], item.get("rand_s", 0.05))
            margin = item.get("margin", 0.2)

            # Try to place within room bounds
            x_lo = room["x_min"] + margin + sx / 2
            x_hi = room["x_max"] - margin - sx / 2
            y_lo = room["y_min"] + margin + sy / 2
            y_hi = room["y_max"] - margin - sy / 2

            if x_lo >= x_hi or y_lo >= y_hi:
                continue  # room too small for this item

            # Try random placement up to 10 times
            placed_ok = False
            for _ in range(10):
                cx = random.uniform(x_lo, x_hi)
                cy = random.uniform(y_lo, y_hi)

                # Simple overlap check
                overlap = False
                for (ox, oy, osx, osy) in placed:
                    if (abs(cx - ox) < (sx + osx) / 2 + 0.15 and
                            abs(cy - oy) < (sy + osy) / 2 + 0.15):
                        overlap = True
                        break
                if not overlap:
                    placed_ok = True
                    break

            if not placed_ok:
                continue

            cz = sz / 2
            color = random.choice(item.get("colors", [(0.5, 0.5, 0.5)]))
            obj_name = f"{name}_{room['name']}_{item['name']}"
            obj = make_box(obj_name, cx, cy, cz, sx, sy, sz)
            _apply_color(obj, color)
            objs.append(obj)
            placed.append((cx, cy, sx, sy))

    return objs


def _apply_color(obj: bpy.types.Object, color: tuple) -> None:
    """Apply a flat diffuse material to an object."""
    mat = bpy.data.materials.new(name=obj.name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
