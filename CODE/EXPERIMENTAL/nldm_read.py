

import numpy as np
import re


NLDM_FILE = '/Users/taizunj/Documents/Masters_2024/ASU/Student_Docs/SEM2/EEE598_VLSI_Design_Automation/Mini_Project/CODE/TEST_FILES/sample_NLDM.lib'

LUT_nodes_set = {}

# Define class LUT as mentioned in ProjectDescription.pdf file.
class LUT : 
    def __init__(self):
        self.cell_name = ""
        self.input_slews = None          # index-1 
        self.load_capacitance = None     # index-2
        self.delay_table = None          # 2D numpy array for delay
        self.output_slew_table = None    # 2D numpy array for output slew
        self.capacitance = None

        self.table__rows = None         # Variables keep track of rows and cols 
        self.table__cols = None


def parse_lib_file(nldm_file):

    cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{([\s\S]*?)}\s*$', nldm_file, re.S)

    for cell_name, cell_body in cell_blocks:

        print(cell_body)
        lut = LUT()
        lut.cell_name = cell_name.strip()

        capacitance_match = re.search(r'capacitance\s*:\s*(\d+\.\d+);', cell_body)
        index_1_match = re.search(r'index_1\s*\("(.*?)"\)', cell_body)
        index_2_match = re.search(r'index_2\s*\("(.*?)"\)', cell_body)
        delay_values_match = re.search(r'cell_delay\(.*?\)\s*{[\s\S]*?values\s*\(([\s\S]*?)\);', cell_body)
        slew_values_match = re.search(r'output_slew\(.*?\)\s*{[\s\S]*?values\s*\(([\s\S]*?)\);', cell_body)
        
        if capacitance_match:
            lut.capacitance = float(capacitance_match.group(1))
        if index_1_match:
            lut.input_slews = np.array([float(x) for x in index_1_match.group(1).split(',')])
        if index_2_match:
            lut.load_capacitance = np.array([float(x) for x in index_2_match.group(1).split(',')])
        if delay_values_match:
            delay_values = delay_values_match.group(1).replace('\\', '').strip().split('",')
            lut.delay_table = np.array([[float(x.strip().strip('"')) for x in row.split(',')] for row in delay_values])
        if slew_values_match:
            slew_values = slew_values_match.group(1).replace('\\', '').strip().split('",')
            lut.output_slew_table = np.array([[float(x.strip().strip('"')) for x in row.split(',')] for row in slew_values])
        
        LUT_nodes_set[cell_name] = lut

    return LUT_nodes_set


def print_nldm_delay_table() :

    with open(NLDM_FILE, 'r') as f :
        
        lut_objects = parse_lib_file(f.read())

        for cell_name, lut_node in lut_objects.items():
            print('\n')
            print('-' * 80 )
            print(f"Cell        : {cell_name}")
            print(f"Input Slews : {','.join(map(str, lut_node.input_slews))}")
            print(f"Load Cap    : {','.join(map(str, lut_node.load_capacitance))}")
            print("Delays:")
            for row in lut_node.delay_table:
                print(f"    {','.join(map(str, row))}")
            print("Output Slews:")
            for row in lut_node.output_slew_table:
                print(f"    {','.join(map(str, row))}")

print_nldm_delay_table()



#########################################################
# WORKING CODE :
#########################################################

# CELL DELAY TABLE :
# with open(NLDM_FILE, 'r') as file:
#     file_content = file.read()

#     cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{(.*?)}\s*}', file_content, re.DOTALL)
#     # pprint(cell_blocks)

#     for cell_name, cell_content in cell_blocks:
        
#         cell_capacitance = re.search(r'capacitance\s*:\s*(\d+\.\d+);', cell_content)  # Works as intended
        
#         index_1 = re.search(r'cell_delay\s*\(\w+\)\s*{\s*index_1\s*\("(.*?)"\)', cell_content)
#         index_1_values = np.array(index_1.group(1).split(','), dtype=float)
        
#         index_2 = re.search(r'index_2\s*\("(.*?)"\)', cell_content)
#         index_2_values = np.array(index_2.group(1).split(','), dtype=float)

#         # Cell Delay Table extraction :
#         _cell_delay = re.search(r'values\s*\((.*?)\);', cell_content, re.DOTALL).group(1).replace('", \\\n', '').replace('\t', '').replace('"', '')
#         rows = _cell_delay.split(' ')
#         cell_delay_table = np.array([list(map(float, row.split(','))) for row in rows if row.strip() != ''])
