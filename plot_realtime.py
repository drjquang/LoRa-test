import tkinter as tk
from datetime import datetime
import random

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


SAMPLE_INTERVAL_MS = 1000   # 1 second
MAX_POINTS = 60             # last 60 seconds


class RealTimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Data Tracking (1s sampling)")

        self.times = []
        self.values = []

        fig = Figure(figsize=(7, 4))
        self.ax = fig.add_subplot(111)
        self.line, = self.ax.plot([], [], marker="o")

        self.ax.set_title("Live Data Tracking")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.set_ylim(0, 100)

        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_data()

    def update_data(self):
        # Simulated real-time value
        value = random.randint(20, 90)
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.times.append(timestamp)
        self.values.append(value)

        # Keep fixed window
        if len(self.times) > MAX_POINTS:
            self.times.pop(0)
            self.values.pop(0)

        self.line.set_data(range(len(self.values)), self.values)
        self.ax.set_xticks(range(len(self.times)))
        self.ax.set_xticklabels(self.times, rotation=45, ha="right")

        self.ax.set_xlim(0, MAX_POINTS)
        self.canvas.draw()

        # Schedule next sample (1 second)
        self.root.after(SAMPLE_INTERVAL_MS, self.update_data)


root = tk.Tk()
RealTimeTracker(root)
root.mainloop()
