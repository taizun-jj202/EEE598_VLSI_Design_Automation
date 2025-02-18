

C17_PATH = '/Users/taizunj/Documents/Masters_2024/ASU/Student_Docs/SEM2/EEE598_VLSI_Design_Automation/Mini_Project/CODE/TEST_FILES/c17.bench'


# Define a class named Node to represent each gate or input in the circuit
class Node:
    def __init__(self):
        self.name = ""  # Name of the node (gate or input)
        self.outname = ""  # Output name of the node
        self.Cload = 0.0  # Load capacitance
        self.inputs = []  # List of handles to the fanin nodes of this node
        self.outputs = []  # List of handles to the fanout nodes of this node
        self.Tau_in = []  # Array/list of input slews (for all inputs to the gate), to be used for STA
        self.inp_arrival = []  # Array/list of input arrival times for input transitions (ignore rise or fall)
        self.outp_arrival = []  # Array/list of output arrival times, outp_arrival = inp_arrival + cell_delay
        self.max_out_arrival = 0.0  # Arrival time at the output of this gate using max on (inp_arrival + cell_delay)
        self.Tau_out = 0.0  # Resulting output slew

# Define a function to read the .bench file and populate the nodes, inputs, and outputs
def read_bench(file_path):
    nodes = {}  # Dictionary to store nodes by their names
    inputs = []  # List to store input nodes
    outputs = []  # List to store output names

    # Open the .bench file for reading
    with open(file_path, 'r') as file:
        # Iterate over each line in the file
        for line in file:
            line = line.strip()  # Remove leading and trailing whitespace
            if line.startswith("INPUT"):  # Check if the line defines an input
                input_name = line.split('(')[1].split(')')[0]  # Extract the input name
                node = Node()  # Create a new Node instance
                node.name = input_name  # Set the node's name
                nodes[input_name] = node  # Add the node to the nodes dictionary
                inputs.append(node)  # Add the node to the inputs list
            elif line.startswith("OUTPUT"):  # Check if the line defines an output
                output_name = line.split('(')[1].split(')')[0]  # Extract the output name
                outputs.append(output_name)  # Add the output name to the outputs list
            elif "=" in line:  # Check if the line defines a gate
                out_name, expr = line.split('=')  # Split the line into output name and expression
                out_name = out_name.strip()  # Remove leading and trailing whitespace from the output name
                gate_type, in_names = expr.split('(')  # Split the expression into gate type and input names
                in_names = in_names.split(')')[0].split(',')  # Extract the input names
                in_names = [name.strip() for name in in_names]  # Remove leading and trailing whitespace from input names

                node = Node()  # Create a new Node instance
                node.name = out_name  # Set the node's name
                node.inputs = [nodes[in_name] for in_name in in_names]  # Set the node's inputs to the corresponding nodes
                for in_node in node.inputs:  # Iterate over the input nodes
                    in_node.outputs.append(node)  # Add this node to the outputs list of each input node
                nodes[out_name] = node  # Add the node to the nodes dictionary

    return nodes, inputs, outputs  # Return the nodes dictionary, inputs list, and outputs list

# Example usage of the read_bench function
# file_path = '/Users/taizunj/Documents/Masters_2024/ASU/Student_Docs/SEM2/EEE598_VLSI_Design_Automation/Mini_Project/CODE/FILES/c17.bench'
nodes, inputs, outputs = read_bench(C17_PATH)  # Read the .bench file and get the nodes, inputs, and outputs

# Print the nodes and their connections
for node_name, node in nodes.items():
    print(f"Node: {node.name}")  # Print the node's name
    print(f"  Inputs: {[n.name for n in node.inputs]}")  # Print the names of the input nodes
    print(f"  Outputs: {[n.name for n in node.outputs]}")  # Print the names of the output nodes
