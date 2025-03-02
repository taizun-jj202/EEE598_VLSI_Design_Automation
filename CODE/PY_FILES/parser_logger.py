import os
import subprocess
import time
import glob

# Folder containing the .bench files
test_files_folder = "/Users/taizunj/Documents/Masters_2024/ASU/Student_Docs/SEM2/EEE598_VLSI_Design_Automation/Mini_Project/CODE/TEST_FILES"

# List of .bench files to run
bench_files = glob.glob(os.path.join(test_files_folder, "*.bench"))

# List of commands to run for each .bench file
commands = [
    "python3.7 parser.py --read_ckt {bench_file}"
]

# Number of runs to average
num_runs = 10

# Log file to store the results
log_file = "parser_run_log.txt"

with open(log_file, 'w') as log:
    log.write(f"# Runtime averaged over {num_runs} runs")
    log.write("\n")

    log.write("Input File\t\tAverage Time (seconds)\n")
    log.write("="*40 + "\n")

    for bench_file in bench_files:
        for command in commands:
            total_time = 0.0
            for _ in range(num_runs):
                formatted_command = command.format(bench_file=bench_file)
                input_file = os.path.basename(bench_file)
                start_time = time.time()
                subprocess.run(formatted_command, shell=True)
                end_time = time.time()
                elapsed_time = end_time - start_time
                total_time += elapsed_time

            average_time = total_time / num_runs
            log.write(f"{input_file}\t\t{average_time:.6f}\n")

print(f"Log saved to {log_file}")
