"""Generate a new house world and launch it immediately.

This launch file runs the HouseGen Blender pipeline headlessly,
then launches Gazebo with the newly generated world.

Usage:
    ros2 launch house_world generate.launch.py
    ros2 launch house_world generate.launch.py scene:=small_apartment
    ros2 launch house_world generate.launch.py scene:=family_house rviz:=false

Arguments
---------
scene : str
    HouseGen scene name. Default: family_house.
rviz : bool
    Launch RViz2. Default: true.
blender : str
    Path to Blender launcher binary.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    RegisterEventHandler,
    IncludeLaunchDescription,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg      = get_package_share_directory('house_world')
    pkg_src  = os.path.join(os.path.dirname(pkg), '..', '..', '..', 'src', 'house_world')
    blender_main = os.path.expanduser('~/HouseGen/main.py')

    scene_arg = DeclareLaunchArgument(
        'scene', default_value='family_house',
        description='HouseGen scene to generate',
    )
    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Launch RViz2 after simulation starts',
    )
    blender_arg = DeclareLaunchArgument(
        'blender',
        default_value='/snap/bin/blender',
        description='Path to Blender launcher binary',
    )

    scene   = LaunchConfiguration('scene')
    blender = LaunchConfiguration('blender')

    worlds_out = os.path.join(pkg, 'worlds')

    # ── Step 1: Run HouseGen ───────────────────────────────────
    generate = ExecuteProcess(
        cmd=[
            blender,
            '--background', '--factory-startup',
            '--python', blender_main,
            '--', scene,
        ],
        additional_env={
            'HOUSEGEN_ALLOW_ABS': '1',
            'HOUSEGEN_OUTPUT_DIR': worlds_out,
        },
        output='screen',
        name='housegen_blender',
    )

    # ── Step 2: Launch sim after generation completes ──────────
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'sim.launch.py')
        ),
        launch_arguments={'rviz': LaunchConfiguration('rviz')}.items(),
    )

    launch_sim_on_gen_exit = RegisterEventHandler(
        OnProcessExit(
            target_action=generate,
            on_exit=[sim_launch],
        )
    )

    return LaunchDescription([
        scene_arg,
        rviz_arg,
        blender_arg,
        generate,
        launch_sim_on_gen_exit,
    ])
