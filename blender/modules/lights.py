"""Ceiling light generation for HouseGen."""

import bpy
import mathutils
from modules.types import Config, RoomDict, LampDict


def generate_lights(
    name: str,
    rooms: list[RoomDict],
    wall_height: float,
    config: Config,
) -> list[LampDict]:
    """Place one ceiling light per room."""
    intensity  = config.get("intensity", 800.0)
    color      = config.get("color", [1.0, 0.95, 0.85, 1.0])
    att_range  = config.get("attenuation_range", 8.0)

    lamps: list[LampDict] = []

    for room in rooms:
        cx = room["cx"]
        cy = room["cy"]
        cz = wall_height - 0.05

        # Blender light object
        light_data = bpy.data.lights.new(
            name=f"{name}_{room['name']}_light", type='POINT')
        light_data.energy = intensity
        light_data.color = color[:3]
        light_obj = bpy.data.objects.new(
            f"{name}_{room['name']}_light", light_data)
        light_obj.location = (cx, cy, cz)
        bpy.context.collection.objects.link(light_obj)

        # Visible fixture (small cylinder proxy)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.08, depth=0.06,
            location=(cx, cy, cz + 0.03)
        )
        mesh_obj = bpy.context.object
        mesh_obj.name = f"{name}_{room['name']}_fixture"

        lamps.append({
            "light_obj": light_obj,
            "mesh_obj":  mesh_obj,
            "world_pos": mathutils.Vector((cx, cy, cz)),
            "sdf": {
                "type":         "point",
                "diffuse":      color,
                "specular":     [0.2, 0.2, 0.2, 1.0],
                "cast_shadows": True,
                "attenuation": {
                    "range":    att_range,
                    "constant": 0.5,
                    "linear":   0.1,
                    "quadratic": 0.01,
                },
            },
        })

    return lamps
