#!/usr/bin/env python3
import os
import re
import argparse
import sys
from itertools import zip_longest
from copy import copy

HOME = os.getenv('HOME')
config_file_location = os.getenv('sxhkd_config', f'{HOME}/.config/sxhkd/sxhkdrc')
descriptor = os.getenv('descriptor', '# ')
category_descriptor = os.getenv('category_descriptor', '### ')


class sxhkd_helper:
    """ instance helper args and functions """
    def __init__(self, loc, descr, category_descr):
        self.location = loc
        self.descr = descr
        self.category_descr = category_descr
        self.raw_config = self._get_raw_config()
        self.keybinds = self._get_keybinds()
        self.categories = self._get_categories()

    def _get_categories(self):
        categories = list()
        for parsed_keybind in self._parse_keybinds():
            for category in parsed_keybind.keys():
                categories.append(category)

        categories = [*{*categories}]

        return categories


    def _get_keybinds(self):
        keybinds = list()
        for parsed_keybind in self._parse_keybinds():
            for bind in parsed_keybind.values():
                keybinds.append(bind)

        return keybinds


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
        block_regex = r"^" + self.descr + r"[\w\s\(\),\-\/&{}_\-,;:\%]+\n[\w\s+\d{}_\-,;:]+\n[\s+\t]+[\w\$()\~\-,{}/;]+.*"
        eligible_blocks = re.findall(block_regex, self._get_raw_config(), flags=re.M)
        unchained_lines = list()
        return_keybinds = list()
        for block in eligible_blocks:
            lines = self._transform_block(block)
            category = self._get_keybind_category(lines[0])  # use the description to find the first preceeding header
            unchained_lines = self._unchain_lines(lines)
            to_be_returned = list(zip_longest(*unchained_lines, fillvalue=f'{unchained_lines[0][0]}'))
            for line in to_be_returned:
                return_keybinds.append({f'{category}': line})

        return return_keybinds


    def _get_keybind_category(self, key_desc):
        """ take a description as formatted by _transform_block, search for and return the first preceeding header (string defined by -cd) """
        query = "(?<=\\n)({}.*?)\\n(?=.*{})".format(re.escape(self.category_descr), re.escape(key_desc))
        category_search = re.findall(query, self._get_raw_config(), flags=re.S)
        if category_search:
            # strip away any special chars in case the category is formatted weirdly for some reason
            # we allow & and | since they aren't generally great characters for padding something in ascii art/column-filling...
            result = re.sub('[^A-Za-z0-9\s&|]+', '', category_search[-1]).strip()
            return result
        else:
            return 'misc'


    def _unchain_lines(self, lines):
        """ take a transformed block of lines (from ._transform_block), unpacking any keychains, finally
        returning a list containing any unpacked or original lines of keybinds """
        any_chain = False
        return_lines = list()
        lines[0] = lines[0].strip(self.descr)
        lines[2] = lines[2].rstrip()

        for index, line in enumerate(lines):
            chain = re.search(r'(?<={).*?(?=})', line)
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

        keys = re.sub(r'\s\+\s', '', keys)

        copy_keys = copy(keys)
        if re.search(r'^[a-zA-Z]-[a-zA-Z][,$]', keys):
            copy_keys = re.sub(r'(?<=\w)[\,\w]+', '', copy_keys)
            copy_keys = copy_keys.split('-')
            character_range = map(chr, range(ord(copy_keys[0]), ord(copy_keys[-1])+1))
            for range_index in character_range:
                lines.append(self._delim_segment(range_index, line, index))

        elif re.search(r'\d+-\d+', keys):
            copy_keys = re.match(r'\d+-\d+', keys)[0].split('-')
            start_of_range = int(copy_keys[0])
            end_of_range = int(re.sub(r',.*', '', copy_keys[-1]))
            for range_index in range(start_of_range, end_of_range + 1):
                lines.append(self._delim_segment(str(range_index), line, index))

        if ',' in keys:
            comma_keys = copy(keys)
            comma_keys = re.sub(r'^[\w\d]+-[\w\d]+,', '', comma_keys)
            for key in comma_keys.split(','):
                lines.append(self._delim_segment(key, line, index))

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
            # TODO: yeah, so... a thing happened...
            # Clean this PoS up and make this more intelligent than the current implementation...
            pos_in_chain = [r'{.*}\s(?!=\+)(?=\w)',
                            r'{.*}\s+(?=\+)',
                            r'.*{_}.*',
                            r'{\d+-\d+}',
                            r'(?<=\s){.*}(?=\s)',
                            r'{.*\+\s}',
                            r'{.*?}(?!={.*})',
                            r'{.*?}$',
                            r'{(?<=_).*(?=\+)}',
                            r'{_,.*(?=\+).*}',
                            r'^{.*}$',
                            r'{(?<=[\s\w]){\b(?!\+).*\b}(?=[\s\w])}',
                            r'{(?<=[\s\w]){.*(?=\+).*}(?=[\s\w])}',
                            r'{\b_}',
                            r'(?<=\S){.*}(?=\S)']

            delim_in_chain = [f"{key} + ",
                              f"{key} ",
                              f"{key} + ",
                              f"{key}",
                              f"{key}",
                              f"{key} + ",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key} + ",
                              f"{key}",
                              f"{key}",
                              f"{key} + ",
                              f"",
                              f"{key}"]

        positions = zip(pos_in_chain, delim_in_chain)
        # search keychain for possible delimiter position and transform the line to make sense
        for pos, delim in positions: 
            match = re.search(pos, line, re.M)
            if match:
                # bugfix chains containing one or more spaces: {key1, key2}, strip the leading space(s),
                #   and anywhere two or more spaces is seen, replace by one single space
                delim = delim.lstrip()
                delim = re.sub(r'\s\s+', ' ', delim)
                # just return nothing if we struck a wildcard
                if key == '_':
                    return re.sub(f'{pos}', '', line)
                return re.sub(rf'{pos}', rf'{delim}', line, count=1)

        # if no special rules was found to match, fallback to return the key sent into the script
        return key
    

def print_keybinds(config, column_width):
    """ print all parsed and unpacked keybinds to console """
    widths = [max(len(word) for word in col)
              for col in zip_longest(*config.keybinds, fillvalue='')]

    for bind in config.keybinds:
        # left align but leave two spaces for max length word in col
        # inspo: https://rosettacode.org/wiki/Align_columns#Python
        print(' '.join(f"{wrd:<{wdth+1}}" for wdth, wrd in zip(widths, bind)))


def print_markdown(config):
    """ print all parsed and unpacked keybinds to console in a markdown format """

    for category in config.categories:
        print(f'# {category}')
        for bind in config._parse_keybinds():
            if category in bind:
                original_desc, keybind, original_cmd = bind[category]
                print(f'* `{keybind}`: {original_desc} - `{original_cmd}`')

        print()


def execute_cmd(config, keystroke):
    """ run command passed with --exec 'modifier + <character>' """
    import subprocess
    for keybind in config.keybinds:
        # loop through all possible keybinds, finally executing a process if we matched
        cmd = keybind[2]
        keybind = keybind[1]
        if keystroke == keybind:
            subprocess.run([f'{cmd}'], shell=True)


def main():
    parser = argparse.ArgumentParser(description='hotkey helper - standalone sxhkd configuration parser and keystroke runner')
    parser.add_argument('-f', '--file', default=f'{config_file_location}', help='path to configuration file')
    parser.add_argument('-d', '--descriptor', default=f'{descriptor}', help='comment descriptor')
    parser.add_argument('-cd', '--category_descriptor', default=f'{category_descriptor}', help='category descriptor')
    parser.add_argument('-e', '--exec', default=False, help='execute command bound to passed shortcut')
    parser.add_argument('-p', '--print', default='true', action='store_true', help='Print fully unpacked keybind table')
    parser.add_argument('-t', '--tabexpand', default=50, help='set amount of cells to pad columns by')
    parser.add_argument('-m', '--markdown', action='store_true', help='Print fully unpacked keybind table in markdown format(for cheatsheets)')
    parser.add_argument('-r', '--raw', action='store_true', help='Print raw configuration')
    args = parser.parse_args()
    column_width = int(args.tabexpand)

    config = sxhkd_helper(args.file, args.descriptor, args.category_descriptor)

    # only execute if --exec was passed with an actual value
    if bool(args.exec) == True:
        execute_cmd(config, args.exec)

    elif args.raw:
        print(f'Config location: {config.location}')
        print(config.raw_config)

    elif args.markdown:
        print_markdown(config)

    elif args.print:
        print_keybinds(config, column_width=column_width)
        

if __name__ == '__main__':
    main()
