"""Random house scene — everything randomised, different every run.

Use this for dataset generation. The seed is printed to console
so any interesting layout can be reproduced by hardcoding it here.
"""

import random
from scenes.base import scene_spec

# None = unseeded, different every run
# Set to an int to reproduce a specific house, e.g. SEED = 42731
SEED = None

SPEC = scene_spec(
    name="RandomHouse",
    seed=SEED,
    overrides={
        "export": {
            "enabled":    True,
            "model_name": "random_house",
            "world_name": "random_house_sim",
        },
    },
)
