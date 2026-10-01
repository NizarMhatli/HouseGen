"""HouseGen runner — generate one house scene and export it for Gazebo.

Mirrors TunnelGen's main.py exactly.

Run inside Blender (VS Code "Blender Development" → Blender: Run Script), or
headless::

    /opt/blender-5.1/blender-launcher --background --python main.py -- family_house

Scene selection precedence:
  1. First argument after ``--``
  2. ``$HOUSEGEN_SCENE``
  3. DEFAULT_SCENE
"""

import os
import sys

import bpy

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
if hasattr(bpy.context.space_data, "text") and bpy.context.space_data.text:
    dir_path = os.path.dirname(bpy.context.space_data.text.filepath)
else:
    dir_path = os.path.dirname(os.path.abspath(__file__))

if dir_path not in sys.path:
    sys.path.append(dir_path)

import importlib
import modules.reloader
importlib.reload(modules.reloader)

# ---------------------------------------------------------------------------
# Scene selection
# ---------------------------------------------------------------------------
#: Change this for interactive Blender: Run Script sessions.
DEFAULT_SCENE = "family_house"


def _pick_scene() -> str:
    if "--" in sys.argv:
        rest = sys.argv[sys.argv.index("--") + 1:]
        if rest:
            return rest[0]
    return os.environ.get("HOUSEGEN_SCENE", DEFAULT_SCENE)


def _resolve_output_dir(features: dict) -> str | None:
    """Resolve export directory, refusing unsafe absolute paths."""
    raw = (
        os.environ.get("HOUSEGEN_OUTPUT_DIR")
        or features.get("export", {}).get("output_dir", "export")
    )
    expanded = os.path.expanduser(raw)

    if not os.path.isabs(expanded):
        return os.path.join(dir_path, expanded)

    if os.environ.get("HOUSEGEN_ALLOW_ABS") == "1":
        return expanded

    print(
        f"[export] REFUSED absolute output_dir {expanded!r}.\n"
        f"[export] To deploy to ROS workspace, re-run with:\n"
        f"[export]   HOUSEGEN_ALLOW_ABS=1 HOUSEGEN_OUTPUT_DIR={expanded} ..."
    )
    return None


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------
scene_name = _pick_scene()
modules.reloader.reload_all(extra=[f"scenes.{scene_name}"])

import modules.exporter
import modules.scene_utils
import modules.house
import scenes

spec = scenes.load(scene_name)
print(f"[main] scene={scene_name}  seed={spec.seed}  name={spec.name}")

modules.scene_utils.clear_scene()

scene = modules.house.generate_scene(spec)
print(scene.summary())

if spec.features.get("export", {}).get("enabled", False):
    out_dir = _resolve_output_dir(spec.features)
    if out_dir:
        modules.exporter.export_gazebo(scene, output_dir=out_dir)
