#!/usr/bin/env python3
"""Now-playing module for waybar (custom/media), for any MPRIS player.

Shows whichever player most recently changed track or play state. That
player's instance name (e.g. `vlc.instance123`, unique even when two copies of
one app are open) is written to PLAYER_FILE so the module's click actions
control the player it is showing (`playerctl -p "$(cat ...)"` in the waybar
config) rather than whatever playerctl would pick on its own. When a player closes,
the module falls back to another running player instead of going blank.
A player with no artist/title (e.g. a browser tab that registers MPRIS without
track info) never takes over the display from one that has it, and a player
that isn't playing never takes over from one that is (e.g. a background video
pausing while music plays). Track text is escaped, since waybar reads a custom
module's output as Pango markup and a `&` or `<` would otherwise blank it.
"""
import html
import os
import signal
import sys

import gi
gi.require_version('Playerctl', '2.0')
from gi.repository import Playerctl, GLib  # noqa: E402

PLAYER_FILE = os.path.join(
    os.environ.get('XDG_RUNTIME_DIR') or '/tmp', 'waybar-media-player')

manager = Playerctl.PlayerManager()
loop = GLib.MainLoop()
current = None  # instance name of the player being shown


def write(line):
    try:
        sys.stdout.write(line + '\n')
        sys.stdout.flush()
    except BrokenPipeError:
        # waybar has gone away; GLib only logs exceptions from callbacks, so
        # exit explicitly or this process is orphaned.
        os._exit(0)


def set_current(name):
    """Record which player the module is showing, for the click actions."""
    global current
    current = name
    try:
        if name:
            with open(PLAYER_FILE, 'w') as f:
                f.write(name)
        elif os.path.exists(PLAYER_FILE):
            os.remove(PLAYER_FILE)
    except OSError:
        pass


def track_info(player):
    """Text to show for `player`, or None if it has no track info."""
    metadata = player.props.metadata
    if player.props.player_name == 'spotify' and \
            'mpris:trackid' in metadata.keys() and \
            ':ad:' in metadata['mpris:trackid']:
        return 'AD PLAYING'
    if player.get_artist() and player.get_title():
        return '{artist} - {title}'.format(artist=player.get_artist(),
                                           title=player.get_title())
    return None


def find_player(instance):
    for p in manager.props.players:
        if p.props.player_instance == instance:
            return p
    return None


def show(player):
    """Show `player` if it has track info; otherwise leave the display alone,
    unless it was the player being shown, in which case fall back."""
    instance = player.props.player_instance
    info = track_info(player)
    if info is None:
        if instance == current:
            show_fallback(exclude=player)
        return
    if instance != current and player.props.status != 'Playing':
        shown = find_player(current) if current else None
        if shown is not None and shown.props.status == 'Playing':
            return  # don't let a paused/stopped player steal the display
    set_current(instance)
    icon = '󰏦' if player.props.status == 'Playing' else '󰐍'
    write(f'{icon} {html.escape(info, quote=False)}')


def show_fallback(exclude=None):
    """Show another player with track info (preferring one that is playing),
    or nothing if there is none."""
    candidates = [p for p in manager.props.players
                  if p is not exclude and track_info(p) is not None]
    if not candidates:
        set_current(None)
        write('')
        return
    playing = [p for p in candidates if p.props.status == 'Playing']
    show((playing or candidates)[0])


def on_play(player, _status, _manager):
    show(player)


def on_metadata(player, _metadata, _manager):
    show(player)


def on_name_appeared(_manager, name):
    init_player(name)


def on_player_vanished(_manager, player):
    if player.props.player_instance == current:
        show_fallback(exclude=player)


def init_player(name):
    player = Playerctl.Player.new_from_name(name)
    player.connect('playback-status', on_play, manager)
    player.connect('metadata', on_metadata, manager)
    manager.manage_player(player)
    show(player)


def signal_handler(_sig, _frame):
    write('')
    loop.quit()
    sys.exit(0)


manager.connect('name-appeared', on_name_appeared)
manager.connect('player-vanished', on_player_vanished)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

for name in manager.props.player_names:
    init_player(name)

loop.run()
