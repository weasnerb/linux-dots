#!/usr/bin/env python3
"""Cycle the ThinkPad keyboard backlight: off -> dim -> bright -> off.

Previously driven by `light`, which is archived upstream. That version read a
percentage and special-cased the strings "0.00"/"50.00"/"100.00", because the
LED actually has only three levels (max_brightness = 2). brightnessctl speaks
in raw levels, so the cycle is plain modulo arithmetic.
"""
import subprocess

DEVICE = "tpacpi::kbd_backlight"


def brightnessctl(*args):
    return subprocess.run(
        ["brightnessctl", "--device", DEVICE, *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


current = int(brightnessctl("get"))
maximum = int(brightnessctl("max"))
brightnessctl("set", str((current + 1) % (maximum + 1)))
