"""Low-level XML helpers shared by every SDF writer in this package.

These are intentionally tiny and have no dependencies beyond the standard
library so that any other sub-module (``sdf``, ``obstacle_assets``) can
import them without dragging in Blender.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

import mathutils


def _pretty_xml(elem: ET.Element) -> str:
    """Return a pretty-printed XML string for an ElementTree element.

    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        Root of the subtree to serialise.

    Returns
    -------
    str
        Multi-line XML string with two-space indentation, ready to be
        written to disk.
    """
    raw = ET.tostring(elem, encoding="unicode")
    dom = minidom.parseString(raw)
    return dom.toprettyxml(indent="  ", encoding=None)


def _sub(parent: ET.Element, tag: str, text: str | None = None, **attribs: str) -> ET.Element:
    """Create a sub-element under ``parent``, optionally setting text and attrs.

    Shorthand around :func:`xml.etree.ElementTree.SubElement` used
    everywhere in the SDF writers to keep the call sites short.

    Parameters
    ----------
    parent : xml.etree.ElementTree.Element
        Parent element the new child is attached to.
    tag : str
        XML tag name of the new element.
    text : str or None, optional
        If not ``None``, assigned to the element's ``text`` attribute
        (stringified via ``str``).
    **attribs
        Keyword attributes passed straight to ``SubElement``.

    Returns
    -------
    xml.etree.ElementTree.Element
        The newly created element.
    """
    el = ET.SubElement(parent, tag, **attribs)
    if text is not None:
        el.text = str(text)
    return el


def _pose_str(
    x: float,
    y: float,
    z: float,
    roll: float = 0,
    pitch: float = 0,
    yaw: float = 0,
) -> str:
    """Format a 6-DOF pose as the space-separated string SDF expects.

    Parameters
    ----------
    x, y, z : float
        Position in metres.
    roll, pitch, yaw : float, optional
        Orientation in radians. Default ``0`` for each.

    Returns
    -------
    str
        Six space-separated floats with six decimal places.
    """
    return f"{x:.6f} {y:.6f} {z:.6f} {roll:.6f} {pitch:.6f} {yaw:.6f}"


def _quat_to_rpy(quat: mathutils.Quaternion) -> tuple[float, float, float]:
    """Convert a Blender quaternion to ``(roll, pitch, yaw)`` Euler angles.

    Parameters
    ----------
    quat : mathutils.Quaternion
        Blender-native quaternion.

    Returns
    -------
    tuple of float
        ``(roll, pitch, yaw)`` in radians, extracted with the ``XYZ``
        Euler convention.
    """
    euler = quat.to_euler('XYZ')
    return euler.x, euler.y, euler.z


DEFAULT_WORLD_NAME = "tunnel_sim"


def world_name_from_config(config: dict) -> str:
    """Return the Gazebo ``<world name=...>`` for this export.

    Single source of truth for two writers that must agree: the ``<world>``
    element in :func:`modules.exporter.sdf._write_world_sdf` and the
    ``"world_name"`` key in :func:`modules.exporter._write_nav_meta`. The ROS
    path follower builds ``/world/<name>/set_pose`` from the metadata value, so
    if the two ever diverge the wheel loader silently never moves.

    Parameters
    ----------
    config : dict
        The full features config. Reads ``export.world_name``.

    Returns
    -------
    str
        The configured world name, or ``"tunnel_sim"`` when unset.
    """
    return (config or {}).get("export", {}).get("world_name", DEFAULT_WORLD_NAME)
