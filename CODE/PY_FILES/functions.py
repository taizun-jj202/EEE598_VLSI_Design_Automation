"""

This file contains all function definitions used for the following purposes :
    - Reading .bench file
    - Reading .lib file (NLDM table)

    
File contains two sections :
    - Reading and parsing data for --read_ckt command
    - Reading and parsing data for --slew and --delays command

The section for .lib has documentation related to it in this file, however 
the section for .bench files does not have documentation as of now

@author Taizun Jafri, jafri.taizun.s@gmail.com
@file functions.py
@brief Contains all functions used in parser.py file
@date 11 Feb 2025 22:24:37
"""


####################################################################################
#     SECTION 1 :
#  All functions used for .bench files.
####################################################################################




from tabulate import tabulate
import contextlib


# Define data structure to store details of each node in bench
class Node:
    def __init__(self):
        self.name = ""
        self.gate_type = ""
        self.outname = ""
        self.Cload = 0.0
        self.inputs = []  # List of instances that fan-in to this node
        self.outputs = [] # List of instances that fan-out from this node
        self.Tau_in = []
        self.inp_arrival = []
        self.outp_arrival = []
        self.max_out_arrival = 0.0
        self.Tau_out = 0.0

# Store nodes, input lines, and output lines
nodes = {}
inputs_list = []
outputs_list = []


# Run function first to create all nodes
#   as it creates problems when nodes are not in order 
def create_nodes(CIRCUIT_BENCH_FILE) :
    with open(CIRCUIT_BENCH_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("INPUT"):
                input_name = line.split('(')[1].split(')')[0]
                node = Node()
                node.name = input_name
                node.gate_type = "INPUT"
                nodes[input_name] = node
                inputs_list.append(node)
                
            elif line.startswith("OUTPUT"):
                output_name = line.split('(')[1].split(')')[0]
                outputs_list.append(output_name)
            
            elif "=" in line:
                out_name, expression = line.split("=")
                out_name = out_name.strip()
                gate_type, in_names = expression.split('(')
                in_names = in_names.split(')')[0].split(',')
                in_names = [name.strip() for name in in_names]

                node = Node()
                node.name = out_name
                node.gate_type = gate_type.strip()
                nodes[out_name] = node


# Run function after the first one to set inputs and ouputs
#   IMPORTANT : Run only after running create_nodes() function.
def set_nodes(CIRCUIT_BENCH_FILE):
    with open(CIRCUIT_BENCH_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                out_name, expression = line.split("=")
                out_name = out_name.strip()
                gate_type, in_names = expression.split('(')
                in_names = in_names.split(')')[0].split(',')
                in_names = [name.strip() for name in in_names]

                node = nodes[out_name]
                node.inputs = [nodes[in_name] for in_name in in_names]
                for inp_node in node.inputs:
                    inp_node.outputs.append(node)



# Function to print all nodes in required format :
def print_output_info(file=None):
    # Count the different types and number of gates
    gate_counts = {}
    for node in nodes.values():
        if node.gate_type:
            if node.gate_type not in gate_counts:
                gate_counts[node.gate_type] = 0
            gate_counts[node.gate_type] += 1

    # Prepare data for the table
    table_data = [
        ["Primary Inputs", len(inputs_list)],
        ["Primary Outputs", len(outputs_list)]
    ]
    for gate_type, count in gate_counts.items():
        table_data.append([f"{gate_type} gates", count])

    # Redirect output to file if provided
    with contextlib.redirect_stdout(file) if file else contextlib.nullcontext():
        # Print the table
        print(tabulate(table_data, headers=["Type", "Count"], tablefmt="grid"))

        # Print Fanout :
        # Example Output: e.g -- NAND-16 : NAND-22, NAND-19
        print("\n")
        print('-' * 70)
        print("\t \t FAN-OUT")
        print('-' * 70)
        for node in nodes.values():
            if node.gate_type != "INPUT" and node.outputs:  # Exclude primary inputs from fan-out section
                output_names = [f"{out_node.gate_type}-{out_node.name}" for out_node in node.outputs]
                print(f"{node.gate_type}-{node.name}: {', '.join(output_names)}")
            elif node.gate_type != "INPUT":
                print(f"{node.gate_type}-{node.name}: OUTPUT-{node.name}")

        # print("\n")
        print('-' * 70)
        print("\t \t FAN-IN")
        print('-' * 70)
        for node in nodes.values():
            if node.gate_type != "INPUT" and node.inputs:
                input_names = [f"INPUT-{inp_node.name}" if inp_node.gate_type == "-" else f"{inp_node.gate_type}-{inp_node.name}" for inp_node in node.inputs]
                print(f"{node.gate_type}-{node.name} : {', '.join(input_names)}")
            elif node.gate_type != "INPUT":
                print(f"{node.gate_type}-{node.name} : INPUT-{node.name}")


####################################################################################
#     SECTION 2 :
#  All functions used for .lib files.
# Please see nldm_exp.py for documentation
####################################################################################
"""
Mini-Project 1 Phase 1 

This section contains functions that are used to parse given .lib(NLDM) file into a data structure(LUT class) and 
    print data about corresponding `slew` and `delay` values and give the following sample output :

Parsing file using the --delays option should give the following output for all cells in the file:
>>> cell: NAND2_X1
        input slews: 0.00117378,0.00472397,0.0171859,0.0409838,0.0780596,0.130081,0.198535
        load cap: 0.365616,1.854900,3.709790,7.419590,14.839200,29.678300,59.356700
        delays:
        0.00743070,0.0112099,0.0157672,0.0247561,0.0426101,0.0782368,0.149445;
        0.00896317,0.0127084,0.0173000,0.0263569,0.0442815,0.0799642,0.151206;
        0.0141826,0.0189535,0.0236392,0.0325101,0.0503637,0.0860462,0.157306;
        0.0198673,0.0266711,0.0336357,0.0448850,0.0628232,0.0981540,0.169220;
        0.0262799,0.0348883,0.0438330,0.0586475,0.0818511,0.117889,0.188351;
        0.0334985,0.0438815,0.0546771,0.0727012,0.101569,0.145562,0.216015;
        0.0415987,0.0537162,0.0663517,0.0874425,0.121509,0.174517,0.253405;

Parsing file using the --slew option should produce the following output for all cells in the file:

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

"""

import numpy as np
import re

LUT_nodes_set = {}

# Define class LUT as mentioned in ProjectDescription.pdf file.
class LUT : 
    def __init__(self):
        self.cell_name = ""
        self.capacitance = None
        self.input_slews = None          # index-1 
        self.load_capacitance = None     # index-2
        self.ost_input_slews = None      # index-1 for output slew
        self.ost_load_capacitance = None # index-2 for output slew
        self.delay_table = None          # 2D numpy array for delay
        self.output_slew_table = None    # 2D numpy array for output slew


def print_nldm_output_slew_table(NLDM_FILE:str):

    with open( NLDM_FILE ) as file :
        
        file_content = file.read()
        cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{(.*?)}\s*}', file_content, re.DOTALL)

        for cell_name, cell_content in cell_blocks:

            # Extract cell capacitance
            cell_capacitance = re.search(r'capacitance\s*:\s*(\d+\.\d+);', cell_content).group(1)

            # Extract index-1 values from output_slew subsection of .lib file
            index_1 = re.search(r'output_slew\s*\(\w+\)\s*{\s*index_1\s*\("(.*?)"\)', cell_content)
            index_1_values = np.array(index_1.group(1).split(','), dtype=float)
            
            # Extract index-2 values from output_slew subsection of .lib file
            index_2 = re.search(r'output_slew\s*\(\w+\)\s*{[^}]*?index_2\s*\("(.*?)"\)', cell_content, re.DOTALL)
            index_2_values = np.array(index_2.group(1).split(','), dtype=float)
            
            # Extract output slew table from output_slew sub-section of cell in .lib file.
            _output_slew = re.search(r'output_slew\s*\(\w+\)\s*{[^}]*?values\s*\((.*?)\);', cell_content, re.DOTALL).group(1).replace('", \\\n', '').replace('\t', '').replace('"', '')
            rows  = _output_slew.split(' ')
            output_slew_table = np.array([list(map(float, row.split(','))) for row in rows if row.strip() != ''])            
        
            # Create LUT object for each cell and assign corresponding values :
            lut = LUT()
            lut.cell_name = cell_name
            lut.capacitance = cell_capacitance           # Capacitance of this cell
            lut.ost_input_slews = index_1_values         # Index-1 values in output_slew() sub-section of a cell
            lut.ost_load_capacitance = index_2_values    # Index-2 values in output_slew() sub-section of a cell
            lut.output_slew_table = output_slew_table    # Output slew table as a 2D numpy array

            print(f'Cell Name          : {lut.cell_name}')
            print(f'Cell Capacitance   : {lut.capacitance}')
            print(f'Input Slew         : {lut.ost_input_slews}')
            print(f'Load Capacitance   : {lut.ost_load_capacitance}')
            print("Output Slew Table  :")
            for row in lut.output_slew_table:
                print(f"    {','.join(map(str, row))}")

            

def print_nldm_cell_delay_table(NLDM_FILE:str) :

    with open(NLDM_FILE, 'r') as file:

        file_content = file.read()
        cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{(.*?)}\s*}', file_content, re.DOTALL)


        for cell_name, cell_content in cell_blocks:

            # Extract cell capacitance
            cell_capacitance = re.search(r'capacitance\s*:\s*(\d+\.\d+);', cell_content).group(1)
            
            # Extract index-1 values from cell_delay subsection of .lib file
            index_1 = re.search(r'cell_delay\s*\(\w+\)\s*{\s*index_1\s*\("(.*?)"\)', cell_content)
            index_1_values = np.array(index_1.group(1).split(','), dtype=float)
            
            # Extract index-2 values from cell_delay subsection of .lib file
            index_2 = re.search(r'cell_delay\s*\(\w+\)\s*{[^}]*?index_2\s*\("(.*?)"\)', cell_content, re.DOTALL)
            index_2_values = np.array(index_2.group(1).split(','), dtype=float)
            
            # Extract cell delay table from cell_delay sub-section of cell in .lib file.
            _cell_delay = re.search(r'values\s*\((.*?)\);', cell_content, re.DOTALL).group(1).replace('", \\\n', '').replace('\t', '').replace('"', '')
            rows = _cell_delay.split(' ')
            cell_delay_table = np.array([list(map(float, row.split(','))) for row in rows if row.strip() != ''])
           
            # Create LUT object for each cell and assign corresponding values :
            lut = LUT()
            lut.cell_name = cell_name
            lut.capacitance = cell_capacitance       # Capacitance of this cell
            lut.input_slews = index_1_values         # Index-1 values in cell_delay() sub-section of a cell
            lut.load_capacitance = index_2_values    # Index-2 values in cell_delay() sub-section of a cell
            lut.delay_table = cell_delay_table       # Cell delay table as a 2D numpy array

            print('\n')
            print(f'Cell Name          : {lut.cell_name}')
            print(f'Cell Capacitance   : {lut.capacitance}')
            print(f'Input Slew         : {lut.input_slews}')
            print(f'Load Capacitance   : {lut.load_capacitance}')
            print("Cell Delay Table    :")
            for row in lut.delay_table:
                print(f"    {','.join(map(str, row))}")