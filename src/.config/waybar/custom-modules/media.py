#!/usr/bin/env python3
"""Now-playing module for waybar (custom/media), for any MPRIS player.

Shows whichever player most recently changed track or play state. That
player's instance name (e.g. `vlc.instance123`, unique even when two copies of
one app are open) is written to PLAYER_FILE so the module's click actions
control the player it is showing (`playerctl -p "$(cat ...)"` in the waybar
config) rather than whatever playerctl would pick on its own. When a player closes,
the module falls back to another running player instead of going blank.
"""
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
    try:
        if name:
            with open(PLAYER_FILE, 'w') as f:
                f.write(name)
        elif os.path.exists(PLAYER_FILE):
            os.remove(PLAYER_FILE)
    except OSError:
        pass


def show(player):
    metadata = player.props.metadata
    if player.props.player_name == 'spotify' and \
            'mpris:trackid' in metadata.keys() and \
            ':ad:' in metadata['mpris:trackid']:
        track_info = 'AD PLAYING'
    elif player.get_artist() and player.get_title():
        track_info = '{artist} - {title}'.format(artist=player.get_artist(),
                                                 title=player.get_title())
    else:
        set_current(player.props.player_instance)
        write('')
        return

    set_current(player.props.player_instance)
    icon = '󰏦' if player.props.status == 'Playing' else '󰐍'
    write(f'{icon} {track_info}')


def show_fallback():
    """Show a remaining player (preferring one that is playing), or nothing."""
    players = manager.props.players
    if not players:
        set_current(None)
        write('')
        return
    playing = [p for p in players if p.props.status == 'Playing']
    show((playing or players)[0])


def on_play(player, _status, _manager):
    show(player)


def on_metadata(player, _metadata, _manager):
    show(player)


def on_name_appeared(_manager, name):
    init_player(name)


def on_player_vanished(_manager, _player):
    show_fallback()


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
