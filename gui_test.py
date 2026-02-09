# main.py

import tkinter as tk
import random
from queue import Queue
from parameters import *
from serial_manager import SerialManager

class RouletteApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=WINDOW_BG)
        self.root.state("zoomed")

        self.queue = Queue()
        self.serial_manager = SerialManager(self.queue)
        self.serial_manager.start()

        self.labels = []
        self.numbers = []

        self.source = "RANDOM"

        self.build_ui()
        self.root.after(50, self.check_serial)

    # ---------------- UI ----------------

    def build_ui(self):
        self.root.rowconfigure(0, weight=HEADER_RATIO)
        self.root.rowconfigure(1, weight=BODY_RATIO)
        self.root.rowconfigure(2, weight=FOOTER_RATIO)
        self.root.columnconfigure(0, weight=1)

        # Header
        self.header = tk.Frame(self.root, bg=WINDOW_BG, highlightthickness=2, highlightbackground="white")
        self.header.grid(row=0, column=0, sticky="nsew")

        self.title_label = tk.Label(
            self.header,
            text=APP_TITLE,
            fg="white",
            bg=WINDOW_BG,
            font=("Arial", 32, "bold")
        )
        self.title_label.pack(expand=True)

        # Body
        self.body = tk.Frame(self.root, bg=WINDOW_BG, highlightthickness=2, highlightbackground="white")
        self.body.grid(row=1, column=0, sticky="nsew")

        for r in range(ROWS):
            self.body.rowconfigure(r, weight=1)
            for c in range(COLS):
                self.body.columnconfigure(c, weight=1)

                lbl = tk.Label(
                    self.body,
                    text="",
                    fg=COLOR_TEXT,
                    bg=WINDOW_BG,
                    font=("Arial", LABEL_FONT_SIZE, "bold"),
                    width=4,
                    height=2,
                    relief="solid",
                    borderwidth=1
                )
                lbl.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
                self.labels.append(lbl)

        # Footer
        self.footer = tk.Frame(self.root, bg=WINDOW_BG, highlightthickness=2, highlightbackground="white")
        self.footer.grid(row=2, column=0, sticky="nsew")

        self.footer.columnconfigure(0, weight=1)
        self.footer.columnconfigure(1, weight=1)

        self.status_label = tk.Label(
            self.footer,
            text="Serial: Disconnected | Source: RANDOM",
            fg="white",
            bg=WINDOW_BG,
            font=("Arial", 16)
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=20)

        self.btn_generate = tk.Button(
            self.footer,
            text="Generate",
            font=("Arial", 16, "bold"),
            command=self.generate_random
        )
        self.btn_generate.grid(row=0, column=1, sticky="e", padx=20)

    # ---------------- Logic ----------------

    def get_color(self, num):
        if num == 0 or num == 37:
            return COLOR_GREEN
        elif num in RED_NUMBERS:
            return COLOR_RED
        else:
            return COLOR_BLACK

    def push_number(self, num, source):
        self.source = source
        self.numbers.insert(0, num)
        self.numbers = self.numbers[:ROWS * COLS]

        for i, lbl in enumerate(self.labels):
            if i < len(self.numbers):
                n = self.numbers[i]
                lbl.config(text=str(n), bg=self.get_color(n))
            else:
                lbl.config(text="", bg=WINDOW_BG)

        self.update_status()

    def generate_random(self):
        num = random.randint(0, 37)
        self.push_number(num, "RANDOM")

    def check_serial(self):
        while not self.queue.empty():
            source, num = self.queue.get()
            self.push_number(num, source)

        self.update_status()
        self.root.after(50, self.check_serial)

    def update_status(self):
        self.status_label.config(
            text=f"Serial: {self.serial_manager.status} | Source: {self.source}"
        )

# ---------------- Main ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteApp(root)
    root.mainloop()
