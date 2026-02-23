import threading
import time
import serial
from .models import SessionLocal, DeviceData

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate=9600, device_id="CHAMBER_01"):
        super().__init__()
        self.daemon = True
        self.port = port
        self.baudrate = baudrate
        self.device_id = device_id
        self.running = True
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"已連接到 {self.port}")
        except Exception as e:
            print(f"連接 {self.port} 失敗: {e}")
            self.running = False

    def parse_line(self, line):
        """解析類似 'ID:CHAMBER_01,TEMP:25.3,HUMI:52.1,STATUS:RUN' 的格式"""
        data = {}
        parts = line.strip().split(',')
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                data[key] = value
        return data

    def run(self):
        self.connect()
        if not self.running:
            return
        db = SessionLocal()
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode().strip()
                    if line:
                        data = self.parse_line(line)
                        # 根據模擬器輸出的格式，key 可能是 'TEMP' 和 'HUMI'
                        temp_str = data.get('TEMP')
                        humi_str = data.get('HUMI')
                        if temp_str is not None and humi_str is not None:
                            record = DeviceData(
                                device_id=self.device_id,
                                temperature=float(temp_str),
                                humidity=float(humi_str),
                                raw_data=line
                            )
                            db.add(record)
                            db.commit()
                            print(f"[{self.device_id}] 儲存: {temp_str}°C, {humi_str}%")
                except Exception as e:
                    print(f"讀取錯誤: {e}")
            time.sleep(0.1)
        db.close()
        if self.ser and self.ser.is_open:
            self.ser.close()

    def stop(self):
        self.running = False