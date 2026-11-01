#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class LocalAITeleopNode(Node):
    def __init__(self):
        super().__init__('gemini_teleop_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("=== 自律NLU推論ノード（90度ターン調整版）準備完了 ===")

    def nlu_inference(self, text: str):
        t = text.lower().strip()
        lin_x = 0.0
        ang_z = 0.0
        dur = 1.5
        intent = "UNKNOWN"
        modifier = "NORMAL"
        confidence = 0.98
        reason = ""

        # 速度・継続時間
        speed_scale = 1.0
        if any(w in t for w in ["sukoshi", "yukkuri", "slow", "little", "bit", "chotto", "少し", "ゆっくり"]):
            speed_scale = 0.5
            dur = 1.0
            modifier = "SLOW / SHORT"
            reason += "低速指示 "
        elif any(w in t for w in ["hayaku", "fast", "quick", "speed", "急いで", "速く"]):
            speed_scale = 1.5
            modifier = "FAST"
            reason += "高速指示 "

        # 1. 停止
        if any(w in t for w in ["toma", "stop", "brake", "halt", "止まれ", "停止", "5"]):
            lin_x = 0.0
            ang_z = 0.0
            dur = 0.0
            intent = "STOP"
            reason = "➔ 即時停止"

        # 2. 右旋回（約90度でピタッと止まる設定）
        elif any(w in t for w in ["migi", "right", "右", "2"]):
            lin_x = 0.15              # わずかに前進を混ぜてスムーズに
            ang_z = -1.4              # 角速度
            dur = 1.1 * speed_scale   # 約1.5ラジアン（約86〜90度）
            intent = "TURN_RIGHT_90"
            reason += "➔ 右へ約90度旋回"

        # 3. 左旋回（約90度でピタッと止まる設定）
        elif any(w in t for w in ["hidari", "left", "左", "3"]):
            lin_x = 0.15
            ang_z = 1.4
            dur = 1.1 * speed_scale   # 約86〜90度
            intent = "TURN_LEFT_90"
            reason += "➔ 左へ約90度旋回"

        # 4. 後退
        elif any(w in t for w in ["ushiro", "back", "sagare", "backward", "後ろ", "下がれ", "4"]):
            lin_x = -0.4 * speed_scale
            ang_z = 0.0
            dur = 1.5
            intent = "BACKWARD"
            reason += "➔ 後退動作"

        # 5. 直進前進
        elif any(w in t for w in ["mae", "forward", "susume", "go", "front", "前", "進め", "1"]):
            lin_x = 0.5 * speed_scale
            ang_z = 0.0
            dur = 1.5
            intent = "FORWARD"
            reason += "➔ 直進前進"

        else:
            lin_x = 0.3
            ang_z = 0.0
            dur = 1.2
            intent = "DEFAULT_FORWARD"
            confidence = 0.70
            reason = "➔ 汎用前進"

        return {
            "intent": intent,
            "modifier": modifier,
            "confidence": confidence,
            "linear_x": lin_x,
            "angular_z": ang_z,
            "duration": dur,
            "reason": reason
        }

    def execute_command(self, user_instruction: str):
        t0 = time.time()
        plan = self.nlu_inference(user_instruction)
        calc_time = (time.time() - t0) * 1000

        lin_x = plan["linear_x"]
        ang_z = plan["angular_z"]
        dur = plan["duration"]

        print(f"\n[エッジAI推論完了 (処理時間: {calc_time:.3f} ms)]")
        print(f"・解析意図 : {plan['intent']} | 修飾: {plan['modifier']} (信頼度: {plan['confidence']*100:.1f}%)")
        print(f"・判断根拠 : {plan['reason']}")
        print(f"・送信指令 : 前後速度={lin_x:.2f} m/s, 旋回速度={ang_z:.2f} rad/s (継続 {dur} 秒)")

        twist = Twist()
        twist.linear.x = float(lin_x)
        twist.angular.z = float(ang_z)
        self.publisher_.publish(twist)

        if dur > 0:
            time.sleep(dur)
            self.publisher_.publish(Twist())
            print("-> 動作完了（自動停止しました）\n")

def main(args=None):
    rclpy.init(args=args)
    node = LocalAITeleopNode()

    print("\n=======================================================")
    print("  エッジ自律NLU 自然言語ロボット操作システム（90度ターン版）")
    print("  【ショートカット】 1: 前進 / 2: 右90度 / 3: 左90度 / 4: 後退 / 5: 停止")
    print("  【テキスト入力】 'migi', 'mae ni susunde', 'sukoshi hidari' など")
    print("  終了: 'q' または 'exit'")
    print("=======================================================\n")

    try:
        while rclpy.ok():
            cmd = input("指示を入力 > ").strip()
            if cmd.lower() in ['q', 'exit']:
                break
            if cmd:
                node.execute_command(cmd)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
