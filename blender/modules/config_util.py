"""Config dict helpers shared by scenes and the showcase renderer.

The generator is configured by one deeply nested plain dict. Both the scene
presets in :mod:`scenes` and the per-shot overrides in ``showcase.py`` build
theirs by layering a small override dict over a shared base, so the merge lives
here rather than being reimplemented on each side.

Deliberately free of any ``bpy`` import so it can be used from tooling that
runs outside Blender.
"""

import copy

from modules.types import Config


def deep_merge(base: Config, overrides: Config) -> Config:
    """Deep-merge ``overrides`` into a deep copy of ``base``.

    Nested dicts are merged recursively. Any non-dict value in ``overrides``
    replaces whatever sat at the same key in ``base``. ``base`` is never
    mutated, and every value taken from either side is deep-copied, so two
    scenes derived from the same base can never alias each other's sub-dicts.

    **Lists are replaced wholesale, not concatenated or merged element-wise.**
    That matters for the list-valued config keys — ``small_tubes``,
    ``wall_cables``, ``obstacles.patterns``, ``obstacles.scripted`` — where an
    override always fully supersedes the base. It is the long-standing
    behaviour of the showcase renderer and the intuitive reading of "this
    scene has these patterns", so it is preserved rather than fixed.

    Parameters
    ----------
    base : dict
        Defaults dict; copied before merging.
    overrides : dict
        Overrides to layer on top. Keys may be nested dicts.

    Returns
    -------
    dict
        Fresh dict with the merged values.
    """
    result = copy.deepcopy(base)
    for key, val in overrides.items():
        if isinstance(val, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result
