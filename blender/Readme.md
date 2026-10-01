# HouseGen — Procedural House Environment Generator

A procedural generation pipeline built with Python and Blender for creating
realistic multi-room house environments. Designed for robotics simulation,
HouseGen generates fully configurable 3D house scenes and exports to Gazebo
(gz-sim) for use with ROS 2 Jazzy.

Built following the same architecture as **TunnelGen**.

## Architecture

```
main.py                          Thin runner: picks a scene, generates, exports
  |
  v
scenes/<name>.py                 Scene preset: dimensions, seed, feature overrides
  |                              (scenes/base.py holds BASE, the default feature tree)
  v
house.generate_scene(spec)       Orchestrator -> HouseScene
  |
  |-- layout.generate_layout()   Random floor plan (rooms, dividers, hallway, bathroom)
  |-- walls.generate_walls()     Exterior walls, interior dividers, doors, windows
  |-- furniture.generate_furniture()  Room-specific furniture from catalogue
  |-- lights.generate_lights()   Ceiling point lights per room
  |-- materials.apply_all()      Procedural Principled BSDF shaders
  |
  v
exporter.export_gazebo()         SDF + OBJ export for Gazebo (gz-sim)
  |
  |-- meshes/walls.obj           All wall/floor/ceiling geometry
  |-- meshes/furniture.obj       All furniture
  |-- meshes/fixtures.obj        Light fixture geometry
  |-- model.sdf + model.config   Static SDF model
  |-- worlds/<name>.sdf          World file with lights + spawn point
  +-- worlds/house_meta.json     Room centers + spawn pose (read by ROS)
```

## Room Layout

```
┌─────────────────────────────────┐
│                                 │
│         BEDROOM                 │  ┌──────┐
│                                 │  │ BATH │
│                                 │  └──────┘
├──────────────┬──────────────────┤
│              │                  │
│  LIVING      │    KITCHEN       │
│  ROOM        │                  │
│              │                  │
├──────────────┴──────────────────┤
│           HALLWAY               │  ← front door
└─────────────────────────────────┘
```

Layout dimensions and divider positions are randomised each run.

## Scenes

| Scene | Purpose |
|-------|---------|
| `family_house` | Large house (13–16m × 10–14m), dense furniture |
| `small_apartment` | Compact (7–10m × 6–9m), no hallway |
| `random_house` | Fully random every run — for dataset generation |

## Quick Start

### Interactive (VS Code + Blender)

1. Open `main.py` in VS Code, set `DEFAULT_SCENE`.
2. `Ctrl+Shift+P` → **Blender: Start** → **Blender 5.1**.
3. `Ctrl+Shift+P` → **Blender: Run Script**.

### Headless

```bash
BL=/opt/blender-5.1/blender-launcher

# Generate family_house and export to export/
$BL --background --factory-startup --python main.py -- family_house

# Generate and deploy directly to ROS workspace
HOUSEGEN_ALLOW_ABS=1 \
HOUSEGEN_OUTPUT_DIR=~/pr/Simple-mapping-jig-prototype/workspace/jig_description/worlds \
  $BL --background --factory-startup --python main.py -- family_house
```

### Reproducing a house

Every run prints the seed:
```
[main] scene=family_house  seed=42731  name=FamilyHouse
```

To regenerate the same house, set `SEED = 42731` in `scenes/family_house.py`.

## Deploying to Gazebo

After export, launch with:
```bash
# Inside jig Docker container
gz sim /ros2_ws/src/jig_description/worlds/family_house_42731/worlds/family_house_42731.sdf
```

Or update `gazebo.launch.py` to use the generated world:
```python
world_file = '/ros2_ws/src/jig_description/worlds/family_house_42731/worlds/family_house_42731.sdf'
```

## Configuration

All configuration is in `scenes/`. Edit `scenes/base.py` for global defaults.

Key parameters:

| Section | Controls |
|---------|---------|
| `layout` | House size, hallway, bathroom |
| `walls` | Door/window dimensions |
| `furniture` | Density (0=sparse, 1=normal, 2=dense) |
| `lights` | Intensity, color, attenuation |
| `materials` | Wall/floor/ceiling colors |
| `export` | Output dir, model name, world name |

## Prerequisites

- Blender 5.x
- VS Code + Blender Development extension
- `uv` for Python environment

## Setup

```bash
git clone <repo>
cd HouseGen
uv venv
uv pip install fake-bpy-module-latest
```
