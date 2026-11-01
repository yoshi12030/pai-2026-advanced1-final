# AI Robot Teleoperation

ROS 2とIgnition Gazeboを使って、自然言語風のテキスト指示で差動二輪ロボットを操作するサンプルです。外部のAIサービスは使用せず、入力されたキーワードをローカルで判定して`/cmd_vel`に速度指令を送ります。

## 必要な環境

- Ubuntu 22.04
- ROS 2 Humble
- `ros_ign_gazebo`および`ros_ign_bridge`

Humbleの環境では、依存パッケージをインストールします。

```bash
sudo apt update
sudo apt install ros-humble-ros-ign-gazebo ros-humble-ros-ign-bridge
```

## ビルド

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## 実行

ターミナル1でシミュレータとROS-Gazeboブリッジを起動します。

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
source install/setup.bash
ros2 launch ai_robot_teleop robot_sim.launch.py
```

ターミナル2で操作ノードを起動します。

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
source install/setup.bash
ros2 run ai_robot_teleop gemini_teleop_node
```

## 操作方法

ノードのプロンプトに指示を入力します。数字のショートカットのほか、日本語やローマ字、英語のキーワードを利用できます。

| 入力例 | 動作 |
| --- | --- |
| `1`、`mae`、`前`、`forward` | 前進 |
| `2`、`migi`、`右`、`right` | 右旋回 |
| `3`、`hidari`、`左`、`left` | 左旋回 |
| `4`、`ushiro`、`後ろ`、`back` | 後退 |
| `5`、`stop`、`停止` | 停止 |
| `sukoshi`、`ゆっくり`、`slow` | 低速で動作 |
| `hayaku`、`速く`、`fast` | 高速で動作 |
| `q`、`exit` | ノードを終了 |

動作指令は一定時間後にゼロ速度を送って停止します。認識されない入力は前進として扱われるため、シミュレータ内で試し、入力内容を確認してから実行してください。このサンプルを安全機能のない実機で使用しないでください。

## パッケージ構成

```text
ros2_ws/src/ai_robot_teleop/
	ai_robot_teleop/  # 自然言語風入力を判定する操作ノード
	config/           # ROS-Gazeboブリッジ設定
	launch/           # シミュレータ起動設定
	worlds/           # 差動二輪ロボットのGazeboワールド
```
