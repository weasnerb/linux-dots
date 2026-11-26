#!/usr/bin/env python3
import os
import sys
import json
import html
import time
import fcntl
import subprocess

# key-variant. MDI has no key-off glyph, so the disconnected states strike this
# through with pango markup instead. The diagonal key crosses cleanly; the plain
# horizontal `key` glyph would swallow the line into its own shaft.
KEY = '\U000F030B'
ARROW = '\U000F0054'  # mdi arrow-right

WAYBAR_SIGNAL = 'RTMIN+8'
MAX_NAME = 20

# Waybar hides a custom module when its text is empty.
HIDDEN = {'text': ''}

OPERATOR_HINT = 'Run once: sudo tailscale set --operator=$USER'


def state_file():
    runtime_dir = os.environ.get('XDG_RUNTIME_DIR') or '/tmp'
    return os.path.join(runtime_dir, 'waybar-tailscale.state')


def tailscale(args, timeout=5):
    try:
        return subprocess.run(['tailscale'] + args, capture_output=True,
                              text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_tailscale_status():
    completed_process = tailscale(['status', '--json'])
    if completed_process is None or completed_process.returncode != 0:
        return None
    try:
        return json.loads(completed_process.stdout)
    except json.JSONDecodeError:
        return None


def get_dns_info(status):
    completed_process = tailscale(['dns', 'status', '--json'])
    if completed_process is None or completed_process.returncode != 0:
        return None
    try:
        dns_info = json.loads(completed_process.stdout)
    except json.JSONDecodeError:
        return None

    # Drop the tailnet's own suffix; only custom split-DNS domains are interesting.
    # With MagicDNS off the suffix is empty, and every string ends with '', so
    # only filter on it when there is one.
    suffix = (status.get('MagicDNSSuffix') or '').rstrip('.')
    routes = []
    for domain in (dns_info.get('SplitDNSRoutes') or {}):
        bare = domain.rstrip('.')
        if bare and bare != 'ts.net' and not (suffix and bare.endswith(suffix)):
            routes.append(bare)
    dns_info['_routes'] = sorted(routes)
    return dns_info


def get_exit_node(status):
    for peer in (status.get('Peer') or {}).values():
        if peer.get('ExitNode'):
            return peer
    return None


def hostname(node):
    return node.get('HostName') or (node.get('DNSName') or '').split('.')[0]


def shorten(name):
    if len(name) <= MAX_NAME:
        return name
    return name[:MAX_NAME - 1] + '…'


def escape(text):
    return html.escape(str(text), quote=False)


def struck(icon):
    return '<span strikethrough="true">%s</span>' % icon


def build_tooltip(status, dns_info, exit_node):
    self_node = status.get('Self') or {}
    tailnet = status.get('CurrentTailnet') or {}
    lines = []

    if tailnet.get('Name'):
        lines.append('<b>%s</b>' % escape(tailnet.get('Name')))
    if self_node.get('DNSName'):
        lines.append(escape(self_node.get('DNSName').rstrip('.')))
    for ip in status.get('TailscaleIPs') or []:
        lines.append(escape(ip))

    if exit_node is not None:
        lines.append('')
        lines.append('Exit node: %s' % escape(hostname(exit_node)))

    if dns_info is not None:
        lines.append('')
        if dns_info.get('TailscaleDNS'):
            dns_line = 'DNS: Tailscale'
            if dns_info.get('_routes'):
                dns_line += '  ·  split routes: %s' % escape(
                    ', '.join(dns_info['_routes']))
            lines.append(dns_line)
        else:
            lines.append('DNS: system default — split DNS inactive')

    peers = list((status.get('Peer') or {}).values())
    if peers:
        online = [peer for peer in peers if peer.get('Online')]
        lines.append('')
        lines.append('Peers: %d/%d online' % (len(online), len(peers)))
        peers.sort(key=lambda peer: (not peer.get('Online'),
                                     hostname(peer).lower()))
        for peer in peers:
            marker = '●' if peer.get('Online') else '○'
            lines.append('  %s %s' % (marker, escape(hostname(peer))))

    warnings = status.get('Health') or []
    if warnings:
        lines.append('')
        for warning in warnings:
            lines.append('⚠ %s' % escape(warning))

    return '\n'.join(lines)


def notify(summary, body='', urgency='normal'):
    # Fire and forget: notify-send blocks until the notification daemon answers,
    # and a wedged daemon would otherwise stall the module on every poll.
    try:
        subprocess.Popen(['notify-send', '-u', urgency, '-a', 'Tailscale',
                          summary, body],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    except FileNotFoundError:
        pass


# A connect/disconnect started from this module (click or menu) is recorded
# here, so the resulting transition is announced as a normal notification
# rather than as an unexpected, persistent critical one.
EXPECTED_SECS = 60


def expected_file():
    return state_file() + '.expected'


def mark_expected():
    try:
        with open(expected_file(), 'w') as handle:
            handle.write(str(time.time()))
    except OSError:
        pass


def clear_expected():
    try:
        os.remove(expected_file())
    except OSError:
        pass


def take_expected():
    """True if this module requested a change in the last EXPECTED_SECS."""
    try:
        with open(expected_file()) as handle:
            requested = float(handle.read())
        os.remove(expected_file())
    except (OSError, ValueError):
        return False
    return time.time() - requested < EXPECTED_SECS


def notify_on_change(backend_state):
    # Waybar runs one copy of this module per bar (per monitor), and a refresh
    # signal reaches them all at once. The lock makes the read-compare-write
    # atomic, so only the first copy sees the transition and notifies.
    try:
        lock = open(state_file() + '.lock', 'w')
        fcntl.flock(lock, fcntl.LOCK_EX)
    except OSError:
        lock = None
    try:
        _notify_on_change(backend_state)
    finally:
        if lock:
            lock.close()


# Only these states are tracked. Transitional ones (e.g. Starting while Wi-Fi
# roams) are ignored entirely, so Running -> Starting -> Running doesn't look
# like a fresh connection or use up the "expected" marker.
NOTIFY_STATES = ('Running', 'Stopped', 'NeedsLogin', 'NeedsMachineAuth')


def _notify_on_change(backend_state):
    if backend_state not in NOTIFY_STATES:
        return
    path = state_file()
    previous = None
    try:
        with open(path) as handle:
            previous = handle.read().strip()
    except OSError:
        pass

    try:
        with open(path, 'w') as handle:
            handle.write(backend_state or '')
    except OSError:
        pass

    # No notification on the first run after login, only on real transitions.
    if previous is None or previous == backend_state:
        return

    requested = take_expected()
    if backend_state == 'Running':
        notify('Tailnet connected')
    elif backend_state == 'Stopped':
        notify('Tailnet disconnected',
               urgency='normal' if requested else 'critical')
    elif backend_state in ('NeedsLogin', 'NeedsMachineAuth'):
        notify('Tailscale logged out', 'Click the module to authenticate',
               urgency='critical')


def render():
    status = get_tailscale_status()
    if status is None:
        sys.stdout.write(json.dumps(HIDDEN) + '\n')
        sys.stdout.flush()
        return

    backend_state = status.get('BackendState')
    notify_on_change(backend_state)

    if backend_state == 'Running':
        exit_node = get_exit_node(status)
        dns_info = get_dns_info(status)
        text = escape(shorten(hostname(status.get('Self') or {})))
        css_class = 'connected'
        if exit_node is not None:
            text = '%s %s %s' % (text, ARROW,
                                 escape(shorten(hostname(exit_node))))
            css_class = 'exit-node'
        if status.get('Health'):
            css_class = 'warning'
        module = {'text': '%s %s' % (KEY, text),
                  'tooltip': build_tooltip(status, dns_info, exit_node),
                  'class': css_class}
    elif backend_state == 'Stopped':
        module = {'text': '%s Disconnected' % struck(KEY),
                  'tooltip': build_tooltip(status, None, None),
                  'class': 'disconnected'}
    elif backend_state in ('NeedsLogin', 'NeedsMachineAuth'):
        module = {'text': '%s Logged out' % struck(KEY),
                  'tooltip': 'Not logged in to a tailnet\nClick to authenticate',
                  'class': 'logged-out'}
    else:
        module = HIDDEN

    sys.stdout.write(json.dumps(module) + '\n')
    sys.stdout.flush()


def refresh_bar():
    subprocess.run(['pkill', '-%s' % WAYBAR_SIGNAL, 'waybar'],
                   capture_output=True)


def run_action(args, timeout=30):
    # Mark up/down as expected only if it will actually change the state: a
    # leftover marker would make the next *unexpected* drop look intentional.
    marked = False
    if args[0] in ('up', 'down'):
        status = get_tailscale_status()
        current = status.get('BackendState') if status else None
        if (args[0] == 'down') == (current == 'Running'):
            mark_expected()
            marked = True
    completed_process = tailscale(args, timeout=timeout)
    if marked and (completed_process is None or completed_process.returncode != 0):
        clear_expected()
    if completed_process is None:
        notify('Tailscale did not respond', 'tailscale %s timed out'
               % ' '.join(args), urgency='critical')
    elif completed_process.returncode != 0:
        message = (completed_process.stderr or '').strip()
        # Without an operator set, tailscaled refuses writes from a normal user.
        if 'access denied' in message.lower() or 'permission' in message.lower():
            notify('Tailscale needs permission', OPERATOR_HINT,
                   urgency='critical')
        else:
            notify('Tailscale command failed',
                   message or 'tailscale %s' % ' '.join(args),
                   urgency='critical')
    refresh_bar()


def login():
    # `tailscale up` prints an auth URL and blocks, so it needs a visible terminal.
    subprocess.Popen(['alacritty', '-e', 'tailscale', 'up'])


def toggle():
    status = get_tailscale_status()
    if status is None:
        notify('Tailscale status unavailable',
               'tailscaled did not answer; is it running?')
        return
    backend_state = status.get('BackendState')
    if backend_state == 'Running':
        run_action(['down'])
    elif backend_state == 'Stopped':
        run_action(['up'])
    elif backend_state in ('NeedsLogin', 'NeedsMachineAuth'):
        login()
    else:
        notify('Tailscale is %s' % (backend_state or 'in an unknown state'),
               'Try again in a moment.')


def main():
    args = sys.argv[1:]
    if not args:
        render()
    elif args[0] == 'toggle':
        toggle()
    elif args[0] == 'up':
        # Logged out, `tailscale up` would block waiting for a login and time
        # out; open the login flow instead, as the left-click toggle does.
        status = get_tailscale_status()
        if status and status.get('BackendState') in ('NeedsLogin', 'NeedsMachineAuth'):
            login()
        else:
            run_action(['up'])
    elif args[0] == 'down':
        run_action(['down'])
    elif args[0] == 'dns' and len(args) > 1:
        # `tailscale up --accept-dns=` would demand every other pref be respecified;
        # `set` changes just this one, while connected, and it persists.
        wanted = 'true' if args[1] == 'on' else 'false'
        run_action(['set', '--accept-dns=%s' % wanted], timeout=15)
    else:
        sys.stderr.write('usage: tailscale.py [toggle|up|down|dns on|dns off]\n')
        sys.exit(1)

if __name__ == '__main__':
    main()
