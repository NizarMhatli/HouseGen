"""Random floor plan layout for HouseGen.

Generates a rectilinear room layout from a HouseSpec config.
Rooms are defined by their bounding box and type (living, kitchen, bedroom,
bathroom, hallway). The layout is fully deterministic given a seed.

Layout strategy
---------------
1. Choose total house footprint (W x D) from config ranges.
2. Place a vertical divider splitting house into left wing / right wing.
3. Place a horizontal divider in the right wing splitting kitchen / bedroom.
4. Optionally add a hallway strip and bathroom.

All coordinates are in metres, origin at house center bottom.
"""

import random
import math
from modules.types import Config, RoomDict


def generate_layout(config: Config) -> list[RoomDict]:
    """Generate a random room layout.

    Parameters
    ----------
    config : dict
        The ``layout`` sub-dict from features. Keys:
        - ``house_width_range`` : [min, max] total width (X)
        - ``house_depth_range`` : [min, max] total depth (Y)
        - ``room_types``        : list of room type names to include
        - ``hallway``           : bool, add hallway strip
        - ``bathroom``          : bool, add bathroom

    Returns
    -------
    list of dict
        Room records, each with:
        - ``name``   : str
        - ``type``   : str  (living, kitchen, bedroom, bathroom, hallway)
        - ``x_min``, ``x_max``, ``y_min``, ``y_max`` : float bounds
        - ``cx``, ``cy`` : float center
        - ``width``, ``depth`` : float dimensions
    """
    w_range = config.get("house_width_range", [10.0, 16.0])
    d_range = config.get("house_depth_range", [8.0, 14.0])
    has_hallway = config.get("hallway", True)
    has_bathroom = config.get("bathroom", True)

    W = random.uniform(*w_range)
    D = random.uniform(*d_range)

    hx = W / 2
    hy = D / 2

    rooms = []

    # ── Hallway strip along south wall ─────────────────────────
    hallway_d = random.uniform(1.2, 1.8) if has_hallway else 0.0

    # Effective interior after hallway
    int_y_min = -hy + hallway_d
    int_y_max = hy

    # ── Vertical divider: living | right wing ──────────────────
    split_x = random.uniform(W * 0.38, W * 0.55)
    div_x = -hx + split_x

    # ── Horizontal divider in right wing: kitchen | bedroom ────
    split_y = random.uniform(D * 0.38, D * 0.55)
    div_y = -hy + split_y

    # ── Bathroom in bedroom corner ──────────────────────────────
    bath_w = random.uniform(1.8, 2.4) if has_bathroom else 0.0
    bath_d = random.uniform(1.6, 2.2) if has_bathroom else 0.0

    # ══ Room definitions ═══════════════════════════════════════

    # Living room (left wing, full height minus hallway)
    rooms.append(_room(
        "living_room", "living",
        -hx, div_x, int_y_min, int_y_max,
    ))

    # Kitchen (right-bottom)
    rooms.append(_room(
        "kitchen", "kitchen",
        div_x, hx, int_y_min, div_y,
    ))

    # Bedroom (right-top, minus bathroom corner)
    if has_bathroom:
        # Main bedroom area
        rooms.append(_room(
            "bedroom", "bedroom",
            div_x, hx - bath_w, div_y, int_y_max,
        ))
        # Bathroom
        rooms.append(_room(
            "bathroom", "bathroom",
            hx - bath_w, hx, int_y_max - bath_d, int_y_max,
        ))
        # Bedroom extension next to bathroom
        if int_y_max - bath_d - div_y > 0.5:
            rooms.append(_room(
                "bedroom_ext", "bedroom",
                hx - bath_w, hx, div_y, int_y_max - bath_d,
            ))
    else:
        rooms.append(_room(
            "bedroom", "bedroom",
            div_x, hx, div_y, int_y_max,
        ))

    # Hallway
    if has_hallway:
        rooms.append(_room(
            "hallway", "hallway",
            -hx, hx, -hy, int_y_min,
        ))

    # Store house dimensions on first room for wall builder
    rooms[0]["house_W"] = W
    rooms[0]["house_D"] = D
    rooms[0]["house_hx"] = hx
    rooms[0]["house_hy"] = hy
    rooms[0]["div_x"] = div_x
    rooms[0]["div_y"] = div_y
    rooms[0]["hallway_d"] = hallway_d
    rooms[0]["bath_w"] = bath_w
    rooms[0]["bath_d"] = bath_d

    return rooms


def _room(
    name: str, rtype: str,
    x_min: float, x_max: float,
    y_min: float, y_max: float,
) -> RoomDict:
    """Build a room dict from bounds."""
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    return {
        "name": name,
        "type": rtype,
        "x_min": x_min, "x_max": x_max,
        "y_min": y_min, "y_max": y_max,
        "cx": cx, "cy": cy,
        "width": x_max - x_min,
        "depth": y_max - y_min,
    }
