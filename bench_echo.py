#!/usr/bin/env python3
"""
bench_echo.py  (ラズパイマウス側)
QoS を bench_rtt_logger.py と統一（BestEffort + keep_last=1000）
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from std_msgs.msg import String


def make_qos(depth: int = 1000) -> QoSProfile:
    return QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
    )


class EchoNode(Node):
    def __init__(self) -> None:
        super().__init__("bench_echo")
        qos = make_qos()
        self.publisher    = self.create_publisher(String, "bench_echo", qos)
        self.subscription = self.create_subscription(
            String, "bench_ping", self._callback, qos
        )
        self.get_logger().info("EchoNode ready.")

    def _callback(self, msg: String) -> None:
        self.publisher.publish(msg)


def main() -> None:
    rclpy.init()
    node = EchoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        context = rclpy.get_default_context()
        if context.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
