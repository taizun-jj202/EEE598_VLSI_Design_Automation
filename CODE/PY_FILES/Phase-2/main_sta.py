"""

Mini-Project 1 Phase 2

This file is intended to perform Static Timing Analysis (STA) on a given netlist.
Please note that due to some constraints, this code will not fully work on the following files :
    - b19_C.bench
    - b17_C.bench

    


@author Taizun Jafri, jafri.taizun.s@gmail.com 
@file Phase-2 Mini-Project STA file.
@data 12 Mar 2025 22:09:34   
"""

import os
import argparse
from main_sta_functions import *

DEBUG = 0

if DEBUG:
    import debugpy

    debugpy.listen(("localhost", 5678))
    print("Waiting for debugger to attach...")
    debugpy.wait_for_client()
    debugpy.breakpoint()


parser = argparse.ArgumentParser(
   
    description="""
                    Mini-Project Phase 2

                    This program performs Static Timing Analysis.
                    Program builds upon Phase-1 of Mini-Project.
                """,
    epilog="""
            Example Usage :

                python3.7 main_sta.py --read_ckt c17.bench --read_nldm sample_NLDM.lib
           
           """
)

parser.add_argument("--read_ckt", 
                    type=str,
                    help="Input path to .bench file to be read using this program")

parser.add_argument("--read_nldm", 
                    type=str,
                    help="Input path to .lib file to be read using this program")

args = parser.parse_args() # Parses arguments into object.


if args.read_ckt and args.read_nldm :
    
    BENCH_FILE_PATH = os.path.abspath(args.read_ckt)
    NLDM_FILE_PATH = os.path.abspath(args.read_nldm)
    OUTPUT_FILE = f"ckt_traversal_{os.path.splitext(os.path.basename(BENCH_FILE_PATH))[0]}.txt"

    get_bench_nodes(BENCH_FILE_PATH)
    get_nldm_data(NLDM_FILE_PATH)
    
    set_load_capacitance(nodes)
    Compute_arrival_timing(nodes) 
    _circuit_delay = Compute_Required_Time(nodes)
    # _critical_path = Find_critical_path(outputs_list)
    
    with open(OUTPUT_FILE, 'w') as f:
        
        f.write('\n')
        f.write(f"Circuit Delay  :  {_circuit_delay * 1000} ps")

        f.write("\n")
        f.write("\n")
        f.write('-' * 70)
        f.write("\n")
        f.write("\t \t GATE SLACKS")
        f.write("\n")
        f.write('-' * 70)
        f.write("\n")
        for node in nodes.values():
            f.write(f"{node.gate_type}-{node.name} : {node.slack * 1000} ps\n")

        Find_critical_path(outputs_list, file=f)
