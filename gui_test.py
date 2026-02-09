import tkinter as tk
import random
import threading
import time
import configparser
import serial
import parameters as p


def get_color(n):
    if n == 0:
        return "green"
    elif n in p.RED_NUMBERS:
        return "red"
    else:
        return "black"


class SerialReader:
    def __init__(self):
        self.ser = None
        self.connected = False
        self.last_error = ""

    def connect(self):
        try:
            config = configparser.ConfigParser()
            config.read("serial_config.ini")
            s = config["SERIAL"]

            self.ser = serial.Serial(
                port=s.get("port"),
                baudrate=s.getint("baudrate"),
                bytesize=s.getint("bytesize"),
                parity=s.get("parity"),
                stopbits=s.getint("stopbits"),
                timeout=s.getfloat("timeout"),
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = str(e)

    def read_number(self):
        if not self.connected or not self.ser:
            return None
        try:
            line = self.ser.readline().decode().strip()
            if line.isdigit():
                n = int(line)
                if 0 <= n <= 37:
                    return n
        except:
            pass
        return None


class RouletteApp:
    def __init__(self, root):
        self.root = root
        root.title(p.APP_TITLE)
        root.attributes("-fullscreen", True)
        root.configure(bg=p.APP_BG)

        self.values = []
        self.last_source = "NONE"

        # Layout ratio
        root.rowconfigure(0, weight=p.HEADER_RATIO)
        root.rowconfigure(1, weight=p.BODY_RATIO)
        root.rowconfigure(2, weight=p.FOOTER_RATIO)
        root.columnconfigure(0, weight=1)

        self.header = tk.Frame(root, bg=p.APP_BG, bd=2, relief="groove")
        self.body = tk.Frame(root, bg=p.APP_BG, bd=2, relief="groove")
        self.footer = tk.Frame(root, bg=p.APP_BG, bd=2, relief="groove")

        self.header.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.body.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.footer.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        self.build_header()
        self.build_body()
        self.build_footer()

        # Serial
        self.serial_reader = SerialReader()
        self.serial_reader.connect()
        self.update_serial_status()

        self.running = True
        threading.Thread(target=self.serial_loop, daemon=True).start()

        root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    # ---------- HEADER ----------
    def build_header(self):
        self.title_label = tk.Label(
            self.header,
            text=p.APP_TITLE,
            fg="white",
            bg=p.APP_BG,
            font=(p.FONT_FAMILY, p.HEADER_FONT_SIZE, "bold")
        )
        self.title_label.pack(expand=True)

    # ---------- BODY ----------
    def build_body(self):
        self.canvas = tk.Canvas(self.body, bg=p.APP_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.draw_grid)

    def draw_grid(self, event=None):
        self.canvas.delete("all")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        usable_w = w - 2 * p.MARGIN_X - (p.COLS - 1) * p.CELL_GAP
        usable_h = h - 2 * p.MARGIN_Y - (p.ROWS - 1) * p.CELL_GAP

        cell_size = min(usable_w // p.COLS, usable_h // p.ROWS)

        self.cells = []

        grid_w = cell_size * p.COLS + (p.COLS - 1) * p.CELL_GAP
        grid_h = cell_size * p.ROWS + (p.ROWS - 1) * p.CELL_GAP

        start_x = (w - grid_w) // 2
        start_y = (h - grid_h) // 2

        for r in range(p.ROWS):
            row = []
            for c in range(p.COLS):
                x1 = start_x + c * (cell_size + p.CELL_GAP)
                y1 = start_y + r * (cell_size + p.CELL_GAP)
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=p.EMPTY_CELL_BG,
                    outline=p.BORDER_COLOR,
                    width=2
                )

                text = self.canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text="",
                    fill="white",
                    font=(p.FONT_FAMILY, p.FONT_SIZE, "bold")
                )

                row.append((rect, text))
            self.cells.append(row)

        self.refresh_grid()

    def refresh_grid(self):
        idx = 0
        for r in range(p.ROWS):
            for c in range(p.COLS):
                rect, text = self.cells[r][c]
                if idx < len(self.values):
                    n = self.values[idx]
                    self.canvas.itemconfig(rect, fill=get_color(n))
                    self.canvas.itemconfig(text, text=str(n))
                else:
                    self.canvas.itemconfig(rect, fill=p.EMPTY_CELL_BG)
                    self.canvas.itemconfig(text, text="")
                idx += 1

    # ---------- FOOTER ----------
    def build_footer(self):
        self.footer.columnconfigure(0, weight=1)
        self.footer.columnconfigure(1, weight=1)
        self.footer.columnconfigure(2, weight=1)

        # Serial status (LEFT)
        self.serial_label = tk.Label(
            self.footer,
            text="Serial: Disconnected",
            fg=p.SERIAL_TEXT_COLOR,
            bg=p.APP_BG,
            font=(p.FONT_FAMILY, p.FOOTER_FONT_SIZE, "bold")
        )
        self.serial_label.grid(row=0, column=0, sticky="w", padx=20)

        # Source status (CENTER)
        self.source_label = tk.Label(
            self.footer,
            text="Source: NONE",
            fg="white",
            bg=p.APP_BG,
            font=(p.FONT_FAMILY, p.FOOTER_FONT_SIZE, "bold")
        )
        self.source_label.grid(row=0, column=1)

        # Generate button (RIGHT)
        self.btn = tk.Button(
            self.footer,
            text="GENERATE",
            font=(p.FONT_FAMILY, 20, "bold"),
            bg="green",
            fg="white",
            padx=30,
            pady=10,
            command=self.generate_random
        )
        self.btn.grid(row=0, column=2, sticky="e", padx=20)

    def update_serial_status(self):
        if self.serial_reader.connected:
            self.serial_label.config(
                text="Serial: Connected",
                fg=p.SERIAL_OK_COLOR
            )
        else:
            err = self.serial_reader.last_error
            self.serial_label.config(
                text=f"Serial: Disconnected ({err})",
                fg=p.SERIAL_FAIL_COLOR
            )

    def update_source_status(self, source):
        if source == "RANDOM":
            self.source_label.config(
                text="Source: RANDOM",
                fg=p.SOURCE_RANDOM_COLOR
            )
        elif source == "SERIAL":
            self.source_label.config(
                text="Source: SERIAL",
                fg=p.SOURCE_SERIAL_COLOR
            )

    # ---------- LOGIC ----------
    def push_number(self, n, source):
        self.values.insert(0, n)
        self.values = self.values[:p.ROWS * p.COLS]
        self.refresh_grid()
        self.update_source_status(source)

    def generate_random(self):
        n = random.randint(0, 37)
        self.push_number(n, "RANDOM")

    def serial_loop(self):
        while self.running:
            n = self.serial_reader.read_number()
            if n is not None:
                self.root.after(0, self.push_number, n, "SERIAL")
            time.sleep(0.01)


if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteApp(root)
    root.mainloop()
