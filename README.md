# HotKey Helper  - standalone sxhkd configuration parser and keybind runner

[![.github/workflows/main.yml](https://github.com/fiskhest/sxhkd-helper-menu/workflows/.github/workflows/main.yml/badge.svg)](https://github.com/fiskhest/sxhkd-helper-menu/actions?query=workflow%3A.github%2Fworkflows%2Fmain.yml)
[![AUR package](https://img.shields.io/aur/version/sxhkhm-git)](https://aur.archlinux.org/packages/sxhkhm-git/)
[![PyPI package](https://img.shields.io/pypi/v/sxhkhm?color=green)](https://pypi.org/project/sxhkhm/)

sxhkd HotKey helper/menu -- Easily discover and execute sxhkd keybindings, inspired by [Hotkey-Helper](https://github.com/Triagle/hotkey-helper)

![sxhkhm usage](showcase-sxhkhm.gif)

# What this is
hkhelper is a python utility that parses `sxhkdhrc`-files for valid blocks of keybinds to create a documented list
associating the description, the keybinding and the action to execute. It can be used in conjunction with rofi/dmenu to have a fuzzy searchable cheatsheet of your configured keybinds.

This program was written using Python 3.8, but should work for 3.6 and greater.

# Installation
# AUR
```sh
sudo aura -A sxhkhm-git
```

# PyPI
```sh
pip install --user sxhkhm
```

# manual install from git repo
To set this up inside your `$SHELL` (make sure that `${HOME}/.local/bin/` is located somewhere within your `$PATH`, or alternatively specify a directory that is in your `$PATH` after -O: `wget [...] -O <directory>/hkhelper.py`):

```sh
$ mkdir -p ${HOME}/.local/bin/
$ wget https://raw.githubusercontent.com/fiskhest/sxhkd-helper-menu/master/sxhkhm/__init__.py -O ${HOME}/.local/bin/hkhelper.py
```

You can also clone the repo and use the bundled install script:

```sh
$ cd /tmp/
$ git clone https://github.com/fiskhest/sxhkd-helper-menu/ && cd sxhkd-helper-menu/
$ make install

# or do what the makefile does manually:
$ python3 -m pip install -f requirements.txt
$ python3 setup.py install
```

# sxhkdrc setup
In order to use the program's functionality, you need to tweak your
`sxhkdrc` to include special comments designed as documentation for
keybindings.

The special syntax for these documentation comments is any line beginning with the value of the variable `descriptor`, which can
be defined with [`--descriptor`, `-d`] or the shell variable `export descriptor='# '`, defaulting to `# ` if none is defined. Set these comments up above every keybinding you wish to document.

```
# Example keybinding with documentation
# Quit bspwm
super + alt + Escape
    bspc quit

# This would show up in the formatted output as:
Quit bspwm                                        super + alt + Escape                              bspc quit
```

Additionally, `{}` can be used to unpack keychains mapping multiple segments of description to keybind and action.
**If the preceeding description does not contain any keychains, all unpacked lines will get the same description.**

```
# Example of segmented documentation
# Move the current window {left,down,up,right}
super + {h,j,k,l}
  bspc node -s {west,south,north,east}

# This would expand in output as:
Move the current window left                      super + h                                         bspc node -s west
Move the current window down                      super + j                                         bspc node -s south
Move the current window up                        super + k                                         bspc node -s north
Move the current window right                     super + l                                         bspc node -s east

# Example of a keychain containing a range
# Focus workspace {1-6,9}
super + {1-6,9}
    bspc desktop -f '^{1-6,9}'

# This would expand in output as:
Focus workspace 1                                 super + 1                                         bspc desktop -f '^1'
Focus workspace 2                                 super + 2                                         bspc desktop -f '^2'
Focus workspace 3                                 super + 3                                         bspc desktop -f '^3'
Focus workspace 4                                 super + 4                                         bspc desktop -f '^4'
Focus workspace 5                                 super + 5                                         bspc desktop -f '^5'
Focus workspace 6                                 super + 6                                         bspc desktop -f '^6'
Focus workspace 9                                 super + 9                                         bspc desktop -f '^9'
```

This allows for fast, compact documentation for keybindings of arbitrary complexity.

# Usage
To use the program, run `hkhelper.py`. This will attempt to parse the configuration stored at the default location with the default descriptor, finally printing back to console (same as `--print`).

```
python hkhelper.py
```

Pass `--help` for a usage table:

```
usage: hkhelper.py [-h] [-f FILE] [-d DESCRIPTOR] [-e EXEC] [-p] [-m] [-r]

hotkey helper - standalone sxhkd configuration parser and keystroke runner

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to configuration file
  -d DESCRIPTOR, --descriptor DESCRIPTOR
                        comment descriptor
  -e EXEC, --exec EXEC  execute the passed shortcut
  -p, --print           Print fully unpacked keybind table
  -m, --markdown        Print fully unpacked keybind table in markdown format(for cheatsheets)
  -r, --raw             Print the raw configuration

```

By default, `hkhelper` will look for sxhkdrc in `~/.config/sxhkd/sxhkdrc`, but can be overridden by passing a path to the [`--file`, `-f`] argument or the shell variable `sxhkd_config=$CFGPATH/sxhkdrc`,

```sh
python hkhelper.py -f path/to/sxhkdrc
```

This will print an unpacked table of possible keybinds. passing [--exec,-e] instead executes the action defined for that keystroke (if one was found)

```
Split horizontal                                  super + period                                    bspc node -p east
Split vertical                                    super + minus                                     bspc node -p south
Split cancelation                                 super + comma                                     bspc node -p cancel
Preselect the ratio                               super + ctrl + 1                                  bspc node -o 0.1
Preselect the ratio                               super + ctrl + 2                                  bspc node -o 0.2
Preselect the ratio                               super + ctrl + 3                                  bspc node -o 0.3
Preselect the ratio                               super + ctrl + 4                                  bspc node -o 0.4
Preselect the ratio                               super + ctrl + 5                                  bspc node -o 0.5
Preselect the ratio                               super + ctrl + 6                                  bspc node -o 0.6
Preselect the ratio                               super + ctrl + 7                                  bspc node -o 0.7
Preselect the ratio                               super + ctrl + 8                                  bspc node -o 0.8
Preselect the ratio                               super + ctrl + 9                                  bspc node -o 0.9
Bspwm mode pseudotiled                            super + p                                         bspc node -t
Bspwm mode tiled                                  super + t                                         bspc node -t tiled
Set the node flags marked                         super + ctrl + m                                  bspc node -g marked
Set the node flags locked                         super + ctrl + x                                  bspc node -g locked
Set the node flags sticky                         super + ctrl + y                                  bspc node -g sticky
Set the node flags private                        super + ctrl + z                                  bspc node -g private
Move or swap node to the left (desktop/leaf)      super + shift + h                                 if ! bspc node -s west.local; then bspc node -d prev -f ; fi
Move or swap node to the right (desktop/leaf)     super + shift + l                                 if ! bspc node -s east.local; then bspc node -d next -f ; fi
```

The output is tabulated so that the columns descriptions are neatly aligned and easy to interpret.

This output can be piped to tools such as fzf or rofi for further processing, enabling powerful and easy searching of hotkeys on the system.

By running `python hkhelper.py --exec`, you can execute a command associated with a keybinding. For instance, from
the above configuration `super + w` is bound to closing a window. Therefore, executing the following will close a window, as expected:

```sh
python hkhelper.py --exec "super + w"
```

By combining the `--print` flag, and the `--exec` flag, you can create a relatively
powerful system for discovery and remembering your keybindings by
having `hkhelper.py --exec` run the output of the hotkeys searching script from
earlier. A simple bash helper script `sxhkhmenu` is bundled with this repo, essentially doing the following:

```sh
python hkhelper.py -e "$(python hkhelper.py -p | rofi -p Hotkeys -i -dmenu -width 75 | grep -Po '(?<=\s\s)(?=\S).*(?=\b\s\s)(?!$)')"
```

If you wish to use the bundled `sxhkhmenu`, installation is as simple as:

```sh
# skip this if you used any installation method
$ wget https://raw.githubusercontent.com/fiskhest/sxhkhm/master/sxhkhmenu -O ${HOME}/.local/bin/sxhkhmenu
```

```sh
# skip this if you used any installation method or wish to use the defaults (rofi with some sorting and dmenu mode). Otherwise, configure the below according to your own wishes
$ vi ~/.config/sxhkhm.ini
---
opt_args=''
menuhelper='fzf'
```

create a bind in your sxhkd-configuration:
```sh
# Display keybind rofi menu
super + b
    sxhkhmenu
    # if you installed manually by wgetting the files:
    # ${HOME}/.local/bin/sxhkhmenu
```

# Print to markdown
An option to parse and print the result as markdown for exporting to cheatsheet/blogs/dev/null is available using the `[--markdown,-m]` argument. To try and categorise, and abusing the fact that most configurations of sxhkd are categorised (and /or formated) with comments, this function parses all keybinds and looks for the immediate-most related ancestor, iterating over the categories and prints back any keybinds related to that category. One may control how the parsing of ancestors is performed by passing `[--category_descriptor,-cd]` (default: `### `)

Example:
```sh
# original sxhkdrc
### -- BSPWM | Preselect -- ###

# Preselect {horizontal,vertical,cancel} split
super + {period,minus,comma}
    bspc node -p {east,south,cancel}

### -- System Control | Audio & Brightness -- ###

# {raise,lower} brightness
XF86MonBrightness{Up,Down}
    backlight{-up,-down}

----------------------------------

# unpacked example:
# BSPWM | Preselect
* `super + period`: Preselect horizontal split - `bspc node -p east`
* `super + minus`: Preselect vertical split - `bspc node -p south`
* `super + comma`: Preselect cancel split - `bspc node -p cancel`

# System Control | Audio & Brightness
* `XF86MonBrightnessUp`: raise brightness - `backlight-up`
* `XF86MonBrightnessDown`: lower brightness - `backlight-down`
```

# release workflow
run `make release VERSION=x.y.z`, trying to follow semver.

# misc
There are sure to be some bugs and use cases that wasn't foreseeable. PR's and issues are gladly appreciated!

Alternative: [dmenu-hotkey](https://github.com/maledorak/dmenu-hotkeys)

Todo:
- fix the horrible regex matching...
- cleaner readme/installation instructions
