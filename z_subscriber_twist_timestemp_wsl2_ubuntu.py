import zenoh
import struct
import time
import json

def listener(sample):
    # 受信した瞬間のWSL2側のシステム時刻（エポックタイム秒）を高精度で取得
    recv_time = time.time()
    
    raw_payload = sample.payload
    py_bytes = raw_payload.to_bytes()
    
    try:
        # ROS 2の4バイトヘッダーを剥ぎ取る
        payload = py_bytes[4:]
        
        # TwistStampedの構造解析:
        # 先頭から [秒(4バイト整数: i)] + [ナノ秒(4バイト無符号整数: I)] を切り出す
        sec, nanosec = struct.unpack('<iI', payload[0:8])
        
        # Simulink側がパブリッシュした時刻をエポックタイム（秒）に復元
        simulink_publish_time = sec + (nanosec / 1e9)
        
        # ⚠️ 注意: 3台のPC間の時計が完全に同期（NTP同期）していない場合、
        # 遅延がマイナスになったり異常に大きくなったりします。
        # 純粋な通信の「揺らぎ（ジッタ）」を見るか、事前にPC間の時刻同期が必要です。
        latency_ms = (recv_time - simulink_publish_time) * 1000
        
        # 後半のTwistデータ（linear.xなど）も必要であれば、構造体のオフセット（位置）をずらして抽出可能
        # 今回は遅延測定をメインにするため時刻のみ表示
        
        print(f"【RTT計測】パケット受信 | Simulink送信時刻: {sec}.{nanosec:09d}")
        print(f"            WSL2受信時刻: {recv_time:.6f}")
        print(f"            片道通信遅延: {latency_ms:.2f} ms")
        print("-" * 50)
        
    except Exception as e:
        print(f"デコード失敗: {e}")

def main():
    print("Zenoh セッションを開始中...")
    conf = zenoh.Config()
    
    # PC②（Ubuntuルーター）のIPアドレスを指定
    router_ip = "192.168.10.7" 
    conf.insert_json5("connect", f'{{"endpoints": ["tcp/{router_ip}:7447"]}}')
    
    session = zenoh.open(conf)
    
    # ブリッジが中継するキー名（Simulinkのトピック名に連動）
    key_expression = "cmd_vel_ts"
    
    print(f"Zenohで [{key_expression}] の遅延測定を開始しました。")
    sub = session.declare_subscriber(key_expression, listener)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n計測を停止します。")
    finally:
        sub.undeclare()
        session.close()

if __name__ == "__main__":
    main()