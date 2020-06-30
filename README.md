# keybind helper - standalone sxhkd configuration parser and keybind runner

kbhelper -- Easily discover and execute sxhkd keybindings, inspired by [https://github.com/Triagle/hotkey-helper](Hotkey-Helper)

[[https://ipfs.pics/ipfs/QmTdC3PnD1cEcqVo9cUjwY1PsYdVgRbwtypXTT5z8vC5cp]] gif

# What this is
kbhelper is a python utility that parses `sxhkdhrc`-files for all valid blocks to create a documented list associating
the description, the keybinding, and the action to execute. It can be used in conjunction with rofi/dmenu to have a fuzzy searchable cheatsheet of your configured keybinds.

# Installation
This program requires python 3.7 at minimum .

To set this up inside your $SHELL;

```sh
$ wget https://git.radivoj.se/popo/kbrmenu/src/branch/master/kbhelper.py -O ${HOME}/.local/bin/kbhelper.py
```

# sxhkdrc setup
In order to use the program's functionality, you need to tweak your
`sxhkdrc` to include special comments designed as documentation for
keybindings.

The special syntax for these documentation comments is any line
beginning with the variable `descriptor`, which can be defined with [--descriptor, -d] or the shell variable `descriptor='# '`, defaulting to `# ` if none is defined. Set these comments up above every keybinding
you wish to document.

```
# Example keybinding with documentation
# Quit bspwm
super + alt + Escape
    bspc quit
# This would show up in the formatted output as:
# super alt Escape - Quit bspwm
```

Additionally, `{}` can be used to unpack keychains mapping multiple segments
of description to keybind and action. If the preceeding description does not contain any keychains, all unpacked
lines will get the same description.

```
# Example of segmented documentation
# Move the current window {left,down,up,right}
super + {h,j,k,l}
  bspc node -s {west,south,north,east}
# This would expand in output as:
# super h                  - Move the current window left
# super j                  - Move the current window down
# super k                  - Move the current window up
# super l                  - Move the current window right
```

This allows for fast, compact documentation for keybindings of
arbitrary complexity.

# Usage
To use the program, run `kbhelper.py`. This will attempt to parse the configuration stored at the default location with the default descriptor, finally printing back to console (same as `--print`).

```
./kbhelper.py
```

Pass `--help` for a usage table:

```
usage: kbhelper.py [-h] [-c CONFIG] [-d DESCRIPTOR] [-e] [-ks KEYSTROKE] [-p]
                   [-r]

keybind helper - standalone sxhkd configuration parser and keystroke runner

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configurationfile location
  -d DESCRIPTOR, --descriptor DESCRIPTOR
                        comment descriptor
  -e, --exec            execute the passed shortcut
  -p, --print           Print fully unpacked keybind table
  -r, --raw             Print the raw configuration
```

By default, `kbhelper` will look for a sxhkdrc in `~/.config/sxhkd/sxhkdrc`, but can be overridden by passing a path to the [--config, -c] argument or the shell variable `sxhkd_config=$CFGPATH/sxhkdrc`,

```sh
python kbhelper.py -c path/to/sxhkdrc
```

This will print an unpacked table of possible keybinds. passing [--exec,-e] instead executes the action defined for that keystroke (if one was found)

```
super + question           - Show keybindings
super + i                  - Capture notes using org-mode
super + space              - Run a command
super + Return             - Spawn terminal
XF86AudioStop            - Open ncmpcpp
XF86AudioPrev            - Previous song
XF86AudioNext            - Next song
XF86AudioPlay            - Play mpd
XF86AudioRaiseVolume     - Raise Volume
XF86AudioLowerVolume     - Lower Volume
super + button1-3          - Focus window
button1                  - Focus window
super + ctrl + h             - Move window to the left monitor
super + ctrl + l             - Move window to the right monitor
super + bracketleft        - Go backward a desktop
super + bracketright       - Go forward a desktop
super + shift bracketleft  - Move window back a desktop
super + shift bracketright - Move window forward a desktop
super + h                  - Move the current window left
super + j                  - Move the current window down
super + k                  - Move the current window up
super + l                  - Move the current window right
super + m                  - Make window biggest
super + p                  - Open password manager
Print                    - Take a screenshot
super + apostrophe         - Swap last two window
super + grave              - Goto last window
super + Tab                - Goto last desktop
super + s                  - Make window float
super + f                  - Make window fullscreen
super + t                  - Make window tiled
super + b                  - Balance windows
super + w                  - Close window
super + shift w            - Show window list
super + Delete             - Suspend
super + alt Escape         - Quit bspwm
super + Escape             - Restart sxhkd
```

The output is tabulated so that the columns descriptions are neatly aligned and easy to interpret

This output can be piped to tools such as rofi or dmenu for further processing

```sh
# An example from my own config.
kbhelper.py | rofi -i -p "Hotkeys: "
```

Doing this with a program like rofi allows for powerful searching of
hotkeys on the system.

By running `python kbhelper.py --exec`, you can execute a command associated with a keybinding. For instance, from
the above configuration `super + w` is bound to closing a window. Therefore, calling:

```sh
kbhelper.py --exec "super + w"
```

Will close a window, as expected.

By combining the `--print` flag, and the `--exec` flag, you can create a relatively
powerful system for discovery and remembering your keybindings by
having `kbhelper.py --exec` run the output of the hotkeys searching script from
earlier.

```sh
# Adapted from the last shell script.
kbhelper.py -e "$(kbhelper.py -p | rofi -p Hotkeys: -i -dmenu | awk -F- '{print $1}')"
```