"""Shared type aliases for the HouseGen pipeline.

Mirrors the structure of TunnelGen's types.py, adapted for house generation.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import bpy
import mathutils

# Generic config dict (deeply nested user-facing config).
Config = dict[str, Any]

# Room record: name, bounds, center, type.
RoomDict = dict[str, Any]

# Furniture record: obj, room, category.
FurnitureDict = dict[str, Any]

# Lamp record: mesh_obj, light_obj, world_pos, sdf.
LampDict = dict[str, Any]


@dataclass
class HouseScene:
    """Everything one generation run produced.

    Attributes
    ----------
    name : str
        Base name used for generated objects.
    seed : int or None
        Master seed used.
    rooms : list of dict
        Room records with bounds, center, type.
    groups : dict
        Export group name -> list of Blender objects.
    lamps : list of dict
        Lamp records.
    config : dict
        Merged feature config this scene was generated from.
    scene_name : str or None
        Which scenes/ preset produced this.
    """

    name: str
    seed: int | None = None
    rooms: list[RoomDict] = field(default_factory=list)
    groups: dict[str, list[bpy.types.Object]] = field(default_factory=dict)
    lamps: list[LampDict] = field(default_factory=list)
    config: Config = field(default_factory=dict)
    scene_name: str | None = None

    def add(self, group: str, objs) -> None:
        """Register objects under group."""
        if objs is None:
            return
        obj_list = objs if isinstance(objs, list) else [objs]
        obj_list = [o for o in obj_list if o is not None]
        if not obj_list:
            return
        bucket = self.groups.setdefault(group, [])
        bucket.extend(obj_list)

    def objects(self, group: str) -> list[bpy.types.Object]:
        return self.groups.get(group, [])

    def all_objects(self) -> list[bpy.types.Object]:
        return [obj for objs in self.groups.values() for obj in objs]

    def summary(self) -> str:
        n_rooms = len(self.rooms)
        n_walls = len(self.objects("walls"))
        n_furn = len(self.objects("furniture"))
        n_lamps = len(self.lamps)
        total = sum(len(v) for v in self.groups.values())
        return (
            f"[scene] {self.name}: {n_rooms} rooms, {n_walls} wall segments, "
            f"{n_furn} furniture pieces, {n_lamps} lamps, "
            f"groups={len(self.groups)} ({total} objects)"
        )


@dataclass
class HouseSpec:
    """Everything needed to generate one house.

    Attributes
    ----------
    name : str
        Base name for all generated objects.
    seed : int or None
        Master seed. None = unseeded (different each run).
    features : dict
        The feature config tree, merged over BASE.
    scene_name : str or None
        Set by scenes.load(); scene modules leave it alone.
    """

    name: str = "House"
    seed: int | None = None
    features: Config = field(default_factory=dict)
    scene_name: str | None = None
