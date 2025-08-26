import re
import os
import argparse

def parse_log_file(log_path, output_dir=None):
    """
    Parse the log file for solution entries and write each solution to a .sol file.

    Args:
        log_path (str): Path to the log file.
        output_dir (str, optional): Directory where .sol files will be written. Defaults to current directory.
    """
    instance_name = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Regex patterns
    run_pattern = re.compile(r"Running cargo with argument:.*?/(?P<name>[^/]+)\.fjs")
    solution_pattern = re.compile(r"^\s*Solution:\s*(?P<sol>\[.*\])")

    with open(log_path, 'r') as log_file:
        for line in log_file:
            # Detect instance start
            run_match = run_pattern.search(line)
            if run_match:
                instance_name = run_match.group('name')
                continue

            # Detect solution line
            if instance_name:
                sol_match = solution_pattern.match(line)
                if sol_match:
                    solution = sol_match.group('sol')
                    if len(solution) < 10:
                        continue
                    # Determine output file path
                    out_name = f"{instance_name}.sol"
                    if output_dir:
                        out_name = os.path.join(output_dir, out_name)
                    # Write solution to file
                    with open(out_name, 'w') as sol_file:
                        sol_file.write(solution)
                    print(f"Wrote solution for instance {instance_name} to {out_name}")
                    # Reset instance_name to avoid repeated writes
                    instance_name = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse solutions from log file')
    parser.add_argument('logfile', help='Path to the log file')
    parser.add_argument('-o', '--output', help='Directory for output .sol files', default=None)
    args = parser.parse_args()

    parse_log_file(args.logfile, args.output)
