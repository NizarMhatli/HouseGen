"""Small apartment scene — compact layout, no hallway.

Good for testing in tight spaces with minimal open area.
"""

import random
from scenes.base import scene_spec

SEED = random.randint(0, 99999)

SPEC = scene_spec(
    name="SmallApartment",
    seed=SEED,
    overrides={
        "layout": {
            "house_width_range": [7.0, 10.0],
            "house_depth_range": [6.0, 9.0],
            "hallway":  False,
            "bathroom": True,
        },
        "wall_height": 2.5,
        "furniture": {
            "density": 0.8,
        },
        "export": {
            "enabled":    True,
            "model_name": f"small_apartment_{SEED}",
            "world_name": f"small_apartment_{SEED}",
        },
    },
)
