import os
import re
import glob
import matplotlib.pyplot as plt

def parse_log(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    text = ''.join(lines)

    # a) Number of variables and constraints
    vc_match = re.search(r'Minimization problem - (\d+) variables, (\d+) constraints', text)
    if not vc_match:
        raise ValueError(f"Could not find variables and constraints line in {file_path}")
    variables = int(vc_match.group(1))
    constraints = int(vc_match.group(2))

    # b) TimeLimit value
    tl_match = re.search(r'TimeLimit\s*=\s*(\d+)', text)
    time_limit = int(tl_match.group(1)) if tl_match else None

    # c) Workers value
    w_match = re.search(r'Workers\s*=\s*(\d+)', text)
    workers = int(w_match.group(1)) if w_match else None

    # f) Complete solve time
    st_match = re.search(r'Time spent in solve\s*:\s*([\d\.]+)s', text)
    solve_time = float(st_match.group(1)) if st_match else None

    # e) Final solve status
    if "Search completed" in text:
        status = "Optimal"
    elif "Search terminated" in text:
        status = "Feasible"
    else:
        status = "Unknown"

    # d) Progress values
    progress = []
    current_lb = None
    latest_time = None

    for line in lines:
        line = line.strip()
        # New bound entries
        if line.startswith('+ New bound is'):
            lb_match = re.search(r'\+ New bound is (\d+)', line)
            lb = int(lb_match.group(1))

            # Check for gap in same line
            gap_match = re.search(r'gap is ([\d\.]+)%', line)
            if current_lb is None:
                # first new bound: fixed values
                time_point = 0.01
                ub = 1_000_000
                gap = 100.0
            else:
                # use latest_time for timestamp
                time_point = latest_time
                gap = float(gap_match.group(1)) if gap_match else None
                # UB = LB / (1 - gap)
                if gap is not None:
                    ub = int(round(lb / (1 - gap/100)))
                else:
                    ub = None

            current_lb = lb
            progress.append({
                'time': time_point,
                'bound': lb,
                'best': ub,
                'gap': gap
            })

        # Star lines with best, gap, time
        elif line.startswith('*'):
            parts = re.split(r'\s+', line)
            try:
                best = float(parts[1])
                time_str = parts[3]
                time_point = float(time_str.rstrip('s'))
            except (IndexError, ValueError):
                continue
            gap_match = re.search(r'gap is ([\d\.]+)%', line)
            gap = float(gap_match.group(1)) if gap_match else None

            latest_time = time_point

            progress.append({
                'time': time_point,
                'bound': current_lb,
                'best': best,
                'gap': gap
            })
            
    if status != "Optimal":
        progress.append(progress[-1].copy())
        progress[-1]['time'] = solve_time

    return {
        'file': os.path.basename(file_path),
        'variables': variables,
        'constraints': constraints,
        'time_limit': time_limit,
        'workers': workers,
        'status': status,
        'solve_time': solve_time,
        'progress': progress
    }


def parse_all_logs(folder_path, cutoff_time=60.0, pattern="*.log"):
    """
    Parse all log files in a folder and extract best UB and LB at a given cutoff time.

    Parameters:
    - folder_path: path to directory containing log files
    - cutoff_time: time cutoff in seconds
    - pattern: glob pattern for log files (default '*.log')

    Returns:
    - lower_bounds: dict mapping filename to best lower bound at cutoff
    - upper_bounds: dict mapping filename to best upper bound at cutoff
    """
    lower_bounds = {}
    upper_bounds = {}
    times = {}

    search_pattern = os.path.join(folder_path, pattern)
    files = glob.glob(search_pattern)

    for file_path in files:
        data = parse_log(file_path)

        # Filter progress entries up to cutoff
        if cutoff_time < 1:
            entries = [data['progress'][1]]
        else:
            entries = [p for p in data['progress'] if p['time'] <= cutoff_time]
        if not entries:
            lb_at_cutoff = None
            ub_at_cutoff = None
            time = 0
        else:
            best_entry = entries[-1]
            lb_at_cutoff = best_entry['bound']
            ub_at_cutoff = best_entry['best']
            time = best_entry['time']

        fname = data['file']
        lower_bounds[fname] = lb_at_cutoff
        upper_bounds[fname] = ub_at_cutoff
        times[fname] = time
        
    return lower_bounds, upper_bounds, times


if __name__ == "__main__":
    # Example usage
    folder = r"..\results\cpoptimizer_8_900"
    # cutoffs = [0.5, 1, 10, 60, 900]
    cutoffs = [0.1, 10, 909]

    # Gather bounds per cutoff
    lb_dicts = []
    ub_dicts = []
    for c in cutoffs:
        lb, ub, ts = parse_all_logs(folder, cutoff_time=c)
        lb_dicts.append(lb)
        ub_dicts.append(ub)
        print(round(sum(ub.values()) / len(ub.values()), 3), max(ub.values()))
        
    for i in range(1, 272):
        n = f"{i:03}.log"
        print(f"{int(ub_dicts[0][n])}; {int(ub_dicts[1][n])}; {int(ub_dicts[2][n])}")

    # File list and x-axis indices
    files = sorted(lb_dicts[0].keys())
    x = list(range(1, len(files) + 1))

    plt.figure()
    # Plot LB and UB for each cutoff
    for idx, c in enumerate(cutoffs):
        # lbs = [lb_dicts[idx][f] for f in files]
        ubs = [ub_dicts[idx][f] for f in files]
        # plt.plot(x, lbs, marker='o', label=f'LB @ {c}s')
        plt.plot(x, ubs, marker='s', label=f'UB @ {c if c < 900 else 900}s')

    plt.xlabel('File number')
    plt.xticks(x, files, rotation=45)
    plt.ylabel('Makespan')
    plt.title('Makespan Ub/Lb across Files for Various Cutoffs')
    plt.legend()
    plt.tight_layout()
    plt.show()
