import numpy as np
import re
from collections import deque
import debugpy


####################################################################################
#     SECTION 1 : Class definitions
#  Node and LUT classes used to extract and store data.
####################################################################################

class LUT : 

    def __init__(self):
        self.cell_name            = ""
        self.capacitance          = None
        self.input_slews          = None  # index-1 
        self.load_capacitance     = None  # index-2
        self.ost_input_slews      = None  # index-1 for output slew
        self.ost_load_capacitance = None  # index-2 for output slew
        self.delay_table          = None  # 2D numpy array for delay
        self.output_slew_table    = None  # 2D numpy array for output slew

    def interpolate_table(self, table, slew: float, capacitance: float):
        """Performs bilinear interpolation on the given table to 
        find the value at the given slew and capacitance using the
        following formula : 
            
        |      | C1  | C2  |
        | ---- | --- | --- |
        | tau1 | v11 | v12 |
        | tau2 | v21 | v22 |
            
        Then for given value `v` corresponding to (tau_in, C), 
        bilinear interpolation is given by : 

        v = v11*(C2-C)*(tau2 - tau) + v12*(C - C1)*(tau2 - tau) + v21*(C2 - C)*(tau - tau1) + v22*(C - C1)*(tau - tau1) / (C2 - C1)*(tau2 - tau1)
        """
        
        if self.ost_load_capacitance is None or self.ost_input_slews is None:
            raise ValueError("ost_load_capacitance or self.ost_input_slews is None")

        # Finding the indices for the given slew and capacitance
        row_1 = np.searchsorted(self.ost_load_capacitance, capacitance) - 1
        row_2 = min(row_1 + 1, len(self.ost_load_capacitance) - 1)
        
        col_1 = np.searchsorted(self.ost_input_slews, slew) - 1
        col_2 = min(col_1 + 1, len(self.ost_input_slews) - 1)

        # Getting the bounding values
        C_1, C_2 = self.ost_load_capacitance[row_1], self.ost_load_capacitance[row_2]
        tau_1, tau_2 = self.ost_input_slews[col_1], self.ost_input_slews[col_2]
        # v11, v12 = table[row_1, col_1], table[row_1, col_2]
        # v21, v22 = table[row_2, col_1], table[row_2, col_2]
        v11, v12 = table[row_1, col_1], table[col_2, row_1]
        v21, v22 = table[col_1, row_2], table[row_2, col_2]

        # If slew values become same, then change above formula accordingly :
        if tau_1 == tau_2:
            v = ((v11 * (C_2 - capacitance) * (tau_2 - slew) +
                  v12 * (capacitance - C_1) * (tau_2 - slew) +
                  v21 * (C_2 - capacitance) * (slew - tau_1) +
                  v22 * (capacitance - C_1) * (slew - tau_1)) / ((C_2 - C_1) * (tau_2)))
        
        elif C_1 == C_2:
            v = ((v11 * (C_2 - capacitance) * (tau_2 - slew) +
                  v12 * (capacitance - C_1) * (tau_2 - slew) +
                  v21 * (C_2 - capacitance) * (slew - tau_1) +
                  v22 * (capacitance - C_1) * (slew - tau_1)) / ((C_2) * (tau_2 - tau_1)))

        elif (tau_1 == tau_2 and C_1 == C_2):
            v = ((v11 * (C_2 - capacitance) * (tau_2 - slew) +
                  v12 * (capacitance - C_1) * (tau_2 - slew) +
                  v21 * (C_2 - capacitance) * (slew - tau_1) +
                  v22 * (capacitance - C_1) * (slew - tau_1)) / ((C_2) * (tau_2)))
        else: 
            # Perform bilinear interpolation
            v = ((v11 * (C_2 - capacitance) * (tau_2 - slew) +
                  v12 * (capacitance - C_1) * (tau_2 - slew) +
                  v21 * (C_2 - capacitance) * (slew - tau_1) +
                  v22 * (capacitance - C_1) * (slew - tau_1)) / ((C_2 - C_1) * (tau_2 - tau_1)))
        
        if np.isnan(v):
            debugpy.breakpoint()
            print(f"Interpolation result is nan for slew={slew}, capacitance={capacitance}")
        
        return v
    

class Node:
    def __init__(self):
        self.name      = ""
        self.gate_type = ""
        self.outname   = ""
        self.Cload     = 0.0
        self.fan_ins   = []  # List of instances that fan-in to this node
        self.fan_outs  = []  # List of instances that fan-out from this node
        
        # Every pin of a gate(node) will have the following attributes
        # arrival_time, input_slew will have the the same 
        # length as each input pin to gate will have these two attributes 
        self.arrival_time  = []  # Arrival time at input pins
        self.input_slew    = []  # Input slew at input pins
        self.cell_delay    = None  # Cell delay is a function of INPUT_SLEW and LOAD_CAPACITANCE
                                   # Each pin will have its own cell delay, hence we store it as a list
                                   # Cell_delay has same dimensions as ARRIVAL_TIME and INPUT_SLEW
        self._cell_delay   = []  # List of INPUT_SLEW * LOAD_CAPACITANCE. cell_delay is max value of this list.
        
        self.a_out              = None # Output arrival time.
        self._a_out             = None # List of output arrival time for each input pin.    
        self.t_out              = None # Output slew time.
        self.t_out_max_index    = None # Index of maximum value in t_out list.
        self.slack              = None # Slack = Ckt_Delay - a_out. Ckt_Delay is max_delay * 1.1
        self.required_time      = None # Required Time used to calculate slack

    def Cload_calculations(self):
        """ 
        Calculates Output load capacitance for each node.
        
        Checks the fan_outs of current node and matches the 
        gate_type of this node with corresponding cell in NLDM
        file to extract capacitance of that cell.
        
        If current node has more than two fanouts, Load capacitance 
        is given by the sum of all capacitances of fanouts multiplied by 
        number of fanouts divided by 2.
        
        """
        gate_type_to_lut_name = {
            'NAND' : 'NAND2_X1',
            'NOR'  : 'NOR2_X1',
            'AND'  : 'AND2_X1',
            'OR'   : 'OR2_X1',
            'XOR'  : 'XOR2_X1',
            'INV'  : 'INV_X1',
            'NOT'  : 'INV_X1',
            'BUF'  : 'BUF_X1',
            'BUFF'  : 'BUF_X1',
        }
        
        total_capacitance = 0.0
        for fan_out_node in self.fan_outs:
            lut_key = gate_type_to_lut_name[fan_out_node.gate_type]
            total_capacitance += float(LUT_nodes_set[lut_key].capacitance)
    
            self.Cload = total_capacitance

####################################################################################
#     SECTION 2 : Global Variables
####################################################################################

nodes         = {}       # All nodes in .bench file
inputs_list   = []       # Nodes that are of type INPUT from `nodes` list
outputs_list  = []       # Nodes that are of type OUTPUT from `nodes` list
circuit_delay = 0.0      # Initialize ckt delay to 0. Actual delay is calculated later in a function
LUT_nodes_set = {}       # Each object has LUT data for a specific gate.


####################################################################################
#     SECTION 3 : Parsing functions
####################################################################################

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
            LUT_nodes_set[cell_name] = lut               # Add cell to LUT set.

def nldm_cell_delay_table(NLDM_FILE:str) :

    with open(NLDM_FILE, 'r') as file:

        file_content = file.read()
        cell_blocks = re.findall(r'cell\s*\((.*?)\)\s*{(.*?)}\s*}', file_content, re.DOTALL)


        for cell_name, cell_content in cell_blocks:

            _cell_delay = re.search(r'values\s*\((.*?)\);', cell_content, re.DOTALL).group(1).replace('", \\\n', '').replace('\t', '').replace('"', '')
            rows = _cell_delay.split(' ')
            cell_delay_table = np.array([list(map(float, row.split(','))) for row in rows if row.strip() != ''])
           

            lut = LUT_nodes_set[cell_name]
            lut.delay_table = cell_delay_table       # Cell delay table as a 2D numpy array

def create_nodes(CIRCUIT_BENCH_FILE):
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
                node = Node()
                node.name = output_name
                outputs_list.append(node)
            
            elif "=" in line:
                out_name, expression = line.split("=")
                out_name = out_name.strip()
                gate_type, in_names = expression.split('(')
                in_names = in_names.split(')')[0].split(',')
                in_names = [name.strip() for name in in_names]

                node = Node()
                node.name = out_name
                node.gate_type = gate_type.strip().upper()  # Ensure gate_type is in uppercase
                node.fan_ins = [nodes[in_name] for in_name in in_names if in_name in nodes]
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
                
                # Update fan_outs and set arrival_time and input_slew for INPUT nodes
                node.fan_ins = [nodes[in_name] for in_name in in_names if in_name in nodes]
                [inp_node.fan_outs.append(node) for inp_node in node.fan_ins]

####################################################################################
#     SECTION 4 : Static TIming analysis function definitions
####################################################################################

# Sets load capacitance for each node(gate)
def set_load_capacitance(nodes_set):
    """
    Sets load capacitance for each node using Cload_calculations() method.
    and updates the output nodes."""
    
    [node.Cload_calculations() for node in nodes_set.values() if node.name not in [output_node.name for output_node in outputs_list]]
    
    # Setting Load Capacitance for each node in Output list.
    #  Cload for output node = 4 * capacitance of Inverter from NLDM file
    [setattr(nodes[output_node.name], 'Cload', 4 * float(LUT_nodes_set['INV_X1'].capacitance)) for output_node in outputs_list if output_node.name in nodes]

    # Update the objects in outputs_list with the corresponding nodes from the nodes dictionary
    for i, output_node in enumerate(outputs_list):
        if output_node.name in nodes:
            outputs_list[i] = nodes[output_node.name]


# Calculates arrival timings at each node.
# Uses Topological traversal and DAG algorithm to assign 
# cell delay, output arrival time and output slew.
def Compute_arrival_timing(graph):
    """
        Calculates arrival timings at each node.
        Uses Topological traversal and DAG algorithm to assign 
        cell delay, output arrival time and output slew.

        @brief Calculates output arrival-time, output slew and cell delay for each node.

        @param[in] graph List of Nodes.

        @details Uses DAG and Topological traversal to create graph like structure
                 to calculate above said values.

    """

    in_degree = {node.name: len(node.fan_ins) for node in graph.values()}
    queue = deque([node.name for node in graph.values() if in_degree[node.name] == 0])

    while queue:
        node_name = queue.popleft()
        node = graph[node_name]

        if node.gate_type == "INPUT":
            # INPUT nodes have fixed values
            node.a_out = 0 
            node.t_out = 0.002
            node._cell_delay = [0 for _ in range(len(node.fan_outs) + 1)] 
        else:
            # Compute output arrival time (a_out)
            gate_type_to_lut_name = {
            'NAND' : 'NAND2_X1',
            'NOR'  : 'NOR2_X1',
            'AND'  : 'AND2_X1',
            'OR'   : 'OR2_X1',
            'XOR'  : 'XOR2_X1',
            'INV'  : 'INV_X1',
            'NOT'  : 'INV_X1',
            'BUF'  : 'BUF_X1',
            'BUFF'  : 'BUF_X1',
        }
            gate_type = node.gate_type
            lut_key = gate_type_to_lut_name[gate_type]
            lut = LUT_nodes_set[lut_key]

            node._cell_delay = [
                lut.interpolate_table(lut.delay_table, node.input_slew[i], node.Cload)
                for i in range(len(node.input_slew))
            ]

            node._a_out = [node.arrival_time[i] + node._cell_delay[i] for i in range(len(node.arrival_time))]
            node.a_out = max(node._a_out)

            _t_out = [
                lut.interpolate_table(lut.output_slew_table, node.input_slew[i], node.Cload)
                for i in range(len(node.input_slew))
            ]
            node.t_out = max(_t_out)

        for fan_out in node.fan_outs:
            fan_out.arrival_time.append(node.a_out)
            fan_out.input_slew.append(node.t_out)
            in_degree[fan_out.name] -= 1

            # Add node to queue if all outnodes have been procesed.
            if in_degree[fan_out.name] == 0:
                queue.append(fan_out.name)


# Calculates Required time for each node.
def Compute_Required_Time(nodes, file=None):

    """
    
    Calculates required time for each node and calculates slack for current node using
    Req. arrival time and output arrival time of current node.

    First calculates the circuit delay to find Output required time from OUTPUT nodes.
    
    Required_arrival_time at gate = minimum of (Req. arrival time at fan_out node - cell delay of current node.)
    Slack  = Required_arrival_time - output_arrival_time of node

    @param:in nodes List of all nodes in .bench file.
    """

    max_delay = 0 
    for node in outputs_list:
        if node.a_out > max_delay:
            max_delay = node.a_out

    circuit_delay = 1.1 * max_delay
    debugpy.breakpoint()

    for node in outputs_list:
        node.required_time = circuit_delay

    in_degree = {node.name: len(node.fan_outs) for node in nodes.values()}
    queue = deque([node.name for node in outputs_list])

    while queue:
        node_name = queue.popleft()
        node = nodes[node_name]

        if node.gate_type != "OUTPUT":
            
            # Check added because _cell_delay does not exist for INPUT pins.
            # So required time of INPUT is simply the min of its fan_outs.
            # Check if the node is both INPUT and OUTPUT
            if node.gate_type == "INPUT" and node in outputs_list:
                node.required_time = circuit_delay
            
            elif node.gate_type == "INPUT":
                node.required_time = min(
                    [fan_out.required_time - (fan_out._cell_delay[fan_out.fan_ins.index(node)] if fan_out._cell_delay else 0) for fan_out in node.fan_outs]
                )
            
            elif node.fan_outs:
                node.required_time = min(
                    [fan_out.required_time - (fan_out._cell_delay[fan_out.fan_ins.index(node)] if fan_out._cell_delay else 0) for fan_out in node.fan_outs]
                )

            else:
                node.required_time = circuit_delay  

        # Propagate to fan-in nodes
        for fan_in in node.fan_ins:
            in_degree[fan_in.name] -= 1

            # If all fan-outs are processed, add to queue
            if in_degree[fan_in.name] == 0:
                queue.append(fan_in.name)

    for node in nodes.values():
        node.slack = node.required_time - node.a_out

    return circuit_delay

# Finds Critical Path of CKT.
def Find_critical_path(output_list, file=None):

    """
    Finds Critical path of the circuit.

    @param[in] output_list List of all OUTPUT nodes in .bench file.

    Start with primary OUTPUT with least amount of slack and traverse backwards 
    selecting gates connected to the output with minimum slack till we reach 
    primary INPUT.
    """
    # Find the primary output with the minimum slack
    min_slack_output = min(output_list, key=lambda node: node.slack)
    critical_path = [min_slack_output]

    current_node = min_slack_output
    while current_node.gate_type != "INPUT":
        # Find the fan-in with the minimum slack
        min_slack_fan_in = min(current_node.fan_ins, key=lambda node: node.slack)
        critical_path.append(min_slack_fan_in)
        current_node = min_slack_fan_in

    # Reverse the path to start from the primary input
    critical_path.reverse()
    
    if file:
        file.write("\n")
        file.write('-' * 70)
        file.write("\n")
        file.write("\t \t CRITICAL PATH")
        file.write("\n")
        file.write('-' * 70)
        file.write("\n")
        for node in critical_path:
            file.write(f"{node.gate_type}-{node.name}\n")
    else:
        print("Critical Path:")
        for node in critical_path:
            print(f"{node.gate_type}-{node.name}")

    # print("Critical Path:")
    # for node in critical_path:
    #     print(f"{node.gate_type}-{node.name}", file=file)

def Save_circuit_details(file_path, nodes, outputs_list):
    with open(file_path, 'w') as file:
        max_delay = max(node.a_out for node in outputs_list)
        circuit_delay = 1.1 * max_delay
        file.write(f"Circuit Delay: {circuit_delay * 1000} ps\n\n")
        
        file.write("\n")
        file.write('-' * 70)
        file.write("\t \t GATE SLACKS")
        file.write('-' * 70)
        for node in nodes.values():
            file.write(f"{node.gate_type}-{node.name} : {node.slack * 1000} ps\n")
        
        file.write("\n")
        file.write('-' * 70)
        file.write("\t \t CRITICAL PATH")
        file.write('-' * 70)
        critical_path = Find_critical_path(outputs_list)
        for node in critical_path:
            file.write(f"{node.gate_type}-{node.name}\n")




####################################################################################
#     SECTION 5 : Usefull parsing functions
####################################################################################

# Get data from .bench file into objects 
def get_bench_nodes(FILE):
    create_nodes(FILE)
    set_nodes(FILE)
    print("Nodes created and set successfully.")

# Get data from NLDM file into LUT objects
def get_nldm_data(NLDM_FILE:str) :
    print_nldm_output_slew_table(NLDM_FILE)
    nldm_cell_delay_table(NLDM_FILE)
    print("NLDM data extracted successfully.")


