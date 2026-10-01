"""BASE feature tree for HouseGen — mirrors TunnelGen's scenes/base.py.

Every scene preset deep-merges a small override dict on top of this.
"""

from modules.types import HouseSpec, Config
from modules.config_util import deep_merge

BASE: Config = {

    "wall_height": 2.8,   # interior ceiling height (m)

    "layout": {
        "house_width_range": [10.0, 16.0],
        "house_depth_range": [8.0,  14.0],
        "hallway":   True,
        "bathroom":  True,
    },

    "walls": {
        "door_width":    0.9,
        "door_height":   2.1,
        "window_width":  1.2,
        "window_height": 1.2,
        "window_sill":   0.9,
    },

    "furniture": {
        "density": 1.0,   # 0=sparse, 1=normal, 2=dense
    },

    "lights": {
        "intensity":         800.0,
        "color":             [1.0, 0.95, 0.85, 1.0],
        "attenuation_range": 8.0,
    },

    "materials": {
        "wall_color":    [0.92, 0.91, 0.88],
        "floor_color":   [0.60, 0.50, 0.38],
        "ceiling_color": [0.98, 0.98, 0.97],
    },

    "export": {
        "enabled":    True,
        "output_dir": "export",
        "model_name": "house",
        "world_name": "house_sim",
    },
}


def scene_spec(name: str, seed: int | None, overrides: Config) -> HouseSpec:
    """Build a HouseSpec by merging overrides over BASE.

    Parameters
    ----------
    name : str
        Scene name / object prefix.
    seed : int or None
        Master seed. None = different every run.
    overrides : dict
        Small dict layered over BASE.

    Returns
    -------
    HouseSpec
    """
    features = deep_merge(BASE, overrides)
    return HouseSpec(name=name, seed=seed, features=features)
