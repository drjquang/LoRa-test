import tkinter as tk
import serial
import threading
import json
import os
import random
import constants


# =======================
# Config helpers
# =======================
def load_config():
    if os.path.exists(constants.CONFIG_FILE):
        with open(constants.CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(constants.CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =======================
# Serial port prompt
# =======================
def prompt_for_serial_port():
    while True:
        port = input("Enter serial port (e.g. COM16): ").strip()
        try:
            ser = serial.Serial(
                port=port,
                baudrate=constants.SERIAL_BAUDRATE,
                timeout=constants.SERIAL_TIMEOUT
            )
            ser.close()
            save_config({"serial_port": port})
            print(f"✔ Connected to {port}, saved to config.json")
            return port
        except Exception as e:
            print("✖ Cannot open port:", e)


# =======================
# Roulette color logic
# =======================
def roulette_color(value):
    if value == 0:
        return constants.COLOR_GREEN
    elif value in constants.RED_NUMBERS:
        return constants.COLOR_RED
    else:
        return constants.COLOR_BLACK


# =======================
# Main App
# =======================
class RouletteApp:
    def __init__(self, root, serial_port):
        self.root = root
        self.serial_port = serial_port
        self.ser = None
        self.running = True

        root.title(constants.APP_TITLE)
        root.configure(bg=constants.BG_COLOR)

        if constants.FULLSCREEN:
            root.attributes("-fullscreen", True)

        # ---------- Header ----------
        header = tk.Frame(
            root,
            height=constants.HEADER_HEIGHT,
            bg=constants.HEADER_BG
        )
        header.pack(side="top", fill="x")

        tk.Label(
            header,
            text=constants.HEADER_TEXT,
            bg=constants.HEADER_BG,
            fg=constants.HEADER_FG,
            font=constants.HEADER_FONT
        ).pack(expand=True)

        # ---------- Body ----------
        self.body = tk.Frame(root, bg=constants.BG_COLOR)
        self.body.pack(expand=True)

        self.matrix = []
        self.create_matrix()

        # ---------- Footer ----------
        footer = tk.Frame(
            root,
            height=constants.FOOTER_HEIGHT,
            bg=constants.FOOTER_BG
        )
        footer.pack(side="bottom", fill="x")

        self.status_label = tk.Label(
            footer,
            text=constants.STATUS_DISCONNECTED,
            fg=constants.COLOR_DISCONNECTED,
            bg=constants.FOOTER_BG,
            font=constants.FOOTER_FONT
        )
        self.status_label.pack(side="left", padx=20)

        self.source_label = tk.Label(
            footer,
            text="SOURCE: NONE",
            fg="white",
            bg=constants.FOOTER_BG,
            font=constants.FOOTER_FONT
        )
        self.source_label.pack(side="left", expand=True)

        tk.Button(
            footer,
            text="Generate",
            width=14,
            command=self.generate
        ).pack(side="right", padx=20, pady=10)

        self.connect_serial()
        root.protocol("WM_DELETE_WINDOW", self.close)

    # =======================
    # Matrix
    # =======================
    def create_matrix(self):
        for r in range(constants.ROWS):
            row = []
            for c in range(constants.COLS):
                # Square container (pixel-perfect)
                cell = tk.Frame(
                    self.body,
                    width=constants.CELL_SIZE,
                    height=constants.CELL_SIZE,
                    bg=constants.BG_COLOR,
                    highlightthickness=constants.CELL_BORDER_WIDTH,
                    highlightbackground=constants.HEADER_BG
                )
                cell.grid(
                    row=r,
                    column=c,
                    padx=constants.CELL_PADX,
                    pady=constants.CELL_PADY
                )
                cell.pack_propagate(False)  # IMPORTANT

                # Label inside square
                lbl = tk.Label(
                    cell,
                    text="",
                    font=constants.CELL_FONT,
                    fg=constants.CELL_FG,
                    bg=constants.BG_COLOR
                )
                lbl.pack(fill="both", expand=True)

                row.append(lbl)

            self.matrix.append(row)

    def shift_matrix(self, value):
        values = []
        colors = []

        for row in self.matrix:
            for lbl in row:
                values.append(lbl["text"])
                colors.append(lbl["bg"])

        values.insert(0, str(value))
        colors.insert(0, roulette_color(value))

        values = values[:constants.ROWS * constants.COLS]
        colors = colors[:constants.ROWS * constants.COLS]

        idx = 0
        for r in range(constants.ROWS):
            for c in range(constants.COLS):
                self.matrix[r][c].config(
                    text=values[idx],
                    bg=colors[idx] if values[idx] else constants.BG_COLOR
                )
                idx += 1

    # =======================
    # Serial
    # =======================
    def connect_serial(self):
        try:
            self.ser = serial.Serial(
                self.serial_port,
                constants.SERIAL_BAUDRATE,
                timeout=constants.SERIAL_TIMEOUT
            )
            self.status_label.config(
                text=constants.STATUS_CONNECTED,
                fg=constants.COLOR_CONNECTED
            )
            threading.Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            self.status_label.config(
                text=constants.STATUS_DISCONNECTED,
                fg=constants.COLOR_DISCONNECTED
            )
            print("Serial connection error:", e)

    def read_serial(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line.isdigit():
                    value = int(line)
                    self.root.after(0, self.on_serial_data, value)
            except Exception:
                break

    def on_serial_data(self, value):
        self.shift_matrix(value)
        self.source_label.config(text="SOURCE: SERIAL")

    # =======================
    # Generate
    # =======================
    def generate(self):
        value = random.randint(constants.GENERATE_MIN, constants.GENERATE_MAX)
        self.shift_matrix(value)
        self.source_label.config(text="SOURCE: GENERATE")

    # =======================
    # Close
    # =======================
    def close(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.root.destroy()


# =======================
# Entry point
# =======================
if __name__ == "__main__":
    config = load_config()
    port = config.get("serial_port")

    if not port:
        port = prompt_for_serial_port()

    root = tk.Tk()
    RouletteApp(root, port)
    root.mainloop()
