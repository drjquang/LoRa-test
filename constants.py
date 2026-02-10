# =======================
# App / Window
# =======================
APP_TITLE = "LoRa testing receiver"
FULLSCREEN = True
BG_COLOR = "#2b1e1e"   # dark brown

# =======================
# Header
# =======================
HEADER_HEIGHT = 80
HEADER_BG = "#1f1414"
HEADER_TEXT = "ROULETTE NUMBER MONITOR"
HEADER_FONT = ("Arial", 26, "bold")
HEADER_FG = "white"

# =======================
# Body / Matrix
# =======================
ROWS = 6
COLS = 13

CELL_SIZE = 90          # <-- TRUE SQUARE SIZE (pixels)
CELL_FONT = ("Arial", 26, "bold")
CELL_FG = "white"
CELL_PADX = 6
CELL_PADY = 6
CELL_BORDER_WIDTH = 2

# Roulette colors
COLOR_GREEN = "#1abc9c"
COLOR_RED = "#c0392b"
COLOR_BLACK = "#000000"

# =======================
# Footer
# =======================
FOOTER_HEIGHT = 70
FOOTER_BG = "#1f1414"
FOOTER_FONT = ("Arial", 14, "bold")

STATUS_CONNECTED = "CONNECTED"
STATUS_DISCONNECTED = "DISCONNECTED"

COLOR_CONNECTED = "lightgreen"
COLOR_DISCONNECTED = "red"

# =======================
# Serial
# =======================
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 1

# =======================
# Config
# =======================
CONFIG_FILE = "config.json"

# =======================
# Generate (simulation)
# =======================
GENERATE_MIN = 0
GENERATE_MAX = 36

# =======================
# Roulette rules
# =======================
RED_NUMBERS = {
    1, 3, 5, 7, 9, 12, 14, 16, 18,
    19, 21, 23, 25, 27, 30, 32, 34, 36
}
