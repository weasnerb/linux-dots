#!/bin/sh
# Clipboard history picker: cliphist + fuzzel's dmenu mode (Super+V).
# History is recorded by cliphist.service (`wl-paste --watch cliphist store`).
#
# `cliphist list` prints "<id><TAB><preview>". Only the preview is shown and
# matched (--with-nth/--match-nth), but the whole line is printed back, since
# `cliphist decode` needs the id.
#
# Bail out on Escape/empty selection: piping nothing into `wl-copy` would
# clear the current clipboard.
sel=$(cliphist list |
    fuzzel --dmenu --prompt="Clipboard  " --with-nth=2 --match-nth=2) || exit 0
[ -n "$sel" ] || exit 0

printf '%s\n' "$sel" | cliphist decode | wl-copy
