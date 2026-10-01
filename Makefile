.PHONY: build up down shell rebuild logs ros-build ros-build-pkg clean world rviz

# ── Docker lifecycle ───────────────────────────────────────────────────────

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

shell:
	docker compose exec housegen bash

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d

logs:
	docker compose logs -f housegen

# ── ROS 2 build ───────────────────────────────────────────────────────────

ros-build:
	docker compose exec housegen bash -c \
	  "source /opt/ros/jazzy/setup.bash && \
	   cd /ros2_ws && colcon build --symlink-install && \
	   source install/setup.bash"

ros-build-pkg:
	docker compose exec housegen bash -c \
	  "source /opt/ros/jazzy/setup.bash && \
	   cd /ros2_ws && colcon build --symlink-install --packages-select $(PKG) && \
	   source install/setup.bash"

# ── World generation ──────────────────────────────────────────────────────
# Usage:
#   make world                        # uses default scene (family_house)
#   make world SCENE=small_apartment  # specific scene
#   make world SEED=42731             # reproduce a house (set seed in scene file first)

SCENE ?= family_house
BLENDER ?= /snap/bin/blender

world:
	@echo "[HouseGen] Generating scene: $(SCENE)"
	HOUSEGEN_ALLOW_ABS=1 \
	HOUSEGEN_OUTPUT_DIR=$(PWD)/workspace/house_world/worlds \
	HOUSEGEN_SCENE=$(SCENE) \
	$(BLENDER) --background --factory-startup --python blender/main.py -- $(SCENE)
	@echo "[HouseGen] Done — rebuild ROS package to pick up new world"
	$(MAKE) ros-build-pkg PKG=house_world

# Run world generation inside Docker container
world-docker:
	docker compose exec housegen bash -c \
	  "HOUSEGEN_ALLOW_ABS=1 \
	   HOUSEGEN_OUTPUT_DIR=$(PWD)/workspace/house_world/worlds \
	   HOUSEGEN_SCENE=$(SCENE) \
	   $(BLENDER) --background --factory-startup \
	   --python /ros2_ws/src/house_world/../../../blender/main.py -- $(SCENE) && \
	   cd /ros2_ws && colcon build --symlink-install --packages-select house_world"

# ── Simulation launch ─────────────────────────────────────────────────────
# Usage:
#   make sim                                     # latest generated world
#   make sim WORLD=family_house_42731_sim        # specific world

WORLD ?= house_sim

sim:
	docker compose exec housegen bash -c \
	  "source /opt/ros/jazzy/setup.bash && \
	   source /ros2_ws/install/setup.bash && \
	   ros2 launch house_world sim.launch.py world:=$(WORLD)"

rviz:
	docker compose exec housegen bash -c \
	  "source /opt/ros/jazzy/setup.bash && \
	   source /ros2_ws/install/setup.bash && \
	   rviz2 -d /ros2_ws/src/house_world/rviz/house.rviz"

# ── Utility ───────────────────────────────────────────────────────────────

clean:
	rm -rf build/ install/ log/

list-worlds:
	@echo "Generated worlds:"
	@ls workspace/house_world/worlds/*.sdf 2>/dev/null | xargs -I{} basename {} .sdf || \
	  echo "  (none yet — run 'make world' first)"
