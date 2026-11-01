import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('ai_robot_teleop')
    world_path = os.path.join(pkg_dir, 'worlds', 'diff_drive_world.sdf')
    bridge_config = os.path.join(pkg_dir, 'config', 'bridge.yaml')

    # Gazeboシミュレータの起動
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_ign_gazebo'), 'launch', 'ign_gazebo.launch.py')
        ),
        launch_arguments={'ign_args': f'-r -v 3 {world_path}'}.items()
    )

    # ROS 2 ⇆ Gazebo ブリッジノード
    bridge = Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_config,
            'use_sim_time': True
        }],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        bridge
    ])
