import rclpy
import time

# 1. WindowsやWSL2でのインポート順序バグを防ぐため、最優先で初期化
rclpy.init()

# 2. 初期化完了後にメッセージ型をインポート
from geometry_msgs.msg import TwistStamped

class TwistStampedSubscriber:
    def __init__(self):
        self.node = rclpy.create_node('latency_debug_subscriber')
        
        # /cmd_vel_stamped トピックを TwistStamped 型で購読
        self.subscription = self.node.create_subscription(
            TwistStamped,
            '/cmd_vel_ts',
            self.listener_callback,
            10
        )
        print('【ROS 2】TwistStamped 遅延測定ノードが起動しました。データを待っています...')

    def listener_callback(self, msg):
        # 1. 受信した瞬間のPC（WSL2）側のシステム時刻を高精度で取得
        recv_time = time.time()
        
        # 2. メッセージ内のheaderからSimulinkの送信時刻を取得
        sec = msg.header.stamp.sec
        nanosec = msg.header.stamp.nanosec
        
        # エポックタイム（秒）の浮動小数点に復元
        simulink_publish_time = sec + (nanosec / 1e9)
        
        # 3. 片道の通信遅延をミリ秒（ms）に計算
        # ※注意: PC間の時計が完全に同期していない場合、ここの数値がズレます
        latency_ms = (recv_time - simulink_publish_time) * 1000
        
        # 4. コンソールに綺麗に表示
        print(f"★パケット受信成功!")
        print(f"  Simulink送信時刻 : {sec}.{nanosec:09d}")
        print(f"  WSL2受信時刻     : {recv_time:.6f}")
        print(f"  ネットワーク遅延 : {latency_ms:.2f} ms")
        print(f"  [データ値] Linear.x: {msg.twist.linear.x:.6f}, Angular.x: {msg.twist.angular.x:.6f}")
        print("-" * 50)

def main():
    subscriber = TwistStampedSubscriber()
    
    try:
        rclpy.spin(subscriber.node)
    except KeyboardInterrupt:
        print("\n測定を停止します。")
    finally:
        # 安全なクリーンアップ（二重シャットダウン防止）
        subscriber.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()