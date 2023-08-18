# Linux Dots

These are the dot/config files that I use.

Files and folders in the `src` directory map to `$HOME`

- Examples:
    - `src/.zshrc` should be symlinked to `$HOME/.zshrc`
    - `src/.config/sway` should be symlinked to `$HOME/.config/sway`

## Install

In Terminal Run:
```bash
./installer.py install
```

## Uninstall

In Terminal Run:
```bash
./installer.py uninstall
```

## Dependencies

> Currently not up to date, look into each config to see what may be required.

Note: [Xorg-Wayland](https://archlinux.org/packages/extra/x86_64/xorg-xwayland/) is required for most of these applications to work.

- Terminal
    - [Alacritty](https://github.com/alacritty/alacritty)
    - Font: [Source Code Pro](https://github.com/adobe-fonts/source-code-pro)
- Menu
    - [Rofi](https://github.com/davatorium/rofi)
        - [Rofi Power Menu](https://github.com/jluttine/rofi-power-menu)
        - [Rofi Emoji](https://github.com/Mange/rofi-emoji)
        - [Rofi Calculator](https://github.com/svenstaro/rofi-calc)
    
