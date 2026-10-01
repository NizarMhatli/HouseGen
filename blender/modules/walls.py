"""Wall generation for HouseGen.

Builds exterior walls, interior dividers, doors, and windows
from the room layout produced by modules.layout.

All wall segments have collision-ready geometry (no subdivision noise).
Door gaps are cut wherever rooms share a wall.
"""

import random
import math
import bpy

from modules.types import Config, RoomDict
from modules.geometry import make_box, wall_segment


# Wall thickness (m)
T = 0.15
# Floor thickness (m)
FT = 0.05


def generate_walls(
    name: str,
    rooms: list[RoomDict],
    wall_height: float,
    config: Config,
) -> list[bpy.types.Object]:
    """Build all walls for the house.

    Parameters
    ----------
    name : str
        Object name prefix.
    rooms : list of dict
        Room layout from modules.layout.generate_layout.
    wall_height : float
        Interior ceiling height in metres.
    config : dict
        The ``walls`` sub-dict from features.

    Returns
    -------
    list of bpy.types.Object
        All wall segment objects.
    """
    door_w = config.get("door_width", random.uniform(0.85, 1.0))
    door_h = config.get("door_height", 2.1)
    win_w  = config.get("window_width", random.uniform(1.0, 1.6))
    win_h  = config.get("window_height", 1.2)
    win_sill = config.get("window_sill", 0.9)

    H = wall_height
    objs = []

    # Read house dims from layout metadata stored on first room
    r0 = rooms[0]
    hx = r0["house_hx"]
    hy = r0["house_hy"]
    div_x = r0["div_x"]
    div_y = r0["div_y"]
    hallway_d = r0["hallway_d"]
    bath_w = r0.get("bath_w", 0.0)
    bath_d = r0.get("bath_d", 0.0)
    int_y_min = -hy + hallway_d

    # ── Exterior walls ─────────────────────────────────────────

    # South wall (front) — front door gap
    fd_pos = random.uniform(hx * 0.3, hx * 0.7)
    objs += wall_segment(f"{name}_wall_S",
                         -hx, -hy, hx, -hy, 0, H,
                         fd_pos - door_w / 2, fd_pos + door_w / 2, door_h)

    # North wall — window
    win_pos = random.uniform(0.2, hx * 2 - 0.2 - win_w)
    objs += wall_segment(f"{name}_wall_N",
                         -hx, hy, hx, hy, 0, H,
                         win_pos, win_pos + win_w, win_h + win_sill)
    # Window sill solid section below window
    if win_sill > 0.05:
        objs.append(make_box(
            f"{name}_wall_N_sill",
            -hx + win_pos + win_w / 2, hy,
            win_sill / 2,
            win_w, T, win_sill,
        ))

    # West wall
    objs += wall_segment(f"{name}_wall_W",
                         -hx, -hy, -hx, hy, 0, H)

    # East wall — window
    win_pos_e = random.uniform(0.3, r0["house_D"] - 0.3 - win_w)
    objs += wall_segment(f"{name}_wall_E",
                         hx, -hy, hx, hy, 0, H,
                         win_pos_e, win_pos_e + win_w, win_h + win_sill)
    if win_sill > 0.05:
        objs.append(make_box(
            f"{name}_wall_E_sill",
            hx, -hy + win_pos_e + win_w / 2,
            win_sill / 2,
            T, win_w, win_sill,
        ))

    # ── Interior dividers ──────────────────────────────────────

    # Vertical divider (living | kitchen+bedroom) with door
    door_pos_v = random.uniform(hallway_d + 0.2,
                                r0["house_D"] - hallway_d - door_w - 0.2)
    objs += wall_segment(f"{name}_div_vert",
                         div_x, -hy, div_x, hy, 0, H,
                         door_pos_v, door_pos_v + door_w, door_h)

    # Horizontal divider (kitchen | bedroom) with door
    right_w = hx - div_x - (bath_w if bath_w > 0 else 0)
    door_pos_h = random.uniform(0.2, max(right_w - door_w - 0.2, 0.3))
    objs += wall_segment(f"{name}_div_horiz",
                         div_x, div_y, hx, div_y, 0, H,
                         door_pos_h, door_pos_h + door_w, door_h)

    # Hallway divider
    if hallway_d > 0.05:
        objs += wall_segment(f"{name}_div_hallway",
                             -hx, int_y_min, hx, int_y_min, 0, H,
                             fd_pos - door_w / 2, fd_pos + door_w / 2, door_h)

    # Bathroom walls
    if bath_w > 0 and bath_d > 0:
        bath_x0 = hx - bath_w
        bath_y0 = hy - bath_d
        # Bathroom south wall (with door)
        objs += wall_segment(f"{name}_bath_S",
                             bath_x0, bath_y0, hx, bath_y0, 0, H,
                             0.1, 0.1 + door_w, door_h)
        # Bathroom west wall
        objs += wall_segment(f"{name}_bath_W",
                             bath_x0, bath_y0, bath_x0, hy, 0, H)

    # ── Floor and ceiling ──────────────────────────────────────
    W = r0["house_W"]
    D = r0["house_D"]
    objs.append(make_box(f"{name}_floor",   0, 0, -FT / 2, W, D, FT))
    objs.append(make_box(f"{name}_ceiling", 0, 0, H,       W, D, FT))

    return objs


def generate_collision_walls(
    name: str,
    rooms: list[RoomDict],
    wall_height: float,
    config: Config,
) -> list[bpy.types.Object]:
    """Build low-poly collision walls (same geometry, no subdivision).

    For now delegates to generate_walls — walls are already low-poly.
    Kept as a separate entry point so the exporter can tag them
    differently, mirroring TunnelGen's collision module pattern.
    """
    return generate_walls(name + "_col", rooms, wall_height, config)
