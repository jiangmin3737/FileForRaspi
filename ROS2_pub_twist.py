import rclpy
import time
import random

# 1. WindowsでのDLL衝突を防ぐため、まず最優先で初期化する
rclpy.init()

# 2. 初期化後にメッセージ型をインポート
from geometry_msgs.msg import Twist

class CmdVelPublisher:
    def __init__(self):
        # ノードの作成
        self.node = rclpy.create_node('twist_debug_publisher')
        
        # /cmd_vel トピックを Twist 型でパブリッシュする設定
        self.publisher = self.node.create_publisher(Twist, '/cmd_vel', 10)
        print('ROS 2 Twist 送信ノードが起動しました。1秒おきにランダム値を送信します...')

    def publish_random_twist(self):
        msg = Twist()
        
        # ランダムな値を設定（Simulink側で変化が分かりやすいようにします）
        msg.linear.x = random.uniform(-1.0, 1.0)
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = random.uniform(-0.5, 0.5)
        
        # 送信実行
        self.publisher.publish(msg)
        print(f"【ROS 2送信】Linear.x: {msg.linear.x:.4f}, Angular.z: {msg.angular.z:.4f}")

def main():
    pub = CmdVelPublisher()
    
    try:
        while rclpy.ok():
            pub.publish_random_twist()
            time.sleep(1)  # 1秒周期
            
    except KeyboardInterrupt:
        print("\n停止します。")
    finally:
        # 安全な終了処理
        pub.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()