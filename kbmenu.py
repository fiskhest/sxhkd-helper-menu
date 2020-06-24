#!/usr/bin/env python
import os
import re

HOME=os.getenv('HOME')

keybinds = list()
config = os.getenv('shxkd_config', f'{HOME}/.config/sxhkd/sxhkdrc')
descriptor = os.getenv('descriptor', '# ')

def assemble_output(data):
    breakpoint()
    exit()


def parse_cfg(config, descriptor):
    with open(config, "r") as cfg:
        data = cfg.read()

    block_regex = r"# [\w\s\(\),\-\/&]+\n[\w\s+\d{}_\-,]+\n[\s+\t]+[\w\s\-_$'\\~%{,!.\/\(\)};\"]+\n\n"
    eligible_blocks = re.findall(block_regex, data)

    for block in eligible_blocks:
        substitute = re.sub(r"\n[\t\s]+", "\n", block)
        block_rows = re.split('\n', substitute)
        keybinds.append(tuple((list(filter(None, block_rows)))))


def format_output(keybinds):
    for desc, keybind, cmd in keybinds:
        print(f'{desc} # {keybind} # {cmd}')


def split_chains(keybinds):
    chainbinds = list()
    for block in keybinds:
        check_block(block)


def check_block(block):
    childs_to_transform = list()
    for child in block:
        if re.search(r'{.*}', child):
            childs_to_transform.append(block)
            break

    breakpoint()


def main(config, descriptor):
    parse_cfg(config, descriptor)
    split_chains(keybinds)
    format_output(keybinds)


if __name__ == '__main__':
    main(config, descriptor)