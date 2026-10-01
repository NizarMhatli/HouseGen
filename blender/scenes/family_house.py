"""Family house scene — large multi-room house, dense furniture.

Change SEED to get a different layout while keeping the same
room configuration and furniture density.
"""

import random
from scenes.base import scene_spec

SEED = random.randint(0, 99999)

SPEC = scene_spec(
    name="FamilyHouse",
    seed=SEED,
    overrides={
        "layout": {
            "house_width_range": [13.0, 16.0],
            "house_depth_range": [10.0, 14.0],
            "hallway":  True,
            "bathroom": True,
        },
        "furniture": {
            "density": 1.2,
        },
        "export": {
            "enabled":    True,
            "model_name": f"family_house_{SEED}",
            "world_name": f"family_house_{SEED}",
        },
    },
)
