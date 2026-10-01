"""Scene loader — mirrors TunnelGen's scenes/__init__.py."""

from modules.types import HouseSpec


def load(name: str) -> HouseSpec:
    """Import scenes/<name>.py and return its SPEC."""
    import importlib
    try:
        mod = importlib.import_module(f"scenes.{name}")
    except ModuleNotFoundError:
        available = ["family_house", "small_apartment", "random_house"]
        raise ValueError(
            f"Unknown scene {name!r}. Available: {available}"
        )
    return mod.SPEC
