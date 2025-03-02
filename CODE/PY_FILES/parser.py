"""
Mini-Project 1 Phase 1 

This file is intended to parse given .bench file into a data structure and display 
output in the following way :

>>> python3.7 parser.py --read_ckt c17.bench
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

>>> python3.7 parser.py --slews --read_nldm sample_NLDM.lib 

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

>>> python3.7 parser.py --delays --read_nldm sample_NLDM.lib   

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



@author Taizun Jafri, jafri.taizun.s@gmail.com
@file Phase-1 Mini-Project Parser file.
@data 10 Feb 2025 22:09:34
"""

import os
import argparse
from functions import *
import time
import contextlib

# Command line argument parser section. 
#   Supports the following commands :
#       --read_ckt
#       --slews
#       --delays
#       --read_nldm

parser = argparse.ArgumentParser(
    description="""
    Mini-Project-1 Parser File

    This program processes the .bench file provided.
    
    Features :
    - Read specific .bench file and produce output that shows the number of 
      different gates in the file.
    - Read specific .lib file and produce output that shows the slew values.
    """,
    epilog="""
    Example usage :
        python3.7 parser.py --read_ckt c17.bench 
        python3.7 parser.py --slews --read_nldm sample_NLDM.lib
        python3.7 parser.py --delays --read_nldm sample_NLDM.lib
    """
)

# Add --read_ckt argument to parser
parser.add_argument("--read_ckt", 
                    type=str,
                    help="Input path to .bench file to be read using this program")

# Add --slews and --read_nldm arguments to parser
parser.add_argument("--slews", 
                    action="store_true",
                    help="Flag to indicate that slew values should be printed")

parser.add_argument("--delays",
                    action="store_true",
                    help="Flag to indicate that delay table should be printed")

parser.add_argument("--read_nldm", 
                    type=str,
                    help="Input path to .lib file to be read using this program")

args = parser.parse_args() # Parses arguments into object.

# --read_ckt argument.
if args.read_ckt:
    BENCH_FILE_PATH = os.path.abspath(args.read_ckt)
    start = time.time()
    create_nodes(BENCH_FILE_PATH)
    set_nodes(BENCH_FILE_PATH)
    end = time.time()
    output_file = f"ckt_details_{os.path.splitext(os.path.basename(BENCH_FILE_PATH))[0]}.txt"
    with open(output_file, 'w') as f:
        print_output_info(f)
    print(f"\nExecution time for .bench parsing : {(end-start):.6f} seconds")
    print(f"Output saved to {output_file}")

# --slews and --read_nldm arguments.
if args.slews and args.read_nldm:
    NLDM_FILE_PATH = os.path.abspath(args.read_nldm)
    start = time.time()
    output_file = f"slew_LUT_{os.path.splitext(os.path.basename(NLDM_FILE_PATH))[0]}.txt"
    with open(output_file, 'w') as f:
        with contextlib.redirect_stdout(f):
            print_nldm_output_slew_table(NLDM_FILE_PATH)
    end = time.time()
    print(f"\nExecution time for slew tables : {(end-start):.6f} seconds")
    print(f"Output saved to {output_file}")

# --delays and --read_nldm arguments.
if args.delays and args.read_nldm:
    NLDM_FILE_PATH = os.path.abspath(args.read_nldm)
    start = time.time()
    output_file = f"delay_LUT_{os.path.splitext(os.path.basename(NLDM_FILE_PATH))[0]}.txt"
    with open(output_file, 'w') as f:
        with contextlib.redirect_stdout(f):
            print_nldm_cell_delay_table(NLDM_FILE_PATH)
    end = time.time()
    print(f"\nExecution time for delay tables: {(end-start):.6f} seconds")
    print(f"Output saved to {output_file}")