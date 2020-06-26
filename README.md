# kbrmenu - keybind rofi menu

kbrmenu -- Easily document, and discover sxhkd keybindings, heavily inspired by [https://github.com/Triagle/hotkey-helper](Hotkey-Helper)

[[https://ipfs.pics/ipfs/QmTdC3PnD1cEcqVo9cUjwY1PsYdVgRbwtypXTT5z8vC5cp]] gif

* What this is
kbrmenu is a python utility that parses `sxhkdhrc`-files taking the hotkeys and some specially formatting comments to create a
documented list associating keybindings with their actions.
With the latest updates intelligent parsing is added, allowing
hotkeys to be executed by string
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
beginning with the shell variable `descriptor`, defaulting to `# `. Set these comments up above every keybinding
you wish to document.

#+BEGIN_EXAMPLE
# Example keybinding with documentation
# Quit bspwm
super + alt + Escape
    bspc quit
# This would show up in the formatted output as:
# super alt Escape - Quit bspwm
#+END_EXAMPLE

Additionally, ={}= can be used to denote lists mapping multiple segments
of documentation to multiple hotkey segments at once

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
To use the program, run =hotkeys=.

#+BEGIN_SRC shell
hotkeys
#+END_SRC

This will print the usage for the program

#+BEGIN_EXAMPLE
Usage: hotkeys [options...]

 -e, --execute=HOTKEY     Execute command for HOTKEY
 -p, --print              Print hotkeys
 -f, --file=NAME          Parse file NAME
 -h, --help               Display this text

#+END_EXAMPLE

By default, =hotkeys= looks in the default sxhkd config folder
(~/.config/sxhkd/sxhkdrc) for the sxhkdrc file. You can also pass a path argument, for the location of your =.sxhkdrc=
file.

#+BEGIN_SRC shell
hotkeys -f /path/to/.sxhkdrc
#+END_SRC

However this will do nothing either, you need to pass an action
argument to the program, currently -p or -e to tell hotkeys what to do
with the file.

- -p :: Print a formatted list of hotkeys.
- -e :: Execute a hotkey string (e.g "super w").

Upon running =hotkeys -p=, you should get a formatted list of hotkeys
printed to the terminal, something like

#+BEGIN_EXAMPLE
[~/repos/scm/hotkey-helper] ->>  hotkeys -p
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
