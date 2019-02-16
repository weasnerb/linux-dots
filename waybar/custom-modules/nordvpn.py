#!/usr/bin/env python3
import sys
import signal
import subprocess

def get_vpn_info():
    vpn_info = {}
    completed_process = subprocess.run(['nordvpn', 'status'], capture_output=True, text=True)
    if completed_process.returncode == 0:
        lines = str(completed_process.stdout).split('\n')
        for line in lines:
            key_value_pair = str(line).split(': ')
            if len(key_value_pair) == 2:
                vpn_info[str(key_value_pair[0]).lower()] = str(key_value_pair[1])
    return vpn_info


def run():
    displayed_vpn_info = ''
    vpn_info = get_vpn_info()
    if vpn_info.get('status') == 'Connected':
        displayed_vpn_info = '%s, %s' % (vpn_info.get('city'), vpn_info.get('country'))

    sys.stdout.write(displayed_vpn_info + '\n')
    sys.stdout.flush()

run()