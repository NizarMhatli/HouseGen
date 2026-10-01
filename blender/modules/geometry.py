"""Low-level geometry helpers for HouseGen.

Provides box/wall building primitives using bmesh, mirroring TunnelGen's
geometry.py approach but adapted for rectilinear house architecture.
"""

import bpy
import bmesh
import mathutils


def make_box(
    name: str,
    cx: float, cy: float, cz: float,
    sx: float, sy: float, sz: float,
) -> bpy.types.Object:
    """Create a box mesh object centered at (cx, cy, cz) with dimensions (sx, sy, sz).

    Parameters
    ----------
    name : str
        Blender object name.
    cx, cy, cz : float
        Center position in world space.
    sx, sy, sz : float
        Full dimensions (width, depth, height).

    Returns
    -------
    bpy.types.Object
        The created mesh object, linked to the active collection.
    """
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()

    obj.location = (cx, cy, cz)
    obj.scale = (sx, sy, sz)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True, location=False)
    return obj


def wall_segment(
    name: str,
    x1: float, y1: float,
    x2: float, y2: float,
    z_bot: float, z_top: float,
    gap_start: float | None = None,
    gap_end: float | None = None,
    gap_height: float = 2.1,
) -> list[bpy.types.Object]:
    """Build a wall from (x1,y1) to (x2,y2) with an optional door/window gap.

    Parameters
    ----------
    name : str
        Base name for generated objects.
    x1, y1, x2, y2 : float
        Wall endpoints in XY.
    z_bot, z_top : float
        Bottom and top Z of wall.
    gap_start, gap_end : float or None
        Distance along wall length where gap begins/ends.
        None = solid wall.
    gap_height : float
        Height of gap (door height). Default 2.1 m.

    Returns
    -------
    list of bpy.types.Object
        Created wall segment objects.
    """
    import math
    length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if length < 0.01:
        return []

    dx = (x2 - x1) / length
    dy = (y2 - y1) / length
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    cz = (z_bot + z_top) / 2
    h = z_top - z_bot

    is_x_wall = abs(x2 - x1) >= abs(y2 - y1)
    T = 0.15  # wall thickness

    objs = []

    if gap_start is None:
        # Solid wall
        sx = length if is_x_wall else T
        sy = T if is_x_wall else length
        objs.append(make_box(name, cx, cy, cz, sx, sy, h))
    else:
        g0, g1 = gap_start, gap_end
        pre_len = g0
        post_len = length - g1
        gap_len = g1 - g0

        # Before gap
        if pre_len > 0.05:
            px = x1 + dx * (pre_len / 2)
            py = y1 + dy * (pre_len / 2)
            sx = pre_len if is_x_wall else T
            sy = T if is_x_wall else pre_len
            objs.append(make_box(name + "_pre", px, py, cz, sx, sy, h))

        # After gap
        if post_len > 0.05:
            px = x1 + dx * (g1 + post_len / 2)
            py = y1 + dy * (g1 + post_len / 2)
            sx = post_len if is_x_wall else T
            sy = T if is_x_wall else post_len
            objs.append(make_box(name + "_post", px, py, cz, sx, sy, h))

        # Lintel above gap
        lintel_h = h - gap_height
        if lintel_h > 0.05:
            px = x1 + dx * (g0 + gap_len / 2)
            py = y1 + dy * (g0 + gap_len / 2)
            lz = z_bot + gap_height + lintel_h / 2
            sx = gap_len if is_x_wall else T
            sy = T if is_x_wall else gap_len
            objs.append(make_box(name + "_lintel", px, py, lz, sx, sy, lintel_h))

    return objs
