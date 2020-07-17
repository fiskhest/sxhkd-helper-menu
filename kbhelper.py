#!/usr/bin/env python3
import os
import re
import argparse
import sys
from itertools import zip_longest

HOME = os.getenv('HOME')
config_file_location = os.getenv('sxhkd_config', f'{HOME}/.config/sxhkd/sxhkdrc')
descriptor = os.getenv('descriptor', '# ')

parser = argparse.ArgumentParser(description='keybind helper - standalone sxhkd configuration parser and keystroke runner')
parser.add_argument('-f', '--file', default=f'{config_file_location}', help='path to configuration file')
parser.add_argument('-d', '--descriptor', default=f'{descriptor}', help='comment descriptor')
parser.add_argument('-e', '--exec', default=False, help='execute the passed shortcut')
parser.add_argument('-p', '--print', default='true', action='store_true', help='Print fully unpacked keybind table')
parser.add_argument('-m', '--markdown', action='store_true', help='Print fully unpacked keybind table in markdown format(for cheatsheets)')
parser.add_argument('-r', '--raw', action='store_true', help='Print the raw configuration')


class sxhkd_helper:
    """ instance helper args and functions """
    def __init__(self, loc, descr):
        self.location = loc
        self.descr = descr
        self.raw_config = self._get_raw_config()
        self.keybinds = [bind for bind in self._parse_keybinds()]


    def _transform_block(self, block):
        """ transform an eligible block of keybind into a list of three elements which is returned for further
        processing.
        elem 1: comment/declaration of keybind usage
        elem 2: assigned keystrokes
        elem 3: command to execute """
        indent = re.sub(r"\n[\t\s]+", "\n", block)
        trim_trailing_commands = re.sub(r"\\\n", "", indent)
        block_lines = re.split(r'\n', trim_trailing_commands, 2)

        return block_lines


    def _get_raw_config(self):
        """ load configuration from the location defined upon instantiation of class """
        with open(self.location, "r") as cfg:
            data = cfg.read()
        
        self._raw_config = data
        return data


    def _parse_keybinds(self):
        """ take the raw configuration from config and parses all eligible blocks, unchaining keychains and returning
        a list of unpacked commands """
        block_regex = self.descr + r"[\w\s\(\),\-\/&{}_\-,;:]+\n[\w\s+\d{}_\-,;:]+\n[\s+\t]+[\w\s\-_$'\\~%{,!.\/\(\)};\"\n\^]+\n+"
        eligible_blocks = re.findall(block_regex, self._get_raw_config())
        unchained_lines = list()
        return_keybinds = list()
        for block in eligible_blocks:
            lines = self._transform_block(block)
            unchained_lines = self._unchain_lines(lines)
            to_be_returned = list(zip_longest(*unchained_lines, fillvalue=f'{unchained_lines[0][0]}'))
            for line in to_be_returned:
                return_keybinds.append(line)

        return return_keybinds


    def _unchain_lines(self, lines):
        """ take a transformed block of lines (from ._transform_block), unpacking any keychains, finally
        returning a list containing any unpacked or original lines of keybinds """
        any_chain = False
        return_lines = list()
        lines[0] = lines[0].strip(self.descr)
        lines[2] = lines[2].rstrip()

        for index, line in enumerate(lines):
            chain = re.search(r'(?<={).*(?=})', line)
            if chain:
                any_chain = True
                return_lines.append(self._unchain(chain.group(0), line, index))
            else:
                return_lines.append([line])

        if any_chain and len(return_lines) == 1:
            exit("A keychain denoting multiple segments was specified for the keybind, but no matching cmdchain exists. Fix your sxhkdrc")

        # ensure all sublists in return_lines have the same length by filling the sublist with a copy of the first item 
        maxlen = 0
        for index, line in enumerate(return_lines):
            if len(line) >= maxlen:
                maxlen = len(line)

            else:
                for _ in range(0, maxlen-1):
                    return_lines[index].append(return_lines[index][0]) 

        return return_lines


    def _unchain(self, keys, line, index):
        """ takes a list of keys or commands, the original line and the line index (in the block), returning a new list of unpacked keybinds """
        lines = list()

        keys = re.sub(r'\s', '', keys)

        if ',' in keys:
            for key in keys.split(','):
                lines.append(self._delim_segment(key, line, index))
        elif '-' in keys:
            key = keys.split('-')
            for index in range(int(key[0]), int(key[-1])+1):
                lines.append(self._delim_segment(str(index), line, index))

        return lines


    def _delim_segment(self, key, line, index):
        """ places a delimiter (+, or '') at the previous keychain segment position (start of line, in the middle, end of line OR nothing if the line only contains keychains) """
        if '+' in key:
            key = re.sub(r'\+', '', key)

        # for the first line (the comment), we don't want to put any delimiters in, no matter where in the line the chain is.
        if index == 0:
            pos_in_chain = [r'{.*}']
            delim_in_chain = [f"{key}"]

        else:
            pos_in_chain = [r'{.*}\s(?!=\+)(?=\w)',
                            r'{.*}\s+(?=\+)',
                            r'.*{_}.*',
                            r'{\d+-\d+}',
                            r'(?<=\s){.*}(?=\s)',
                            r'{.*}$',
                            r'^{.*}$',
                            r'(?<=[\s\w]){\b(?!\+).*\b}(?=[\s\w])',
                            r'(?<=[\s\w]){.*(?=\+).*}(?=[\s\w])']

            delim_in_chain = [f"{key} + ",
                              f"{key} ",
                              f"{key} + ",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key} + "]

        positions = zip(pos_in_chain, delim_in_chain)
        for pos, delim in positions: 
            match = re.search(pos, line, re.M)
            if match:
                if '_' in key:  # check for wildcard
                    return re.sub(f'{pos}', '', line)
                return re.sub(f'{pos}', f'{delim}', line)

        return line
    
def print_keybinds(config):
    """ print all parsed and unpacked keybinds to console """
    for bind in config.keybinds:
        original_desc, keybind, original_cmd = bind
        print(f'{original_desc}\t{keybind}\t{original_cmd}'.expandtabs(50))


def print_markdown(config):
    """ print all parsed and unpacked keybinds to console in a markdown format """
    for bind in config.keybinds:
        original_desc, keybind, original_cmd = bind
        print(f'`{original_desc}`\t`{keybind}`\t`{original_cmd}`'.expandtabs(55))


def execute_cmd(config, keystroke):
    """ run command passed with --exec 'modifier + <character>' """
    import subprocess
    for keybind in config.keybinds:
        # loop through all possible keybinds, finally executing a process if we matched
        cmd = keybind[2]
        keybind = keybind[1]
        if keystroke == keybind:
            subprocess.run([f'{cmd}'], shell=True)

def main(args):
    config = sxhkd_helper(args.file, args.descriptor)

    # only execute if --exec was passed with an actual value
    if bool(args.exec) == True:
        execute_cmd(config, args.exec)

    elif args.raw:
        print(f'Config location: {config.location}')
        print(config.raw_config)

    elif args.markdown:
        print_markdown(config)

    elif args.print:
        print_keybinds(config)
        

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)