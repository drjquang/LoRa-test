# serial_manager.py

import serial
import threading
import time
import configparser
from queue import Queue

class SerialManager:
    def __init__(self, queue: Queue):
        self.queue = queue
        self.ser = None
        self.running = False
        self.status = "Disconnected"

        self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read("serial_config.ini")

        self.port = config.get("serial", "port", fallback="COM3")
        self.baudrate = config.getint("serial", "baudrate", fallback=9600)
        self.timeout = config.getfloat("serial", "timeout", fallback=1)

    def connect(self):
        try:
            self.ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout
            )
            self.status = "Connected"
        except Exception as e:
            self.ser = None
            self.status = f"Disconnected"

    def start(self):
        self.running = True
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while self.running:
            if self.ser is None or not self.ser.is_open:
                self.connect()
                time.sleep(2)
                continue

            try:
                if self.ser.in_waiting:
                    data = self.ser.readline().decode(errors="ignore").strip()
                    if data.isdigit():
                        num = int(data)
                        if 0 <= num <= 37:
                            self.queue.put(("SERIAL", num))
            except Exception:
                self.status = "Disconnected"
                try:
                    self.ser.close()
                except:
                    pass
                self.ser = None

            time.sleep(0.05)
