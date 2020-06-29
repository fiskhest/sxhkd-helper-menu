# keybind helper - standalone sxhkd configuration parser and keybind runner

kbhelper -- Easily discover and execute sxhkd keybindings, inspired by [https://github.com/Triagle/hotkey-helper](Hotkey-Helper)

[[https://ipfs.pics/ipfs/QmTdC3PnD1cEcqVo9cUjwY1PsYdVgRbwtypXTT5z8vC5cp]] gif

* What this is
kbhelper.py is a python utility that parses `sxhkdhrc`-files for all valid blocks to create a documented list 
associating the description, the keybinding, and the action to execute.

* Installation
This program requires python 3.7 at minimum .

To set this up inside your $SHELL;

```sh
$ sudo wget ... -O /usr/sbin/local/
```

* .sxhkdrc Setup
In order to use the program's functionality, you need to tweak your
`sxhkdrc` to include special comments designed as documentation for
keybindings.

The special syntax for these documentation comments is any line
beginning with the variable `descriptor`, which can be defined with [--descriptor, -d] or the shell variable `sxhkd_config=CFGPATH/sxhkdrc`, defaulting to `# ` if none is defined. Set these comments up above every keybinding
you wish to document.

#+BEGIN_EXAMPLE
# Example keybinding with documentation
# Quit bspwm
super + alt + Escape
    bspc quit
# This would show up in the formatted output as:
# super alt Escape - Quit bspwm
#+END_EXAMPLE

Additionally, ={}= can be used to unpack keychains mapping multiple segments
of description to keybind and action.

#+BEGIN_EXAMPLE
# Example of segmented documentation
# ;; Move the current window {left,down,up,right}
super + {h,j,k,l}
  bspc node -s {west,south,north,east}
# This would expand in output as:
# super h                  - Move the current window left
# super j                  - Move the current window down
# super k                  - Move the current window up
# super l                  - Move the current window right
#+END_EXAMPLE

This allows for fast, compact documentation for keybindings of
arbitrary complexity.
* Usage
To use the program, run `kbhelper.py`

#+BEGIN_SRC shell
kbhelper.py
#+END_SRC

This will print the usage for the program

#+BEGIN_EXAMPLE
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
  -ks KEYSTROKE, --keystroke KEYSTROKE
                        when using --exec, also define a keystroke for which
                        command is to be executed
  -p, --print           Print fully unpacked keybind table
  -r, --raw             Print the raw configuration
#+END_EXAMPLE

By default, =kbhelper= looks in the default sxhkd config folder
(~/.config/sxhkd/sxhkdrc) for the sxhkdrc file. You can also pass a path with the [--config,-c] argument to the location of your =sxhkdrc=
file.

#+BEGIN_SRC shell
python kbhelper.py -c /path/to/sxhkdrc
#+END_SRC

This will print an unpacked table of possible keybinds. passing [--exec,-e] and [--keystroke,-ks] instead executes the action defined for that keystroke (if one was found)

Upon running =python kbhelper.py -c $sxhkdrc_config_path=, you should get a formatted list of keybinds printed to 
the terminal, something like

#+BEGIN_EXAMPLE
python kbhelper.py
super question           - Show keybindings
super i                  - Capture notes using org-mode
super space              - Run a command
super Return             - Spawn terminal
XF86AudioStop            - Open ncmpcpp
XF86AudioPrev            - Previous song
XF86AudioNext            - Next song
XF86AudioPlay            - Play mpd
XF86AudioRaiseVolume     - Raise Volume
XF86AudioLowerVolume     - Lower Volume
super button1-3          - Focus window
button1                  - Focus window
super ctrl h             - Move window to the left monitor
super ctrl l             - Move window to the right monitor
super bracketleft        - Go backward a desktop
super bracketright       - Go forward a desktop
super shift bracketleft  - Move window back a desktop
super shift bracketright - Move window forward a desktop
super h                  - Move the current window left
super j                  - Move the current window down
super k                  - Move the current window up
super l                  - Move the current window right
super m                  - Make window biggest
super p                  - Open password manager
Print                    - Take a screenshot
super apostrophe         - Swap last two window
super grave              - Goto last window
super Tab                - Goto last desktop
super s                  - Make window float
super f                  - Make window fullscreen
super t                  - Make window tiled
super b                  - Balance windows
super w                  - Close window
super shift w            - Show window list
super Delete             - Suspend
super alt Escape         - Quit bspwm
super Escape             - Restart sxhkd
#+END_EXAMPLE

The output is tabulated (thanks to the fmt library), so all the
descriptions are neatly aligned and easy on the eyes.

This output can be piped to the likes of dmenu, or rofi.

#+BEGIN_SRC shell
# An example from my own config.
hotkeys -p | rofi -i -p "Hotkeys: "
#+END_SRC

Doing this with a program like rofi allows for powerful searching of
hotkeys on the system.

By running =hotkeys -e=, you can execute a command associated with a
keybinding. For instance, from the above configuration =super w= is
bound to closing a window. 
Thus calling:

#+BEGIN_SRC shell
hotkeys -e "super w"
#+END_SRC

Will close a window, as expected.

By combining the -p flag, and the -e flag, you can create a relatively
powerful system for discovery and remembering your keybindings by
having =hotkeys -e= run the output of the hotkeys searching script from
earlier.

#+BEGIN_SRC shell
# Adapted from the last shell script.
hotkeys -e "$(hotkeys -p | rofi -p Hotkeys: -i -dmenu | awk -F- '{print $1}')"
#+END_SRC

The example gif shows how this script works
