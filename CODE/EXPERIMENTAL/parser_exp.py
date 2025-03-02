"""
Mini-Project 1 Phase 1 

This file is intended to parse given .bench file into a data structure and display 
output in the following way :

>>> 5 primary inputs
    2 primary outputs
    6 NAND gates
    Fanout...
    NAND-10: NAND-22
    NAND-11: NAND-16, NAND-19
    NAND-16: NAND-22, NAND-23
    NAND-19: NAND-23
    NAND-22: OUTPUT-22
    NAND-23: OUTPUT-23
    Fanin...
    NAND-10: INPUT-1, INPUT-3
    NAND-11: INPUT-3, INPUT-6
    NAND-16: INPUT-2, NAND-11
    NAND-19: INPUT-7, NAND-11
    NAND-22: NAND-10, NAND-16
    NAND-23: NAND-16, NAND-19

@author Taizun Jafri, jafri.taizun.s@gmail.com
@file Phase-1 Mini-Project Parser file.
@data 10 Feb 2025 22:09:34
"""

C17_BENCH_FILE_PATH = '/Users/taizunj/Documents/Masters_2024/ASU/Student_Docs/SEM2/EEE598_VLSI_Design_Automation/Mini_Project/CODE/TEST_FILES/c17.bench'
B15_BENCH_FILE_PATH = '/Users/taizunj/Documents/Masters_2024/ASU/Student_Docs/SEM2/EEE598_VLSI_Design_Automation/Mini_Project/CODE/TEST_FILES/b15.bench'
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

# # Reading .bench file and printing separated outputs:
# with open(B15_BENCH_FILE_PATH, 'r') as f:
    
#     for line in f:
    
#         line = line.strip()
#         if line.startswith("INPUT"):
#             input_name = line.split('(')[1].split(')')[0]
#             node = Node()  # Declare instance of Node class to store as input node
#             node.name = input_name
#             node.gate_type = "INPUT"
#             nodes[input_name] = node
#             inputs_list.append(node)  # Append to input nodes list
        
#         elif line.startswith("OUTPUT"):
#             output_name = line.split('(')[1].split(')')[0]
#             outputs_list.append(output_name)
        
#         # Main parsing logic : 
#             # Splits line into 2 => Takes left side as node, from other side
#             #   recognizes GATE_TYPE and inputs to that particular gate.
#             #   Then loops over inputs and adds current node to output of nodes in input list.
#         elif "=" in line:
#             node = Node()
#             out_name, expression = line.split("=")
#             out_name = out_name.strip()
#             node.name = out_name
#             gate_type, in_names = expression.split('(')
#             in_names = in_names.split(')')[0].split(',')
#             in_names = [name.strip() for name in in_names]  # Strip whitespace from input names

#             node.gate_type = gate_type.strip()  # Set the gate type
#             node.inputs = [nodes[in_name] for in_name in in_names]
#             for inp_node in node.inputs:
#                 inp_node.outputs.append(node)  # Input nodes to this node must have this node as their output
#             nodes[out_name] = node

# First pass: Create all nodes
with open(B15_BENCH_FILE_PATH, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith("INPUT"):
            input_name = line.split('(')[1].split(')')[0]
            NODE = Node()
            NODE.name = input_name
            NODE.gate_type = "INPUT"
            nodes[input_name] = NODE
            inputs_list.append(NODE)
             
        elif line.startswith("OUTPUT"):
            output_name = line.split('(')[1].split(')')[0]
            outputs_list.append(output_name)
        
        elif "=" in line:
            out_name, expression = line.split("=")
            out_name = out_name.strip()
            gate_type, in_names = expression.split('(')
            in_names = in_names.split(')')[0].split(',')
            in_names = [name.strip() for name in in_names]

            NODE = Node()
            NODE.name = out_name
            NODE.gate_type = gate_type.strip()
            nodes[out_name] = NODE

# Second pass: Set inputs and outputs
with open(B15_BENCH_FILE_PATH, 'r') as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            out_name, expression = line.split("=")
            out_name = out_name.strip()
            gate_type, in_names = expression.split('(')
            in_names = in_names.split(')')[0].split(',')
            in_names = [name.strip() for name in in_names]

            NODE = nodes[out_name]
            NODE.inputs = [nodes[in_name] for in_name in in_names]
            for inp_node in NODE.inputs:
                inp_node.outputs.append(NODE)

# Function to print the required output

def print_output_info():
    # Prints primary inputs and outputs
    print(f"{len(inputs_list)} primary inputs")
    print(f"{len(outputs_list)} primary outputs")

    # Count and print the different types and number of gates
    gate_counts = {}
    for node in nodes.values():
        if node.gate_type:
            if node.gate_type not in gate_counts:
                gate_counts[node.gate_type] = 0
            gate_counts[node.gate_type] += 1
    for gate_type, count in gate_counts.items():
        print(f"{count} {gate_type} gates")

    # To print Fanout :
    # Output: e.g -- NAND-16 : NAND-22, NAND-19
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
    
print_output_info()