import ctypes
import keyboard
import csv
import os
import sys
import pystray
from PIL import Image
from pathlib import Path

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

kernel32.CreateMutexW.restype = ctypes.c_void_p

mutex = kernel32.CreateMutexW(None, False, "NumDeck_SingleInstance")

if not mutex or ctypes.get_last_error() == 183:
    sys.exit(0)
# Locate the external configuration file
if getattr(sys, "frozen", False):
    config_path = Path(sys.executable).with_name("config.csv")
else:
    config_path = Path(__file__).with_name("config.csv")

config = {}

with open(config_path, "r", newline="", encoding="utf-8-sig") as file:
    for row in csv.DictReader(file):
        config[row["scan_code"]] = row["action"]


def get_numlock():
    return bool(ctypes.windll.user32.GetKeyState(0x90) & 1)


def handle_key(event):
    if event.is_keypad and not get_numlock():

        if event.event_type == "down":
            action = config.get(str(event.scan_code), "").strip()

            if action:
                print(repr(action))

                if action.startswith("open:"):
                    path = action[5:].strip().strip('"')
                    keyboard.call_later(os.startfile, args=(path,))
                else:
                    keyboard.call_later(keyboard.send, args=(action,))

        return False

    return True


def create_icon():
    return Image.open(Path(__file__).with_name("icon.ico"))


def open_config(icon, item):
    os.startfile(config_path)


def quit_app(icon, item):
    icon.stop()


unhook = keyboard.hook(handle_key, suppress=True)

icon = pystray.Icon(
    "NumDeck",
    create_icon(),
    "NumDeck",
    menu=pystray.Menu(
        pystray.MenuItem("Open CSV", open_config),
        pystray.MenuItem("Exit", quit_app)
    )
)

try:
    icon.run()
finally:
    unhook()