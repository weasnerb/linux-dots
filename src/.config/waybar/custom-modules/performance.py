#!/usr/bin/env python3
"""Combined power-profile + CPU/RAM indicator for waybar (custom/performance).

Run with no arguments, it stays running and prints one JSON line per update
(waybar reads a long-running custom module line by line):
  - icon: the active power profile (performance / balanced / power-saver),
    read from tlp-pd over the power-profiles-daemon D-Bus API
  - class `high` (red in style.css) when CPU or RAM usage is >= THRESHOLD
  - tooltip: profile, total and per-core CPU, RAM percent and amount used
It updates every INTERVAL seconds, and immediately when the profile changes.

Clicking sends SIGUSR1 to this running process (pid in PID_FILE), which
switches to the next profile itself. Doing it in-process avoids starting
Python on every click (~0.25s), and the icon changes at once instead of
waiting the ~0.35s tlp-pd takes to apply TLP and confirm. The requested
profile is remembered until tlp-pd confirms it, so quick repeated clicks each
advance one step. `performance.py cycle` sends the same signal from a shell.

Low battery: on battery power at <= BATTERY_WARNING percent it shows an urgent
notification and switches to power-saver; at <= BATTERY_CRITICAL a second
urgent notification (UPower hibernates at 2%). Each fires once per discharge.
These match the waybar battery module's warning/critical states. On plug-in
the notification is closed, and if this script was what switched to
power-saver it goes back to performance (TLP's own AC auto-switch would skip
it, since it sees the power-saver switch as a manual change).
"""
import json
import os
import signal
import sys
import time

from gi.repository import Gio, GLib

INTERVAL = 2
THRESHOLD = 80

BUS_NAME = 'org.freedesktop.UPower.PowerProfiles'
OBJ_PATH = '/org/freedesktop/UPower/PowerProfiles'
IFACE = 'org.freedesktop.UPower.PowerProfiles'

PID_FILE = os.path.join(
    os.environ.get('XDG_RUNTIME_DIR') or '/tmp', 'waybar-performance.pid')
# A request tlp-pd hasn't confirmed within this long is assumed to have failed.
PENDING_SECS = 5

BATTERY = '/sys/class/power_supply/BAT0'
BATTERY_WARNING = 15
BATTERY_CRITICAL = 5
NOTIFY_BUS = 'org.freedesktop.Notifications'
NOTIFY_PATH = '/org/freedesktop/Notifications'

# Left-click cycle order: power-saver -> balanced -> performance -> (wraps).
PROFILES = ['power-saver', 'balanced', 'performance']
ICONS = {
    'performance': '\U000F04C5',  # mdi speedometer
    'balanced': '\U000F0F85',     # mdi speedometer-medium
    'power-saver': '\U000F0F86',  # mdi speedometer-slow
}
LABELS = {
    'performance': 'Performance',
    'balanced': 'Balanced',
    'power-saver': 'Power saver',
}


def cpu_times():
    """{'cpu': (idle, total), 'cpu0': (idle, total), ...} from /proc/stat."""
    times = {}
    with open('/proc/stat') as f:
        for line in f:
            if not line.startswith('cpu'):
                break
            name, *values = line.split()
            fields = [int(x) for x in values]
            times[name] = (fields[3] + fields[4], sum(fields))  # idle+iowait
    return times


def usage(prev, cur):
    idle = cur[0] - prev[0]
    total = cur[1] - prev[1]
    return round(100 * (total - idle) / max(total, 1))


def memory():
    info = {}
    with open('/proc/meminfo') as f:
        for line in f:
            key, value = line.split(':', 1)
            info[key] = int(value.split()[0])  # kB
    total = info['MemTotal']
    used = total - info['MemAvailable']
    return round(100 * used / total), used / 1024**2, total / 1024**2


def battery():
    """(capacity percent, on battery power?) or None if there is no battery."""
    try:
        with open(f'{BATTERY}/capacity') as f:
            capacity = int(f.read())
        with open(f'{BATTERY}/status') as f:
            discharging = f.read().strip() == 'Discharging'
    except (OSError, ValueError):
        return None
    return capacity, discharging


class Monitor:
    def __init__(self):
        try:
            self.proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SYSTEM, Gio.DBusProxyFlags.NONE, None,
                BUS_NAME, OBJ_PATH, IFACE, None)
            self.proxy.connect('g-properties-changed', self.on_profile_change)
        except GLib.Error:
            self.proxy = None
        self.pending = None  # (profile, monotonic time requested)
        self.prev = cpu_times()
        self.stats = None
        self.warned = set()       # battery levels already notified this discharge
        self.auto_saver = False   # did *we* switch to power-saver?
        self.notify_id = 0        # dunst id, so warning -> critical replaces it

    def actual_profile(self):
        value = self.proxy.get_cached_property('ActiveProfile') if self.proxy else None
        return value.unpack() if value is not None else None

    def shown_profile(self):
        if self.pending and time.monotonic() - self.pending[1] < PENDING_SECS:
            return self.pending[0]
        self.pending = None
        return self.actual_profile()

    def set_profile(self, profile):
        self.pending = (profile, time.monotonic())
        self.emit()
        self.proxy.call(
            'org.freedesktop.DBus.Properties.Set',
            GLib.Variant('(ssv)', (IFACE, 'ActiveProfile', GLib.Variant('s', profile))),
            Gio.DBusCallFlags.NONE, -1, None, None)

    def cycle(self):
        if not self.proxy:
            return GLib.SOURCE_CONTINUE
        current = self.shown_profile()
        nxt = PROFILES[(PROFILES.index(current) + 1) % len(PROFILES)] \
            if current in PROFILES else 'balanced'
        self.auto_saver = False  # a manual pick overrides the low-battery switch
        self.set_profile(nxt)
        return GLib.SOURCE_CONTINUE

    def notify(self, summary, body):
        """Urgent dunst notification; replaces our previous one if still up."""
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            reply = bus.call_sync(
                NOTIFY_BUS, NOTIFY_PATH, NOTIFY_BUS, 'Notify',
                GLib.Variant('(susssasa{sv}i)', (
                    'battery', self.notify_id, '', summary, body, [],
                    {'urgency': GLib.Variant('y', 2)}, 0)),  # 2 = critical, 0 = no timeout
                GLib.VariantType('(u)'), Gio.DBusCallFlags.NONE, -1, None)
            self.notify_id = reply.unpack()[0]
        except GLib.Error:
            pass

    def close_notification(self):
        if not self.notify_id:
            return
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            bus.call_sync(NOTIFY_BUS, NOTIFY_PATH, NOTIFY_BUS, 'CloseNotification',
                          GLib.Variant('(u)', (self.notify_id,)),
                          None, Gio.DBusCallFlags.NONE, -1, None)
        except GLib.Error:
            pass
        self.notify_id = 0

    def check_battery(self):
        state = battery()
        if state is None:
            return
        capacity, discharging = state

        if not discharging:
            if self.warned:
                self.warned.clear()
                self.close_notification()
            if self.auto_saver:
                self.auto_saver = False
                if self.proxy and self.shown_profile() == 'power-saver':
                    self.set_profile('performance')
            return

        if capacity > BATTERY_WARNING:
            return
        level = 'critical' if capacity <= BATTERY_CRITICAL else 'warning'
        if level in self.warned:
            return
        # A gauge correction can jump straight past 15% to <= 5%; the critical
        # notice then covers both, and the power-saver switch still happens.
        self.warned.update({'warning', level})

        switched = False
        if self.proxy and self.shown_profile() != 'power-saver':
            self.set_profile('power-saver')
            self.auto_saver = switched = True
        saver_note = 'Switched to power saver.' if switched else 'Power saver is on.'

        if level == 'critical':
            self.notify('Battery critical',
                        f'{capacity}% left. Plug in now: the laptop hibernates at 2%.'
                        + ('' if not switched else f' {saver_note}'))
        else:
            self.notify('Battery low', f'{capacity}% left. {saver_note}')

    def sample(self):
        cur = cpu_times()
        cpu = usage(self.prev['cpu'], cur['cpu'])
        cores = [usage(self.prev[n], cur[n]) for n in sorted(
            (n for n in cur if n != 'cpu'), key=lambda n: int(n[3:]))]
        self.prev = cur
        self.stats = (cpu, cores, *memory())

    def emit(self):
        profile = self.shown_profile()
        lines = [f'Profile: {LABELS.get(profile, "unavailable (is tlp-pd running?)")}']
        high = False
        if self.stats:
            cpu, cores, mem, used_gib, total_gib = self.stats
            lines += ['', f'CPU: {cpu}%']
            lines += [f'  Core {i}: {c}%' for i, c in enumerate(cores)]
            lines += ['', f'RAM: {mem}%', f'  {used_gib:.1f} / {total_gib:.1f} GiB']
            high = cpu >= THRESHOLD or mem >= THRESHOLD
        try:
            print(json.dumps({
                'text': ICONS.get(profile, ICONS['balanced']),
                'tooltip': '\n'.join(lines),
                'class': ['high' if high else 'normal', profile or 'unknown'],
            }), flush=True)
        except BrokenPipeError:
            # waybar has gone away. Exceptions raised inside GLib callbacks are
            # only logged, never fatal, so exit explicitly or this process is
            # orphaned and keeps running forever.
            os._exit(0)

    def tick(self):
        self.sample()
        self.check_battery()
        self.emit()
        return GLib.SOURCE_CONTINUE

    def on_profile_change(self, _proxy, changed, _invalidated):
        if 'ActiveProfile' in changed.keys():
            if self.pending and changed['ActiveProfile'] == self.pending[0]:
                self.pending = None
            self.emit()


def send_cycle():
    with open(PID_FILE) as f:
        os.kill(int(f.read()), signal.SIGUSR1)


def main():
    if sys.argv[1:] == ['cycle']:
        send_cycle()
        return
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    monitor = Monitor()
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGUSR1, monitor.cycle)
    monitor.emit()  # profile icon right away; CPU needs one interval to measure
    GLib.timeout_add_seconds(INTERVAL, monitor.tick)
    GLib.MainLoop().run()


if __name__ == '__main__':
    try:
        main()
    except (BrokenPipeError, KeyboardInterrupt):
        sys.exit(0)
