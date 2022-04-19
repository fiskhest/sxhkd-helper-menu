#!/usr/bin/env python3
import os
import re
import argparse
import sys
from itertools import zip_longest, product
from copy import copy

HOME = os.getenv('HOME')
config_file_location = os.getenv('sxhkd_config', f'{HOME}/.config/sxhkd/sxhkdrc')
descriptor = os.getenv('descriptor', '# ')
category_descriptor = os.getenv('category_descriptor', '### ')


class sxhkd_helper:
    """ instance helper args and functions """
    count_uh = 0
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


    def _unpack_chain(self, chain, line):
        """ take an unformatted line and the left-most found chain, iterate upon any chain and return a list
            containing ranges of alphanumerics, comma-separated values found inside chain """
        out = list()

        # no chains found to expand
        if not re.search(r'{.*?}', chain):
            out.append(chain)
        else:
            srch = re.search(r'(?<={).*?(?=})', chain)
            if srch:
                if re.search(r'\d+', chain):
                    srch_lines = list()
                    single_digits = [int(i) for i in re.findall(r'\d+', chain)]
                    for ichain in single_digits:
                        srch_lines.append(int(ichain))

                srch_range_d = re.search(r'\d+-\d+', chain)
                srch_range_a = re.search(r'(?<!\w)[a-z]-[a-z](?!\w)', chain)

                if srch_range_d:
                    range_digits = list()
                    range_steps = [int(i) for i in srch_range_d.group(0).split('-')]
                    for index in range(range_steps[0], range_steps[1] + 1):
                        range_digits.append(index)
                    missing_digits = set(single_digits) - set(range_digits)
                    to_consider = range_digits + list(missing_digits)
                    for cl in to_consider:
                        out.append(cl)

                elif srch_range_a:
                    chain_copy = copy(chain)
                    chain_copy = re.sub(r'(?<=\w)[\,\w]+', '', chain_copy)
                    chain_copy = re.sub(r'[{}]', '', chain_copy)
                    chain_copy = chain_copy.split('-')
                    character_range = map(chr, range(ord(chain_copy[0]), ord(chain_copy[-1])+1))
                    for range_index in character_range:
                        out.append(range_index)
                    out.sort()
                else:
                    if ',' in srch.group(0):
                        split_lines = [i.lstrip() for i in srch.group(0).split(',') if not re.search(r'(\d+-\d+|(?<!\w)[a-z]-[a-z](?!\w))', i)]
                        if split_lines:
                            for sl in split_lines:
                                if sl == '_':
                                    out.append('')
                                else:
                                    out.append(sl)
                    else:
                        out = [i.lstrip() for i in srch.group(0).split(',')]
                        return out

        return out


    def _unpack_chain_lines(self, chains, line):
        """ takes a list of chains found in the line and the complete line, iterates over chains and unpacks each one
            adding a copy of the tranformed line for each iteration that is finally returned as a complete list
        """
        out = list()
        possible_expansions = list()

        out_line = ''
        for chain in chains:
            possible_expansions.append(self._unpack_chain(chain,line))

        all_possible_expansions = product(*possible_expansions)
        for exp in all_possible_expansions:
            exp_line = line
            for i, le in enumerate(exp):
                exp_line = re.sub(r'{.*?}', str(le), exp_line, count=1)
                exp_line = re.sub(r'\s{2,}', ' ', exp_line)
                if (i==len(exp)-1):
                    out.append(exp_line.lstrip())
        return out


    def _unchain_lines(self, lines):
        """ take a transformed block of lines (from ._transform_block), unpacking any keychains, finally
        returning a list containing any unpacked or original lines of keybinds """
        any_chain = False
        lines[0] = lines[0].strip(self.descr)
        lines[2] = lines[2].rstrip()

        to_out = list()
        for outer_index, line in enumerate(lines):
            ri = re.findall(r'{.*?}', line)
            lines_to_out = list()
            lines_to_out.append(ri)
            if ri:
                to_out.append(self._unpack_chain_lines(ri, line))
            else:
                to_out.append([line])


        return_lines = to_out

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


def print_keybinds(config, column_width):
    """ print all parsed and unpacked keybinds to console """
    widths = [max(len(word) for word in col)
              for col in zip_longest(*config.keybinds, fillvalue='')]

    for bind in config.keybinds:
        # left align but leave three spaces for max length word in col
        # inspo: https://rosettacode.org/wiki/Align_columns#Python
        print(' '.join(f"{wrd:<{wdth+2}}" for wdth, wrd in zip(widths, bind)))


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
