#!/bin/sh
# Power menu via fuzzel's dmenu mode -- replaces rofi-power-menu.
#
# Hibernate is only offered where logind's CanHibernate says "yes" (swap big
# enough for RAM plus resume= configured). The script is shared between
# machines and not all of them are set up for it.
#
# Each line is "label<TAB>extra search keywords". Only the label is shown and
# printed back (--with-nth/--accept-nth), but matching runs against both
# columns (--match-nth), so typing e.g. "poweroff" finds Shutdown.

entries=$(printf '%s\t%s\n' \
    "󰌾  Lock"     "" \
    "󰍃  Logout"   "" \
    "󰒲  Sleep"    "suspend")
if busctl call org.freedesktop.login1 /org/freedesktop/login1 \
    org.freedesktop.login1.Manager CanHibernate 2>/dev/null | grep -qx 's "yes"'; then
    entries=$(printf '%s\n%s\t%s' "$entries" "󰤄  Hibernate" "")
fi
entries=$(printf '%s\n%s\t%s\n%s\t%s' "$entries" \
    "󰜉  Reboot"   "restart" \
    "󰐥  Shutdown" "poweroff")

choice=$(printf '%s\n' "$entries" |
    fuzzel --dmenu --prompt="Power  " \
        --lines="$(printf '%s\n' "$entries" | wc -l)" \
        --with-nth=1 --accept-nth=1 --match-nth='{1} {2}')

case "$choice" in
*Lock)
    # No exec, so the notify-send fallback can run if hyprlock is missing or
    # fails to lock. Keep in sync with the Alt+L bind in hyprland.lua.
    pidof hyprlock >/dev/null || uwsm app -- hyprlock ||
        notify-send -u critical 'Lock failed' 'Is hyprlock installed?'
    ;;
*Logout)
    # Under uwsm the session is a systemd unit, so stop it properly; fall back
    # to Hyprland's own exit for the plain (non-uwsm) session.
    if uwsm check is-active >/dev/null 2>&1; then
        exec uwsm stop
    else
        exec hyprctl dispatch 'hl.dsp.exit()'
    fi
    ;;
*Sleep)      exec systemctl suspend ;;
*Hibernate) exec systemctl hibernate ;;
*Reboot)    exec systemctl reboot ;;
*Shutdown)  exec systemctl poweroff ;;
esac
