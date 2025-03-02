
# Mini-Project 

This repository contains all code related to Mini-Project-1 

## Folder Structure :

This folder contains three folders.

- `PY_FILES` contains main `parser.py` file and supporting `functions.py` file
- `TEST_FILES` contains files required for testing. This folder will have .bench and .lib files for which
        the parser was initially developed.
- `EXPERIMENTAL` contains prototype code that was developed to test if developed logic works, 
        and if logic works, transfer required functions into `functions.py` file in `PY_FILES` folder.


## Running the parser :

The parser has three command line arguments :
- `--read_ckt` which requires a `.bench` file to create a netlist
- `--slews --read_nldm` which requires a `.lib` file to extract Output slew 
- `--delays --read_nldm` which requires a `.lib` file to extract the delay values for each cell.

## Usage 

This parser has to be run using `python3.7` and above.

Given a `.lib` and a `.bench` file , you may run the parser using :

```python
>>> python3.7 parser.py --read_ckt (path to `.bench` file here)

>>> python3.7 parser.py --slews --read_nldm (path to .lib file here)    # Read Output Slew table from each cell

>>> python3.7 parser.py --delays --read_nldm (path to .lib file here)   # Read Delay table for each cell 

```



### NOTE :
- `.bench` files can be found in [ISCAS85](https://www.pld.ttu.ee/~maksim/benchmarks/iscas85/bench/) dataset