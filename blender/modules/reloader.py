"""Dependency-ordered module reloading for live iteration inside Blender.

Mirrors TunnelGen's reloader.py, adapted for HouseGen's module graph.
"""

import importlib
import sys
import types

RELOAD_ORDER: list[str] = [
    # Foundations — no dependencies on other HouseGen modules
    "modules.types",
    "modules.config_util",
    "modules.rng",
    "modules.scene_utils",
    # Geometry
    "modules.geometry",
    "modules.layout",       # room layout / floor plan
    "modules.walls",        # exterior + interior walls, doors, windows
    "modules.furniture",    # room-specific furniture placement
    "modules.lights",       # ceiling / wall lights
    "modules.materials",    # procedural shaders
    "modules.house",        # master orchestrator
    # Exporter
    "modules.exporter.xml_helpers",
    "modules.exporter.mesh",
    "modules.exporter.sdf",
    "modules.exporter",
    # Scenes — after everything they configure
    "scenes.base",
    "scenes",
]

_OPTIONAL: frozenset[str] = frozenset({
    "modules.materials",    # can run without procedural shaders
})

_PROJECT_PACKAGES = ("modules", "scenes")


def reload_all(extra: list[str] | None = None) -> None:
    """Import-or-reload every project module in dependency order."""
    for dotted in RELOAD_ORDER + list(extra or []):
        try:
            module = importlib.import_module(dotted)
        except ModuleNotFoundError:
            if dotted in _OPTIONAL:
                continue
            raise
        importlib.reload(module)
    _warn_unlisted(extra or [])


def _warn_unlisted(extra: list[str]) -> None:
    known = set(RELOAD_ORDER) | set(extra) | {__name__}
    unlisted = []
    for name, module in list(sys.modules.items()):
        if name in known or not isinstance(module, types.ModuleType):
            continue
        top = name.split(".", 1)[0]
        if top not in _PROJECT_PACKAGES:
            continue
        if not getattr(module, "__file__", None):
            continue
        unlisted.append(name)
    if unlisted:
        print(f"[reloader] WARNING: not in RELOAD_ORDER, will not hot-reload: "
              f"{', '.join(sorted(unlisted))}")
