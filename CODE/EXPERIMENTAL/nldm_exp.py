"""
Mini-Project 1 Phase 1 

This file contains functions that are used to parse given .lib(NLDM) file into a data structure(LUT class) and 
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
>>> cell: NOR2_X1
        input slews: 0.00117378,0.00472397,0.0171859,0.0409838,0.0780596,0.130081,0.198535
        load cap: 0.365616,1.854900,3.709790,7.419590,14.839200,29.678300,59.356700
        delays:
            0.0136008,0.0161505,0.0205760,0.0292340,0.0462805,0.0801242,0.147594;
            0.0142633,0.0167540,0.0211519,0.0298650,0.0470595,0.0810783,0.148696;
            0.0202027,0.0226399,0.0267281,0.0350583,0.0519006,0.0857406,0.153365;
            0.0282210,0.0316593,0.0372260,0.0469299,0.0634650,0.0965651,0.163573;
            0.0381015,0.0422278,0.0490020,0.0610840,0.0815179,0.115113,0.181020;
            0.0503320,0.0550648,0.0628653,0.0768972,0.101146,0.141009,0.207020;
            0.0651817,0.0704989,0.0792584,0.0950330,0.122530,0.168656,0.242490;

"""

import numpy as np
import re


NLDM_FILE = '/Users/taizunj/Documents/Masters_2024/ASU/Student_Docs/SEM2/EEE598_VLSI_Design_Automation/Mini_Project/CODE/TEST_FILES/sample_NLDM.lib'

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


############################################################################
# EXPERIMENTAL CODE 
# Version 0
# This code contains logic for cell_delay and output_slew table extraction
############################################################################
with open(NLDM_FILE, 'r') as file:
    file_content = file.read()

    cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{(.*?)}\s*}', file_content, re.DOTALL)
    # pprint(cell_blocks)

    for cell_name, cell_content in cell_blocks:

        # Extract cell capacitance
        cell_capacitance = re.search(r'capacitance\s*:\s*(\d+\.\d+);', cell_content)
        
        index_1 = re.search(r'cell_delay\s*\(\w+\)\s*{\s*index_1\s*\("(.*?)"\)', cell_content)
        index_1_values = np.array(index_1.group(1).split(','), dtype=float)
        
        index_2 = re.search(r'cell_delay\s*\(\w+\)\s*{[^}]*?index_2\s*\("(.*?)"\)', cell_content, re.DOTALL)
        index_2_values = np.array(index_2.group(1).split(','), dtype=float)
        
        _cell_delay = re.search(r'values\s*\((.*?)\);', cell_content, re.DOTALL).group(1).replace('", \\\n', '').replace('\t', '').replace('"', '')
        rows = _cell_delay.split(' ')
        cell_delay_table = np.array([list(map(float, row.split(','))) for row in rows if row.strip() != ''])
        print(f'Cell : {cell_name}, Cell Delay Table : {cell_delay_table}')

        # Output Slew Table extraction :
        _output_slew = re.search(r'output_slew\s*\(\w+\)\s*{[^}]*?values\s*\((.*?)\);', cell_content, re.DOTALL).group(1).replace('", \\\n', '').replace('\t', '').replace('"', '')
        rows  = _output_slew.split(' ')
        output_slew_table = np.array([list(map(float, row.split(','))) for row in rows if row.strip() != ''])
        print(f'Cell : {cell_name}, Output_slew_table : {output_slew_table}')



def print_nldm_output_slew_table(NLDM_FILE:str):

    with open( NLDM_FILE ) as file :
        
        file_content = file.read()
        cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{(.*?)}\s*}', file_content, re.DOTALL)

        for cell_name, cell_content in cell_blocks:

            # Extract cell capacitance
            cell_capacitance = re.search(r'capacitance\s*:\s*(\d+\.\d+);', cell_content)

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
            

def print_nldm_cell_delay_table(NLDM_FILE:str) :

    with open(NLDM_FILE, 'r') as file:

        file_content = file.read()
        cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{(.*?)}\s*}', file_content, re.DOTALL)


        for cell_name, cell_content in cell_blocks:

            # Extract cell capacitance
            cell_capacitance = re.search(r'capacitance\s*:\s*(\d+\.\d+);', cell_content)
            
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
            print(f'Cell : {cell_name}, Cell Delay Table : {cell_delay_table}')

            # Create LUT object for each cell and assign corresponding values :
            lut = LUT()
            lut.cell_name = cell_name
            lut.capacitance = cell_capacitance       # Capacitance of this cell
            lut.input_slews = index_1_values         # Index-1 values in cell_delay() sub-section of a cell
            lut.load_capacitance = index_2_values    # Index-2 values in cell_delay() sub-section of a cell
            lut.delay_table = cell_delay_table       # Cell delay table as a 2D numpy array