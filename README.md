# Linux Dots

These are the dot/config files that I use on Arch Linux with Hyprland (Wayland), run as a [uwsm](https://github.com/Vladimir-csp/uwsm) session started from the [ly](https://github.com/fairyglade/ly) login manager.

Files and folders in the `src` directory map to `$HOME`:

- `src/.zshrc` is symlinked to `$HOME/.zshrc`
- `src/.config/hypr` is symlinked to `$HOME/.config/hypr`
- `src/.config/systemd/user/...` files are symlinked into `$HOME/.config/systemd/user/` **one file at a time**, because that directory also holds systemd's own enablement links

## Install

From the repo root:

```bash
./installer.py install          # asks about each config
./installer.py install --all    # installs everything without asking
```

Anything already at a target path is moved to `<name>.bak` first.

Then, on each machine:

1. **Pick the per-machine Hyprland config** (monitors, workspaces, brightness):
   ```bash
   cd ~/.config/hypr && ln -s ./brian-arch ./current-computer   # or ./brian-desktop-arch
   ```
2. **Generate the color scheme.** Hyprland and waybar still start without it (Hyprland with fallback colors and a warning), but **fuzzel refuses to open** until `~/.cache/wal/colors-fuzzel.ini` exists:
   ```bash
   wal -i <wallpaper>   # first time; afterwards `wal -R` restores the last one
   ```
3. **Enable the session services:**
   ```bash
   systemctl --user enable import-gsettings.service hyprpolkitagent.service waybar.service hyprpaper.service
   ```
4. **Laptops: make TLP always switch profiles with the charger.** Plugging in should go to performance and unplugging to balanced, with a profile picked from the bar holding until the next plug/unplug. That's TLP's "auto" mode; its default "smart" mode skips the switch after a manual pick. `/etc/tlp.conf` isn't in this repo, so set it by hand:
   ```bash
   sudo sed -i 's/^#\?TLP_AUTO_SWITCH=.*/TLP_AUTO_SWITCH=1/' /etc/tlp.conf && sudo tlp start
   ```
5. **Log in with the "Hyprland (uwsm-managed)" session in ly.** The plain "Hyprland" session also works: `hyprland.lua` then starts waybar, hyprpaper and the polkit agent itself.

To restart the bar after editing it, use `systemctl --user restart waybar` (or `reload` for style/config-only changes). Don't kill it and relaunch it by hand: the service brings back its own copy too, and you end up with two bars.

## Uninstall

```bash
./installer.py uninstall        # or --all
```

This removes the symlinks the installer made and restores any `.bak` backups.

## What's in here

| Path (under `src/.config/`) | What |
|---|---|
| `hypr/hyprland.lua` | Shared Hyprland config (Lua `hl.*` API): binds, appearance, animations |
| `hypr/brian-arch/`, `hypr/brian-desktop-arch/` | Per-machine settings, loaded through the `current-computer` symlink |
| `hypr/scripts/` | `volume.sh` (volume keys + popup), `powermenu.sh` (Super+Shift+P), `makemywall.sh` (pad an image out to a wallpaper) |
| `waybar/` | Bar config, styles and custom modules (see below) |
| `fuzzel/` | App launcher (Super+D) and power menu |
| `systemd/user/`, `uwsm/env` | Session services and environment for uwsm |
| `wal/templates/` | pywal templates for GTK3/waybar, fuzzel, hyprpaper and Hyprland colors |
| `alacritty/`, `nvim/`, `../.zshrc` | Terminal, editor and shell |

### Waybar modules

- **Performance** (`custom-modules/performance.py`): the icon shows the power profile and turns red when CPU or RAM is at 80% or more. Hover for per-core CPU and RAM use. Left-click cycles power-saver → balanced → performance; right-click opens htop. On battery it warns at 15% and 5% and switches to power saver. Plugging in switches to performance (TLP does this with `TLP_AUTO_SWITCH=1`, see Install step 4; the module also undoes its own low-battery switch).
- **Media** (`custom-modules/media.py`): now playing for any MPRIS player. Click to play/pause, right-click for the next track.
- **Tailscale** (`custom-modules/tailscale.py`): connection status. Click to toggle, right-click for a menu, middle-click to copy this machine's Tailscale IP.
- Built-in modules: workspaces, window title, network (click opens `nmtui`), volume and mic (percentage on hover), battery, tray, and a combined date/time clock (click for the long form, hover for a calendar).

## Dependencies

Arch package names. Packages marked *(AUR)* are not in the official repos.

- **Session:** `hyprland`, `uwsm`, `ly`, `xorg-xwayland`, `hyprpaper`, `hyprpolkitagent`, `xdg-desktop-portal-hyprland`, `xdg-desktop-portal-gtk`
- **Bar:** `waybar`, `python-gobject`, `playerctl`, `htop`, `networkmanager` (for `nmtui`), `tailscale` (optional)
- **Power profiles:** `tlp` and `tlp-pd` (or anything else providing the power-profiles-daemon D-Bus API)
- **Launcher, notifications, lock:** `fuzzel`, `dunst`, `libnotify`, `swaylock-effects` *(AUR)*
- **Audio:** `pipewire`, `pipewire-pulse` (PulseAudio compatibility for apps and pulsemixer), `wireplumber` (`wpctl`), `pulsemixer`
- **Utilities:** `brightnessctl`, `grim`, `slurp` and `jq` (screenshots), `wl-clipboard`, `imagemagick` (`makemywall.sh`)
- **Colors:** `python-pywal` *(AUR)*
- **Fonts:** `ttf-material-design-icons-webfont` *(AUR; bar and popup icons)*, `ttf-meslo-nerd-font-powerlevel10k` *(AUR; terminal and bar text)*, `adobe-source-code-pro-fonts` (launcher)
- **Terminal and shell:** `alacritty`, `zsh`, `zsh-theme-powerlevel10k`, `zsh-syntax-highlighting`, `zsh-autosuggestions`, `zsh-history-substring-search`, `nvm`
- **Editor:** `neovim`
