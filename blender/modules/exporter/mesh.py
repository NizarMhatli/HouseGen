"""Mesh export helpers — adapted from TunnelGen's exporter/mesh.py."""

import bpy


def _select_only(objs: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


def _export_mesh(objs: list[bpy.types.Object], filepath: str) -> None:
    """Export objects to OBJ file."""
    _select_only(objs)
    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=True,
        apply_modifiers=True,
        export_triangulated_mesh=True,
        export_normals=True,
        export_uv=True,
        export_materials=False,
        forward_axis='Y',
        up_axis='Z',
    )


def _extract_base_color(obj: bpy.types.Object) -> tuple[float, float, float]:
    """Read representative base colour from object's first material."""
    if obj.data is None or not obj.data.materials:
        return (0.5, 0.5, 0.5)
    mat = obj.data.materials[0]
    if not mat or not mat.use_nodes:
        return (0.5, 0.5, 0.5)
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bc = node.inputs.get("Base Color")
            if bc and not bc.is_linked:
                c = bc.default_value
                return (c[0], c[1], c[2])
    return (0.5, 0.5, 0.5)
