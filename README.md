# Linux Dots

These are the dot/config files that I use.

Files and folders in the `src` directory map to `$HOME`

- Examples:
    - `src/.zshrc` should be symlinked to `$HOME/.zshrc`
    - `src/.config/sway` should be symlinked to `$HOME/.config/sway`

## Install

> WARNING: Running install.sh will overwrite/delete your current configs.
> Run with care.

In Terminal Run:
```bash
./install.sh
```

## Uninstall

> WARNING: Running uninstall.sh will delete your current configs.
> Run with care.

In Terminal Run:
```bash
./uninstall.sh
```

## Dependencies

Note: [Xorg-Wayland](https://archlinux.org/packages/extra/x86_64/xorg-xwayland/) is required for most of these applications to work.

- Terminal
    - [Alacritty](https://github.com/alacritty/alacritty)
    - Font: [Source Code Pro](https://github.com/adobe-fonts/source-code-pro)
- Menu
    - [Rofi](https://github.com/davatorium/rofi)
        - [Rofi Power Menu](https://github.com/jluttine/rofi-power-menu)
        - [Rofi Emoji](https://github.com/Mange/rofi-emoji)
        - [Rofi Calculator](https://github.com/svenstaro/rofi-calc)
    
