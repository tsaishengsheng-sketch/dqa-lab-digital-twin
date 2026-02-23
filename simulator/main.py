import json
import time
import signal
import sys
import random
import threading
import serial

# ---------- 基礎設備類別 ----------
class BaseDevice(threading.Thread):
    def __init__(self, config):
        super().__init__()
        self.daemon = True
        self.config = config
        self.name = config['name']
        self.port = config['port']
        self.baudrate = config.get('baudrate', 9600)
        self.interval = config.get('interval', 1.0)
        self.running = True
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"[{self.name}] 已連接到 {self.port}")
        except Exception as e:
            print(f"[{self.name}] 連接失敗: {e}")
            self.running = False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def generate_data(self):
        raise NotImplementedError

    def run(self):
        self.connect()
        if not self.running:
            return
        while self.running:
            data = self.generate_data()
            if self.ser and self.ser.is_open:
                self.ser.write(data.encode())
            time.sleep(self.interval)
        self.disconnect()

    def stop(self):
        self.running = False

# ---------- 慶聲溫箱模擬器 ----------
class KsonChamber(BaseDevice):
    def __init__(self, config):
        super().__init__(config)
        self.temp = config.get('initial_temp', 25.0)
        self.humi = config.get('initial_humi', 50.0)
        self.mode = config.get('mode', 'constant')

    def generate_data(self):
        # 加入隨機波動，讓數據更真實
        temp_noise = random.uniform(-0.3, 0.3)
        humi_noise = random.uniform(-1, 1)
        current_temp = round(self.temp + temp_noise, 2)
        current_humi = round(self.humi + humi_noise, 1)

        # 模擬慶聲溫箱的 ASCII 協議（格式可調整）
        data = f"ID:{self.name},TEMP:{current_temp},HUMI:{current_humi},STATUS:RUN\n"
        return data

# ---------- 主程式 ----------
def signal_handler(sig, frame):
    print("\n收到中斷訊號，結束所有模擬器執行緒...")
    for device in devices:
        device.stop()
    sys.exit(0)

if __name__ == "__main__":
    # 讀取設定檔
    with open('config.json', 'r') as f:
        config = json.load(f)

    devices = []
    for dev_cfg in config['devices']:
        if dev_cfg['type'] == 'kson_chamber':
            dev = KsonChamber(dev_cfg)
            devices.append(dev)

    signal.signal(signal.SIGINT, signal_handler)

    for dev in devices:
        dev.start()
        print(f"已啟動 {dev.name}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass