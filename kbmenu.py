#!/usr/bin/env python
import os
import re
import argparse

HOME = os.getenv('HOME')

childs_to_transform = list()
config = os.getenv('sxhkd_config', f'{HOME}/.config/sxhkd/sxhkdrc')
descriptor = os.getenv('descriptor', '# ')


def transform_block(block):
    indent = re.sub(r"\n[\t\s]+", "\n", block)
    trim_trailing_commands = re.sub(r"\\\n", "", indent)
    block_row = re.split('\\n', trim_trailing_commands, 2)

    return block_row


def get_raw_config(config, descriptor):
    keybinds = list()
    with open(config, "r") as cfg:
        data = cfg.read()

    return data


def parse_keybinds(config):
    block_regex = descriptor + r"[\w\s\(\),\-\/&]+\n[\w\s+\d{}_\-,]+\n[\s+\t]+[\w\s\-_$'\\~%{,!.\/\(\)};\"\n]+\n\n"
    eligible_blocks = re.findall(block_regex, config)

    keybinds = list()

    for block in eligible_blocks:
        transformed_line = transform_block(block)
        desc = transformed_line[0].strip(descriptor)
        cmd = re.sub(r'\n', '', transformed_line[2])
        unchained_lines = unchain_line(transformed_line)

        for line in unchained_lines:
            keybinds.append((desc, line, cmd))
    
    return keybinds


def unchain_line(row):
    chained_cmds = list()
    for child in row:
        chain = re.search(r'(?<={).*(?=})', child)
        if chain:
            #chain = re.sub(r'\s\+\s', '', chain.group(0))
            return unchain(chain.group(0), child)
            #chained_cmds.append(chain)
            #breakpoint()

    #if chained_cmds:
    #    return unchain(chained_cmds, row)
    #else:
    #    return row



def unchain(cmds, row):
    rows = list()
    for cmd in cmds.split(','):
        rows.append(delim_row(cmd, row))
    
    return rows


def delim_row(cmd, line):
    """ places a delimiter (+) on the row based on chain position (start of line, in the middle or at the end) """
    if '+' in cmd:
        cmd = re.sub(r'\s\+', '', cmd)

    pos_in_chain = ["^{.*}", "\s{.*}\s", "{.*}$"]
    delim_in_chain = [f"{cmd} +", f" {cmd} + ", f"{cmd}"]
    positions = zip(pos_in_chain, delim_in_chain)

    for pos, delim in positions: 
        match = re.search(fr'{pos}', line)
        if match:
            if '_' in cmd:  # check for wildcard
                return re.sub(fr'{pos}', ' ', line)
            return re.sub(fr'{pos}', fr'{delim}', line)


def main(config, descriptor):
    raw_cfg = get_raw_config(config, descriptor)
    binds = parse_keybinds(raw_cfg)
    for bind in binds:
        original_desc, keybind, original_cmd = bind
        print(f'{original_desc}\t{keybind}\t{original_cmd}'.expandtabs(30))

#        print(original_desc, bind, original_cmd)
    #format_output(keybinds)


if __name__ == '__main__':
    main(config, descriptor)