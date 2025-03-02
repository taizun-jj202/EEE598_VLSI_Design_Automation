# Mini-Project Phase-1

## Table of Contents 
1. [File Description](#file-description)
2. [Evaluation Environment Setup](#evaluation-environment-setup)
    - 2.1 [Setup Python venv](#setup-python-venv)
    - 2.2 [Arguments](#arguments)
3. [Usage](#usage)


## File Description :

- `parser.py` file that is main parser and executes functions to extract data from `.bench` and `.lib`
- `functions.py` contains functions used to perform parsing functionality.
- `requirements.txt` contains list of all packages required by the parser.

Here `parser.py` is the main file. `parser.py` and `functions.py` must be in the same directory.

## Evaluation Environment Setup 

**`NOTE`** : 
- This parser has been developed with `python3.7`. Please ensure python version 3.7 is installed on the system before running the parser file.
- `parser.py` will create a text file containing the required result as well as print out the runtime of the program. 
    - For e.g, if we parse `c17.bench` file using `python3.7 parser.py --read_ckt c17.bench`, then there will be a output text file named `ckt_details_c17.txt`

### Setup python venv 

Use the following commands to setup python virtual env for parser using the following commands

```python
python3.7 -m venv EEE598_V 
source EEE598_V/bin/activate.csh
pip3 install -r requirements.txt
python3.7 parser.py <arguments> <file>

```
### Arguments 

The parser can be used with the following command line arguments :
1.  parser.py `--read_ckt` <.bench file>
2.  parser.py `--slews` `--read_nldm` <.lib file> 
3.  parser.py `--delays` `--read_nldm` <.lib file> 

- `--slews` and `--delays` comand must be used with the `--read_nldm` argument. See [Usage](#usage) section for more detail

## Usage 

Ensure `parser.py` and `functions.py` are in the same directory. 
If both files are in the same directory, you may now run the parser using the commands below. 
Outputs here are show for `c17.bench` file and `sample_NLDM.lib` files respectively

#### **NOTE** : parser will save a text file containing the result, and if file cannot be created, parser will print the output to the console.

`parser.py` can be used to :
1. Extract(parse) data from `.bench` files using the following command :
    ```python
    >>> python3.7 parser.py --read_ckt (path to `.bench` file here)
    ```

    **Expected output :**
    ```python
    +-----------------+---------+
    | Type            |   Count |
    +=================+=========+
    | Primary Inputs  |       5 |
    +-----------------+---------+
    | Primary Outputs |       2 |
    +-----------------+---------+
    | INPUT gates     |       5 |
    +-----------------+---------+
    | NAND gates      |       6 |
    +-----------------+---------+


    ----------------------------------------------------------------------
                    FAN-OUT
    ----------------------------------------------------------------------
    NAND-10: NAND-22
    NAND-11: NAND-16, NAND-19
    NAND-16: NAND-22, NAND-23
    NAND-19: NAND-23
    NAND-22: OUTPUT-22
    NAND-23: OUTPUT-23
    ----------------------------------------------------------------------
                    FAN-IN
    ----------------------------------------------------------------------
    NAND-10 : INPUT-1, INPUT-3
    NAND-11 : INPUT-3, INPUT-6
    NAND-16 : INPUT-2, NAND-11
    NAND-19 : NAND-11, INPUT-7
    NAND-22 : NAND-10, NAND-16
    NAND-23 : NAND-16, NAND-19
    ```



2. We can extract(parse) the `output_slew` and  `cell_delay` table using the following command :

- To get cell_delay table for each cell, we use :
    ```python
    >>> python3.7 parser.py --delays --read_nldm (path to .lib file here)
    ```

    **Expected output for each cell in .lib file :**

    ```python
    Cell Name          : NAND2_X1
    Cell Capacitance   : 1.599032
    Input Slew         : [0.00117378 0.00472397 0.0171859  0.0409838  0.0780596  0.130081
    0.198535  ]
    Load Capacitance   : [ 0.365616  1.8549    3.70979   7.41959  14.8392   29.6783   59.3567  ]
    Cell Delay Table    :
        0.0074307,0.0112099,0.0157672,0.0247561,0.0426101,0.0782368,0.149445
        0.00896317,0.0127084,0.0173,0.0263569,0.0442815,0.0799642,0.151206
        0.0141826,0.0189535,0.0236392,0.0325101,0.0503637,0.0860462,0.157306
        0.0198673,0.0266711,0.0336357,0.044885,0.0628232,0.098154,0.16922
        0.0262799,0.0348883,0.043833,0.0586475,0.0818511,0.117889,0.188351
        0.0334985,0.0438815,0.0546771,0.0727012,0.101569,0.145562,0.216015
        0.0415987,0.0537162,0.0663517,0.0874425,0.121509,0.174517,0.253405
    ```

- To get output_slew table for each cell in liberty file, we use :
    ```python
    >>> python3.7 parser.py --delays --read_nldm (path to .lib file here)
    ```

    **Expected output for each cell in .lib file :**
    ```python 
    Cell Name          : NAND2_X1
    Cell Capacitance   : 1.599032
    Input Slew         : [0.00117378 0.00472397 0.0171859  0.0409838  0.0780596  0.130081 0.198535  ]
    Load Capacitance   : [ 0.365616  1.8549    3.70979   7.41959  14.8392   29.6783   59.3567  ]
    Output Slew Table  :
        0.00474878,0.00814768,0.0123804,0.020848,0.0377848,0.0716838,0.139435
        0.00475427,0.00814708,0.0123814,0.0208446,0.0377762,0.0716641,0.139428
        0.0077976,0.009978,0.0130179,0.02085,0.0378031,0.0716776,0.13943
        0.0122628,0.0156758,0.0191464,0.0247382,0.0382858,0.0716833,0.139437
        0.0178385,0.0220827,0.0266676,0.0342116,0.0458454,0.0726908,0.139429
        0.0249336,0.0298045,0.0352101,0.0445099,0.0592803,0.0822832,0.139806
        0.0337631,0.03916,0.0452534,0.0559346,0.0736025,0.100571,0.148264  
    ```

