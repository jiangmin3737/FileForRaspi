import zenoh
import struct
import time

def listener(sample):
    # 1. パケット受信の確認
    raw_payload = sample.payload
    print(f"★パケット受信! Rawデータ長: {len(raw_payload)} bytes")
    
    try:
        # 修正ポイント: ZBytesオブジェクトを、通常のPython bytesに変換してからスライスする！
        py_bytes = raw_payload.to_bytes()
        payload = py_bytes[4:]
        
        # Twistの48バイトを切り出してデコード
        twist_data = payload[:48]
        unpacked_data = struct.unpack('<dddddd', twist_data)
        
        linear_x  = unpacked_data[0]
        linear_y  = unpacked_data[1]
        linear_z  = unpacked_data[2]
        angular_x = unpacked_data[3]
        angular_y = unpacked_data[4]
        angular_z = unpacked_data[5]
        
        print(f"  Linear  -> x: {linear_x:.6f}, y: {linear_y:.6f}, z: {linear_z:.6f}")
        print(f"  Angular -> x: {angular_x:.6f}, y: {angular_y:.6f}, z: {angular_z:.6f}")
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ デコード失敗: {e}")

def main():
    print("Zenoh セッションを開始中...")
    
    # 1. 空のConfigを作る
    conf = zenoh.Config()
    
    # 2. 【超重要】別PCのUbuntuルーターのIPアドレスを明示的に指定する
    # 例としてルーターのIPが '192.168.10.4' の場合（実際のIPに書き換えてください）
    router_ip = "192.168.10.4" 
    
    # insert_json5を使って、接続先（endpoints）を設定に叩き込む
    conf.insert_json5("connect.endpoints", f'["tcp/{router_ip}:7447"]')
    
    # 3. 指定したIPに向けてセッションを開く
    session = zenoh.open(conf)
    
    key_expression = "cmd_vel"
    print(f"Zenohで [{key_expression}] のサブスクライブを開始しました。データを待っています...")
    sub = session.declare_subscriber(key_expression, listener)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nユーザーによって停止されました。")
    finally:
        sub.undeclare()
        session.close()
        print("Zenoh セッションを正常に終了しました。")

if __name__ == "__main__":
    main()