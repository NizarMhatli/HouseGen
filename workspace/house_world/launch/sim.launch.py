"""Launch file for HouseGen simulation.

Usage:
    ros2 launch house_world sim.launch.py
    ros2 launch house_world sim.launch.py world:=family_house_42731_sim
    ros2 launch house_world sim.launch.py world:=house_sim rviz:=false

Arguments
---------
world : str
    World name (without .sdf). Must exist in the worlds/ directory.
    Default: house_sim (the last generated world).
rviz : bool
    Launch RViz2 alongside Gazebo. Default: true.
headless : bool
    Run Gazebo without GUI. Default: false.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg = get_package_share_directory('house_world')
    worlds_dir = os.path.join(pkg, 'worlds')

    # ── Launch arguments ───────────────────────────────────────
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='house_sim',
        description='World name (without .sdf extension)',
    )
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz2',
    )
    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='false',
        description='Run Gazebo headless (no GUI)',
    )

    world = LaunchConfiguration('world')
    use_rviz = LaunchConfiguration('rviz')
    headless = LaunchConfiguration('headless')

    # ── Resolve world file path ────────────────────────────────
    # Try package worlds dir first, then direct path
    world_file = PathJoinSubstitution([
        FindPackageShare('house_world'), 'worlds', [world, '.sdf']
    ])

    # ── Gazebo Harmonic ────────────────────────────────────────
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py'
            )
        ]),
        launch_arguments={
            'gz_args': ['-r ', world_file],
        }.items(),
    )

    # ── RViz2 ──────────────────────────────────────────────────
    rviz_config = os.path.join(pkg, 'rviz', 'house.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        condition=IfCondition(use_rviz),
        output='screen',
    )

    return LaunchDescription([
        world_arg,
        rviz_arg,
        headless_arg,
        gz_sim,
        rviz_node,
    ])
