#!/usr/bin/env bash
# Change the default sink volume and show a single dunst popup with a
# progress bar. The stack tag makes every call replace the previous popup
# instead of stacking new ones, and each replace restarts the timeout, so the
# popup stays while keys are pressed and hides ~1.5s after the last one.
set -euo pipefail

sink=@DEFAULT_AUDIO_SINK@
case "${1:-}" in
    # Changing the volume also unmutes, like the old `amixer ... unmute` binds.
    up)   wpctl set-mute "$sink" 0; wpctl set-volume -l 1.0 "$sink" 2%+ ;;   # -l 1.0 caps at 100%
    down) wpctl set-mute "$sink" 0; wpctl set-volume "$sink" 2%- ;;
    mute) wpctl set-mute "$sink" toggle ;;
    *)    echo "usage: $0 up|down|mute" >&2; exit 2 ;;
esac

# wpctl prints e.g. "Volume: 0.42" or "Volume: 0.42 [MUTED]"
read -r _ vol muted < <(wpctl get-volume "$sink")
pct=$(awk -v v="$vol" 'BEGIN { printf "%d", v * 100 + 0.5 }')

if [[ -n "${muted:-}" ]]; then
    text="Muted"
else
    text="${pct}%"
fi

# dunst's title is plain text in its default "Monospace 8" font, so the
# percentage is right-aligned by padding with spaces. 44 columns fills the
# 300px-wide popup without wrapping (measured from a screenshot: ~6.4px per
# column at this monitor's 1.25 scale; 45+ wraps the percentage to line 2).
# Change this if the dunst width or font ever changes.
cols=44
title=$(printf "Volume%*s" $(( cols - 6 )) "$text")

notify-send -a volume-osd -u low -t 1500 \
    -h string:x-dunst-stack-tag:volume-osd \
    -h "int:value:$pct" \
    "$title"
