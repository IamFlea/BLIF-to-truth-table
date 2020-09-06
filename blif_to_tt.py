# This script changes Berkeley Logic Interchange Format (BLIF) to truth table 
# format which is easier for usage in Genetic Programming.
#
# Script was coded by Petr Dvoracek 2020

import re

# This constant protects overfilling RAM. Truth table requires `2**len(input)` 
# bytes. Thus truth table memory requirements grows exponentionally! Feel free 
# to change this value as you want. 
MAXIMAL_INPUTS = 22 


def parse_blif(filename):
    """Opens and parses blif file 

    Args:
        filename: The filename 

    Returns:
        inputs: List of named `.inputs` in the BLIF
        outputs: List of named `.outputs` in the BLIF
        list_of_names: List of `.names` containing inputs/output metadata and their truth table values
    """
    with open(filename, 'r') as fh:
        command = ''
        list_of_names = []
        names = []
        for line in fh:
            # Get rid of the comments
            if '#' in line:
                line, _ = line.split('#', 1)
            # Remove whitespaces from beginning and ending of the line
            line = line.strip()
            if not line:
                continue
            # Change whitespace logic
            #line.replace('\t', ' ')
            line = re.sub(r'\s+', ' ', line)

            # Concatenation of the lines
            if line.endswith('\\'):
                command += line[:-1] + ' '
                continue
            
            command += line
            if command.startswith('.'):
                if command.startswith('.inputs'):
                    inputs = command.split(' ')[1:]
                elif command.startswith('.outputs'):
                    outputs = command.split(' ')[1:]
                elif command.startswith('.names'):
                    if names:
                        list_of_names.append(names)
                    *input_names, output_name = command.split(' ')[1:]
                    names = [(tuple(input_names), output_name)]
                elif command.startswith('.model'):
                    pass
                elif command.startswith('.end'):
                    if names:
                        list_of_names.append(names)
                else:
                    print(command)
                    raise NotImplementedError
            else:
                names.append(tuple(line.split(' ')))
            command = ''
    return inputs, outputs, list_of_names

def change_row(row, input_idx_list, output_idx, required_inputs, required_output):
    """Changes values in a given row according to other args.

    Args:
        row: Given row
        input_idx_list: List of indexes of inputs
        output_idx: Index of the output
        required_inputs: Required values that are compared to indexes of the inputs
        required_output: The output which is rewritten.
    Returns:
        row: Changed row (string)
    """
    change = True
    for input_idx, req_val in zip(input_idx_list, required_inputs):
        change = change and bool(req_val == '-' or req_val == row[input_idx])
    if change:
        return row[:output_idx] + str(required_output) + row[output_idx+1:]
    return row


def get_tt_from_blif(filename):
    """Gets truth table from a given file

    Args:
        filename: Name of the file with blif format.
    Retruns:
        tt: Truth table - List of strings in format
            `{VALS_in} : {VALS_out}\n` where VALS ∈ {0,1}
            For each input combination, we gives required output 
            Params are separated by a colon symbol. 
        inputs: List of input names
        outputs: List of output names
    """
    inputs, outputs, list_of_names = parse_blif(filename)
    if len(inputs) > MAXIMAL_INPUTS:
        raise MemoryError("Too many inputs for circuit.")
    # Create first part of the truth table (tt) for all input combinations
    tt = [bin(val)[2:].zfill(len(inputs)) for val in range(2**len(inputs))]
    # Get indexes of names
    name_to_index = {}
    for idx, name in enumerate(inputs):
        name_to_index[name] = idx
    for idx, el in enumerate(list_of_names, len(inputs)):
        name_to_index[el[0][1]] = idx
    # Fill output vals with a default value
    for el in list_of_names:
        ins, outs = el[0]
        ins = [name_to_index[i] for i in ins]
        outs = name_to_index[outs]
        el[0] = [ins, outs]
        
        default = int(el[1][-1])
        reverse = int(not default)
        bit = reverse
        for idx, val in enumerate(tt):
            tt[idx] += str(bit)

    # For each output in `name` replace the output val in the truth table.
    # `name` values do not neccessary need to be ordered! Thus we have
    # a list `checked`
    checked = list(range(len(inputs)))
    for _ in range(len(checked), len(tt[0])):
        # Select an unchecked `name`
        for name in list_of_names:
            if name[0][1] in checked:
                continue
            found_unchecked = True
            for input in name[0][0]:
                if input not in checked:
                    found_unchecked = False
                    break
            if found_unchecked:
                break
        # We should always find an unchecked item
        assert(found_unchecked)
        input_idx_list, output_idx = name[0]
        #print(f"Procession output on idx {output_idx}")
        for val in name[1:]:
            for i, row in enumerate(tt):
                tt[i] = (change_row(row, input_idx_list, output_idx, *val))
        checked.append(output_idx)

    # Remove not necessary primary outputs. 
    for idx, row in enumerate(tt):
        req_output = ''
        for output in outputs:
            req_output += str(row[name_to_index[output]])
        tt[idx] = f'{row[:len(inputs)]} : {req_output}'

    return tt, inputs, outputs

def blif_file_to_tt_file(input_filename, output_filename):
    """Creates a truth table file from a given blif file.

    Args: 
        input_filename:  Required blif file
        output_filename: Created file with Truth table. 
    """
    truth_table, inputs, outputs = get_tt_from_blif(input_filename)
    
    with open(output_filename, 'w') as fh:
        fh.write(f'# File: {output_filename}\n')
        fh.write(f'# Total inputs: {len(inputs)}\n')
        fh.write(f'# Total outputs: {len(outputs)}\n')
        fh.write(f'# Input names: {inputs}\n')
        fh.write(f'# Output names: {outputs}\n')
        fh.write('\n'.join(truth_table))


if __name__ == '__main__':
    """Useage:

    ./blif_to_tt.py {BLIF_FILENAME} {OUTPUT_FILENAME}
        Creates truth table from given BLIF_FILENAME into OUTPUT_FILENAME 

    ./blif_to_tt.py {BLIF_FILENAME}
        Creates truth table from given BLIF_FILENAME. The output filename is 
        the same as BLIF_FILENAME with the suffix `.txt`.

    ./blif_to_tt.py
        Creates truth tables from `.blif` suffixes in the current directory.
    """
    
    # Lazy importing cuz of script might be used elsewhere
    import sys
    import os
    
    if len(sys.argv) > 2:
        blif_file = sys.argv[1]
        tt_file = sys.argv[2]
        blif_file_to_tt_file(blif_file, tt_file)
    elif len(sys.argv) > 1:
        blif_file = sys.argv[1]
        blif_file_to_tt_file(blif_file, f'{blif_file}.txt')
    else:
        # Get filenames
        for (dirpath, dirnames, filenames) in os.walk('.'):
            break

        has_blif_suffix = lambda filaname: filaname.endswith('.blif')
        for input_filename in filter(has_blif_suffix, filenames):
            output_filename = f'{input_filename[:-5]}.txt'
            print(output_filename)
            try:
                blif_file_to_tt_file(input_filename, output_filename)
            except Exception as e: 
                print(e)
                print('\nParsing the next file.\n')
        print('Done')

    