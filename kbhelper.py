#!/usr/bin/env python
import os
import re
import argparse
import sys

HOME = os.getenv('HOME')
config_location = os.getenv('sxhkd_config', f'{HOME}/.config/sxhkd/sxhkdrc')
descriptor = os.getenv('descriptor', '# ')

parser = argparse.ArgumentParser(description='keybind helper - standalone sxhkd configuration parser and keybind runner')
parser.add_argument('-c', '--config', default=f'{config_location}', help='Configurationfile location')
parser.add_argument('-d', '--descriptor', default=f'{descriptor}', help='comment descriptor')
parser.add_argument('-e', '--exec', action='store_true', help='execute the passed shortcut')
parser.add_argument('-ks', '--keystroke', default='', help='if using --exec, also define a keystroke for which command is to be executed')
parser.add_argument('-p', '--print', default='true', action='store_true', help='Print fully unpacked keybind table ')
parser.add_argument('-r', '--raw', action='store_true', help='Print the raw configuration')


class sxhkd_helper:
    """ instance helper args and functions """
    def __init__(self, loc, descr):
        self.location = loc
        self.descr = descr
        self.raw_config = self._get_raw_config()
        self.keybinds = self._parse_keybinds()


    def _transform_block(self, block):
        """ transform an eligible block of keybind into a list of three elements which is returned for further 
        processing.
        elem 1: comment/declaration of keybind usage
        elem 2: assigned keystrokes
        elem 3: command to execute """
        indent = re.sub(r"\n[\t\s]+", "\n", block)
        trim_trailing_commands = re.sub(r"\\\n", "", indent)
        block_row = re.split(r'\n', trim_trailing_commands, 2)

        return block_row


    def _get_raw_config(self):
        """ load configuration from the location defined upon instantiation of class """
        with open(self.location, "r") as cfg:
            data = cfg.read()
        
        self._raw_config = data
        return data


    def _parse_keybinds(self):
        """ take the raw configuration from config and parses all eligible blocks, unchaining keychains and returning
        a list of unpacked commands """
        keybinds = list()
        block_regex = self.descr + r"[\w\s\(\),\-\/&]+\n[\w\s+\d{}_\-,;]+\n[\s+\t]+[\w\s\-_$'\\~%{,!.\/\(\)};\"\n]+\n\n"
        eligible_blocks = re.findall(block_regex, self._get_raw_config())

        for block in eligible_blocks:
            lines = self._transform_block(block)
            desc = lines[0].strip(self.descr)
            cmd = lines[2].rstrip()
            unchained_lines = self._unchain_line(lines)

            if not re.search(r'(?<={).*(?=})', cmd):
                exit("A keychain was specified for the keybind, but no matching cmdchain exists. Fix your sxhkdrc")
            for index, line in enumerate(unchained_lines):
                keybinds.append((desc, line, self._unchain_line([cmd])[index]))
            
        return keybinds


    def _unchain_line(self, lines):
        """ take a transformed block of lines (from ._transform_block), unpacking any keychains, finally
        returning any unpacked or original lines of keybinds """
        any_chain = False
        for line in lines:
            chain = re.search(r'(?<={).*(?=})', line)
            if chain:
                any_chain = True
                return self._unchain(chain.group(0), line)

        if not any_chain:
            no_chain_return = list()
            no_chain_return.append(lines[1])

        return no_chain_return

    def _unchain(self, keys, row):
        """ takes a list of commands and the original row and returns a new list of unpacked rows """
        rows = list()

        keys = re.sub(r'\s', '', keys)

        for key in keys.split(','):
            rows.append(self._delim_row(key, row))
        return rows


    def _delim_row(self, key, line):
        """ places a delimiter (+, or '') on the row based on chain position (start of line, in the middle, end of line OR nothing if the line only contains keychains) """
        if '+' in key:
            key = re.sub(r'\+', '', key)

        pos_in_chain = [r'^{.*}.', r'\s{.*}\s', r'{.*}$', r'^{.*}$']
        delim_in_chain = [f"{key} + ", f" {key} + ", f"{key}", f"{key}"]
        positions = zip(pos_in_chain, delim_in_chain)

        for pos, delim in positions: 
            match = re.search(pos, line)
            if match:
                if '_' in key:  # check for wildcard
                    return re.sub(f'{pos}', ' ', line)
                return re.sub(f'{pos}', fr'{delim}', line)
    
def print_keybinds(config):
    """ print all parsed and unpacked keybinds to console """
    for bind in config.keybinds:
        original_desc, keybind, original_cmd = bind
        print(f'{original_desc}\t{keybind}\t{original_cmd}'.expandtabs(30))

def execute_cmd(config, keystroke):
    """ run command passed with --exec --keystroke 'modifier + <character>' """
    import subprocess
    if len(keystroke) == 0:
        exit("No keystroke defined. Pass argument --keystroke 'modifier + <character>' to execute")

    for keybind in config.keybinds:
        # loop through all possible keybinds, finally executing a process if we matched
        cmd = keybind[2]
        keybind = keybind[1]
        if keystroke == keybind:
            subprocess.run([f'{cmd}'], shell=True)

def main(args):
    config = sxhkd_helper(args.config, args.descriptor)

    if args.exec:
        execute_cmd(config, args.keystroke)

    elif args.raw:
        # print(config.location)
        print(config.raw_config)

    elif args.print:
        print_keybinds(config)
        

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)