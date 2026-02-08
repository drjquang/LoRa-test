import serial
import configparser
from serial.tools import list_ports


def load_serial_config(ini_file: str) -> dict:
    config = configparser.ConfigParser()
    config.read(ini_file)

    if "serial" not in config:
        raise ValueError("Missing [serial] section in ini file")

    s = config["serial"]

    comport = s.get("comport").strip().upper()

    # Windows fix for COM >= 10
    if comport.startswith("COM"):
        try:
            if int(comport[3:]) >= 10:
                comport = "\\\\.\\{}".format(comport)
        except ValueError:
            pass

    return {
        "port": comport,
        "baudrate": s.getint("baudrate", 9600),
        "bytesize": serial.EIGHTBITS,
        "parity": {
            "N": serial.PARITY_NONE,
            "E": serial.PARITY_EVEN,
            "O": serial.PARITY_ODD
        }.get(s.get("parity", "N").upper(), serial.PARITY_NONE),
        "stopbits": serial.STOPBITS_ONE if s.getint("stopbits", 1) == 1 else serial.STOPBITS_TWO,
        "timeout": s.getfloat("timeout", 1)
    }


def check_comport_exists(port: str) -> bool:
    ports = [p.device.upper() for p in list_ports.comports()]

    clean_port = port.upper()
    if clean_port.startswith("\\\\.\\"):
        clean_port = clean_port[4:]

    return clean_port in ports


def main():
    ser = None
    try:
        cfg = load_serial_config("serial_config.ini")

        if not check_comport_exists(cfg["port"]):
            print("ERROR: COM port not found")
            return

        ser = serial.Serial(**cfg)
        print(f"Connected to {ser.port} @ {ser.baudrate}")
        print("Waiting for data...\n(Press Ctrl+C to exit)\n")

        while True:
            data = ser.readline()
            if data:
                message = data.decode(errors="ignore").strip()
                print("RECEIVED:", message)

    except serial.SerialException as e:
        print("Serial error:", e)

    except KeyboardInterrupt:
        print("\nExit by user")

    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial port closed")


if __name__ == "__main__":
    main()
