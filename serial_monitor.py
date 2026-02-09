import serial
import threading
import tkinter as tk

PORT = "COM33"
BAUD = 9600

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Monitor")

        self.status = tk.StringVar(value="Disconnected")
        self.data = tk.StringVar(value="---")

        tk.Label(root, text="Status:").pack(anchor="w")
        tk.Label(root, textvariable=self.status, fg="blue").pack(anchor="w")

        tk.Label(root, text="Received Data:").pack(anchor="w", pady=(10, 0))
        tk.Label(root, textvariable=self.data, fg="green").pack(anchor="w")

        self.ser = None
        self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(
                port=PORT,
                baudrate=BAUD,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.status.set("Connected to " + PORT)
            threading.Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            self.status.set(f"Connection failed: {e}")

    def read_serial(self):
        while True:
            try:
                if self.ser and self.ser.in_waiting:
                    line = self.ser.readline().decode(errors="ignore").strip()
                    self.root.after(0, self.data.set, line)
            except Exception as e:
                self.root.after(0, self.status.set, f"Error: {e}")
                break

root = tk.Tk()
app = SerialApp(root)
root.mainloop()
