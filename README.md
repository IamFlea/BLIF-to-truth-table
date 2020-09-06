# BLIF-to-truth-table
Parses BLIF (Berkeley Logic Interchange Format) to a truth table which is easier for parsing in Genetic Programming Algorithms. You can find lots of digital circuit benchmark files here: https://ddd.fit.cvut.cz/prj/Benchmarks/

## Example of an output file with truthtable
- The comments in the file begins with `#` character. 
- The input and output values in the truth table are separated with colon symbol `:`.

An example of the output is:
```
# File: cm42a.txt
# Total inputs: 4
# Total outputs: 10
# Input names: ['a', 'b', 'c', 'd']
# Output names: ['e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
0000 : 0111111111
0001 : 1111111101
0010 : 1111011111
0011 : 1111111111
0100 : 1101111111
0101 : 1111111111
0110 : 1111110111
0111 : 1111111111
1000 : 1011111111
1001 : 1111111110
1010 : 1111101111
1011 : 1111111111
1100 : 1110111111
1101 : 1111111111
1110 : 1111111011
1111 : 1111111111
```

## Usage
`./blif_to_tt.py {BLIF_FILENAME} {OUTPUT_FILENAME}`
Creates truth table from given BLIF_FILENAME into OUTPUT_FILENAME 

`./blif_to_tt.py {BLIF_FILENAME}`
Creates truth table from given BLIF_FILENAME. The output filename is the same as BLIF_FILENAME with the suffix `.txt`.

`./blif_to_tt.py`
Creates truth tables from `.blif` suffixes in the current directory.

## License
MIT
