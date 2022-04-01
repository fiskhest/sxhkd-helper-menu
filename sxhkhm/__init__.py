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


    def _unchain_lines(self, lines, count_uh=count_uh):
        """ take a transformed block of lines (from ._transform_block), unpacking any keychains, finally
        returning a list containing any unpacked or original lines of keybinds """
        any_chain = False
        return_lines = list()
        lines[0] = lines[0].strip(self.descr)
        lines[2] = lines[2].rstrip()

        count_uh += 1
        r1_lines = list()
        for line in lines:
            if not re.search(r'{.*?}', line):
                r1_lines.append([])
            else:
                cr = re.findall(r'(?<={).*?(?=})', line)
                for chain in cr:
                    if re.search(r'\d-\d', chain):
                        r2_lines = list()
                        all_digits = re.findall(r'\d', chain)
                        for ichain in all_digits:
                            r2_lines.append(int(ichain))
                        r2_lines.sort()
                        r3_lines = list()
                        try:
                            for index in range(r2_lines[0], r2_lines[-1] + 1):
                                r3_lines.append(index)
                            r1_lines.append(r3_lines)
                        except:
                            breakpoint()
                    elif ',' in chain:
                        r1_lines.append([i.strip() for i in chain.split(',')])

        out_list = list()
        count_hits = 0
        for outer_index, line in enumerate(lines):
            print(outer_index, line)
            ri = re.findall(r'{.*?}', line)
            to_out = list()
            longest = len(max(r1_lines, key=len))

            if ri:
                # print(f'{outer_index} contained chain')
                for inner_index, inline in enumerate(ri):
                    if outer_index == 0:
                        outer_index_multiplier = 0 + inner_index
                    else:
                        outer_index_multiplier = outer_index * len(ri)
                    if '+' in inline:
                        inline = re.sub('\+', '\\+', inline)

                    try:
                        key = r1_lines[outer_index_multiplier][inner_index]
                    except IndexError as err:
                        print(err)
                        breakpoint()

                    if key == '_':
                        key = ''
                    line = re.sub(inline, str(key), line)

                to_out.append([line])

                for final_out in to_out:
                    for k in range(1, longest+1):
                        do_return = re.sub(r'\d', str(k), final_out[0])
                        out_list.append([do_return])

            else:

                print(f'{outer_index} did not contain chain')
                for _ in range(1, longest):
                    out_list.append([line])

        return_lines = out_list

        if any_chain and len(return_lines) == 1:
            exit("A keychain denoting multiple segments was specified for the keybind, but no matching cmdchain exists. Fix your sxhkdrc")

        # ensure all sublists in return_lines have the same length by filling the sublist with a copy of the first item 
        #maxlen = 0
        #for index, line in enumerate(return_lines):
        #    if len(line) >= maxlen:
        #        maxlen = len(line)

        #    else:
        #        for _ in range(0, maxlen-1):
        #            return_lines[index].append(return_lines[index][0]) 

        breakpoint()
        return return_lines


    def _unchain_multiple(self, chains, line, index):
        return_keys = list()
        line_no_chains = line
        return_lines = list()
        for chain in chains:
            return_keys.append(self._unchain(chain, line, index))
            #return_keys.append(self._unchain(chain, line, index))
            # for sub_chain in chain_expansions:
            #     #print(chain_index, sub_chain)
            #     regex_to_parse = f"({chain})"
            #     r = re.compile("\{" + regex_to_parse + "\}")
            #     print(re.sub(r, sub_chain, line_no_chains))
        #print(chains)
        # expanding multiple chains in a line, need to zip both expansions
        #for expansions in return_keys:
        #    regex_to_parse = f"{expansions}"
        #    r = re.compile("\{" + regex_to_parse + "\}")
        #    for expansion in expansions:
        #        line_no_chains = re.sub(r, expansion, line_no_chains)
        #        print(line_no_chains)
        #        breakpoint()
        #        #return_lines.append(expansion + line_no_chains)
        cp = list(product(*return_keys))

        for p1, p2 in cp:
            r = re.sub(r'{.*?}', p1, line, count=1)
            r = re.sub(r'{.*?}', p2, r, count=1)
            return_lines.append(r)
        #breakpoint()
        return return_lines


    def _unchain(self, keys, line, index):
        """ takes a list of keys or commands, the original line and the line index (in the block), returning a new list of unpacked keybinds """
        lines = list()

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
            #if keys == '_,shift + ':
            #    breakpoint()
            comma_keys = copy(keys)
            comma_keys = re.sub(r'^[\w\d]+-[\w\d]+,', '', comma_keys)
            for key in comma_keys.split(','):
                lines.append(self._delim_segment(key, line, index))

        #rc = re.compile('.*[{}].*')
        #for line in lines:
        #    if rc.match(line):
        #        print("match")

        return lines


    def _delim_segment(self, key, line, index):
        """ places a delimiter (+, or '') at the previous keychain segment position (start of line, in the middle, end of line OR nothing if the line only contains keychains) """

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
                            r'(?<=\S){.*}(?=\S)',
                            r'((?<=})\{.*{key}.*\})',
                            r'(?<=}){.*?}|{.*?}(?={))']

            delim_in_chain = [f"{key} + ",
                              f"{key} ",
                              f"{key} + ",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key}",
                              f"{key} + ",
                              f"{key}",
                              f"{key}",
                              f"{key} + ",
                              f"",
                              f"{key}",
                              f"{key}",
                              f"{key}"]

        positions = zip(pos_in_chain, delim_in_chain)
        # search keychain for possible delimiter position and transform the line to make sense
        for pos, delim in positions: 
            # just return nothing if we struck a wildcard
            if key == '_':
                return re.sub(f'{pos}', '', line)

            match = re.search(pos, line, re.M)
            if match:
                # bugfix chains containing one or more spaces: {key1, key2}, strip the leading space(s),
                #   and anywhere two or more spaces is seen, replace by one single space
                delim = delim.lstrip()
                delim = re.sub(r'\s\s+', ' ', delim)
                delim = re.sub(r'\s\+\s\+\s', ' + ', delim)
                return re.sub(rf'{pos}', rf'{delim}', line, count=1)
            else:
                print(f"{key}: no match")
                print(f"{pos}: {line}")

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
