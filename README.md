

# Static Timing Analyzer for VLSI Netlists

This project is a Static Timing Analyzer (STA) designed as part of my graduate coursework in VLSI Design Automation. It serves as an introduction to key algorithms used in VLSI-CAD, such as graph traversal techniques (BFS, DFS) and topological sorting for timing analysis

## Project Overview

The goal of this project is to analyze the timing characteristics of a VLSI circuit by computing slack values at each gate and identifying the critical path. The analysis is performed using topological traversal algorithms to propagate arrival times and required times through the circuit. This project was tested on the [I99T Benchmark suite](https://github.com/cad-polito-it/I99T).

## Project Phases

1. [Parsing Netlist and Cell Library](https://github.com/taizun-jj202/EEE598_VLSI_Design_Automation/tree/phase-1)

    - Developed a parser to extract circuit data from .bench netlist files.
    - Processed timing data from a sample .lib (Non-Linear Dynamic Model) file, which provides real-world delay characteristics of standard cells. 

2. [Static Timing Analysis & Critical Path Detection](https://github.com/taizun-jj202/EEE598_VLSI_Design_Automation/tree/phase-2)

    - Used topological sorting to propagate arrival and required times across the circuit.
    - Computed slack values for each gate to determine timing constraints.
    - Identified the critical path, which dictates the maximum delay of the circuit.

This project provides fundamental insights into graph-based timing analysis in VLSI-CAD tools and lays the groundwork for more advanced timing optimization techniques.


## Usage

To effectively utilize this project, follow the instructions corresponding to each phase by navigating to their respective folder as mentioned below and following instructions from README file in that folder.

1. Phase-1 :
```bash
    cd CODE
    cd PY_FILES
    cd Phase-1
```
2. Phase-2 :
```bash
    cd CODE
    cd PY_FILES
    cd Phase-2
```

Follow the README in these folders to use each part of this mini-project separately.

## Test files

All files used as input to either phase are stored in `TEST_FILES` folder. 
Sample outputs for each Phase are given in the `OUTPUTS` folder for each phase. 