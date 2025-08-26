import argparse
import random
from pathlib import Path

def parse_fjs_line(line):
    """Parse a single FJSP job line into list of tokens."""
    return line.strip().split()


def generate_app_plans(num_tasks, min_apps, max_apps, min_plan_len, max_plan_len):
    """Generate a list of alternative process plans for a job."""
    num_apps = random.randint(min_apps, max_apps) if min_apps < max_apps else max_apps
    plans = []
    for _ in range(num_apps):
        # Determine plan length
        min_len = int(min_plan_len * num_tasks + 1)
        max_len = int(max_plan_len * num_tasks)
        plan_len = random.randint(min_len, max_len) if min_len < max_len else max_len
        # Sample unique task indices and sort
        tasks = sorted(random.sample(range(num_tasks), plan_len))
        plans.append(tasks)
    return plans


def process_file(input_path, output_path, min_apps, max_apps, min_plan_len, max_plan_len):
    with open(input_path, 'r') as fin:
        header = fin.readline().strip()
        job_lines = [line.strip() for line in fin if line.strip()]

    with open(output_path, 'w') as fout:
        # Write the original header
        fout.write(header + '\n')

        for job_line in job_lines:
            tokens = parse_fjs_line(job_line)
            # First token is number of tasks (ops)
            num_tasks = int(tokens[0])
            # Generate APPs
            app_plans = generate_app_plans(
                num_tasks, min_apps, max_apps, min_plan_len, max_plan_len
            )
            # Write the augmented job line with number of APPs
            fout.write(f"{len(app_plans)} {job_line}\n")
            # Write each APP line
            for plan in app_plans:
                plan_line = ' '.join(str(idx) for idx in ([len(plan)] + plan))
                fout.write(plan_line + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate FJSP instances with Alternative Process Plans (APPs).'
    )
    parser.add_argument('input', help='Input .fjs file path')
    parser.add_argument('output', help='Output file path for extended instances')
    parser.add_argument('--min_apps', type=int, default=1,
                        help='Minimum number of APPs per job')
    parser.add_argument('--max_apps', type=int, default=3,
                        help='Maximum number of APPs per job')
    parser.add_argument('--min_plan_len', type=float, default=0.5,
                        help='Minimum number of tasks in each APP')
    parser.add_argument('--max_plan_len', type=float, default=None,
                        help='Maximum number of tasks in each APP (default: number of tasks)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
        
    # determine max_plan_len default
    max_plan_len = args.max_plan_len if args.max_plan_len is not None else 1

    inp = Path(args.input)
    outp = Path(args.output)

    if inp.is_dir():
        # ensure output directory exists
        outp.mkdir(parents=True, exist_ok=True)
        for file in inp.iterdir():
            if file.is_file() and file.suffix == '.fjs':
                output_file = outp / file.name
                process_file(str(file), str(output_file),
                             args.min_apps, args.max_apps,
                             args.min_plan_len, max_plan_len)
    else:
        # single file mode
        outp.parent.mkdir(parents=True, exist_ok=True)
        process_file(str(inp), str(outp),
                     args.min_apps, args.max_apps,
                     args.min_plan_len, max_plan_len)
