"""Scene setup helpers — mirrors TunnelGen's scene_utils.py."""

import bpy


def clear_scene() -> None:
    """Delete all mesh objects and lights from the current scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.lights):
        bpy.data.lights.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
