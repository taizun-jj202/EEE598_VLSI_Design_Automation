# Mini-Project Phase-2

## Table of Contents:
1. [File Descriptions](#file-description-)
2. [Evaluation Environment Setup](#evaluation-environment-setup)
    - 2.1 [Setup Python venv](#setup-python-venv)
3. [How to run](#how-to-run)
4. [Expected Output](#expected-output-)

## File Description :

- `main_sta.py` is file that is to be run for STA analysis.
- `main_sta_functions.py` file is a supporting file that contains all functions used to parse and execute STA analysis in `main_sta.py`


## Evaluation Environment Setup 

**`NOTE`** : 
- This parser has been developed with `python3.7`. Please ensure python version 3.7 is installed on the system before running the parser file.
- `main_sta.py` will create a text file containing the required result . 
    - For e.g, if we perform STA analysis on `c17.bench` file using the command `python3.7 main_sta.py --read_ckt c17.bench --read_nldm sample_NLDM.lib`, then output will be in a file called `ckt_traversal_c17.txt`


### Setup python venv 

Use the following commands to setup python virtual env for parser using the following commands

```python
python3.7 -m venv EEE598_V 
source EEE598_V/bin/activate.csh
pip3 install -r requirements.txt
python3.7 parser.py <arguments> <file>

```

### How to run 

To run Static Timing Analysis on a given .bench file and a given .lib file, do the following :

1. Ensure the following files are in same folder after python environment has been setup using the commands shown above :
    - `main_sta.py`
    - `main_sta_functions.py`

2. Use the following command to run the static timing analysis :
    - `python3.7 main_sta.py --read_ckt c17.bench --read_nldm sample_NLDM.lib`


#### **NOTE** : parser will save a text file containing the result



### Expected Output :

Output shown here is for `c17.bench` file. Ouput for other files will be similar.
```python

>>> python3.7 main_sta.py --read_ckt c17.bench --read_nldm sample_NLDM.lib



Circuit Delay  :  64.68834289793794 ps

----------------------------------------------------------------------
	 	 GATE SLACKS
----------------------------------------------------------------------
INPUT-1 : 31.629008569012157 ps
INPUT-2 : 24.339789909919176 ps
INPUT-3 : 5.880758445267084 ps
INPUT-6 : 5.880758445267084 ps
INPUT-7 : 24.237080755551016 ps
NAND-10 : 31.629008569012157 ps
NAND-11 : 5.880758445267084 ps
NAND-16 : 5.880758445267087 ps
NAND-19 : 11.072632556188681 ps
NAND-22 : 5.880758445267087 ps
NAND-23 : 5.880758445267087 ps

----------------------------------------------------------------------
	 	 CRITICAL PATH
----------------------------------------------------------------------
INPUT-3
NAND-11
NAND-16
NAND-22

```

Please note that output will be saved in a file called `ckt_traversal_<ckt>.txt`.


## Note 

Critical path shown in the output is from top to bottom. This means that the first gate/pin shown here is the INPUT and the lines following this gate/pin is path of the signal to create the Critical Path. 

So in the above case, the Critical Path is :
`INPUT-3 --> NAND-11 --> NAND-16 --> NAND-22`