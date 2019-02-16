#!/usr/bin/env python3
import subprocess

base_command = ['light', '-s', 'sysfs/leds/tpacpi::kbd_backlight']

get_current_kbd_backlight = base_command[:]
get_current_kbd_backlight.append('-G')

set_kbd_backlight = base_command[:]
set_kbd_backlight.append('-S')

completed_process = subprocess.run(get_current_kbd_backlight, capture_output=True, text=True)
if completed_process.returncode == 0:
  lines = str(completed_process.stdout).split('\n')
  backlight_percent = lines[0]
  # Backlight seems to only go 0, 50 or 100%, nothing in between? Maybe just 2 different lights
  # print(backlight_percent)
  if backlight_percent == '0.00':
    set_kbd_backlight.append('50')
  elif backlight_percent == '50.00':
    set_kbd_backlight.append('100')
  elif backlight_percent == '100.00':
    set_kbd_backlight.append('0.00')
  else:
    set_kbd_backlight.append('100')
  
  subprocess.run(set_kbd_backlight)
