import re
import matplotlib.pyplot as plt


def parse_concatenated_log(file_path):
    """
    Parses a single concatenated log file containing multiple runs delimited by separators.
    Returns a list of dicts: each with 'file' and 'progress' list.
    """
    runs = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_run_lines = []
    current_file = None
    for line in lines:
        # Detect start of a new run
        m = re.match(r'Running cargo with argument:.*?/([^/]+\.txt)', line)
        if m:
            # save previous run
            if current_file is not None:
                runs.append({'file': current_file, 'lines': current_run_lines})
            # start new
            current_file = m.group(1)
            current_run_lines = []
            continue
        # detect separator: end of run
        if line.strip().startswith('---'):
            if current_file is not None:
                runs.append({'file': current_file, 'lines': current_run_lines})
                current_file = None
                current_run_lines = []
            continue

        # accumulate if inside a run
        if current_file is not None:
            current_run_lines.append(line.rstrip())

    # catch last run if no trailing separator
    if current_file is not None and current_run_lines:
        runs.append({'file': current_file, 'lines': current_run_lines})

    # Parse each run's lines
    parsed = []
    for run in runs:

        prog = []
        curr_lb = None
        duration = None
        final_lb = None
        final_ub = None
        final_gap = None

        for ln in run['lines']:
            # LB: 601 (0.0028)
            lb_m = re.match(r'LB:\s*(\d+)\s*\(([0-9\.]+)\)', ln)
            if lb_m:
                curr_lb = int(lb_m.group(1))
                prog.append({'time': float(lb_m.group(2)), 'bound': curr_lb, 'best': None, 'gap': None})
                continue
            # UB: 432 (0.0079)
            ub_m = re.match(r'UB:\s*(\d+)\s*\(([0-9\.]+)\)', ln)
            if ub_m:
                prog.append({'time': float(ub_m.group(2)), 'bound': curr_lb, 'best': int(ub_m.group(1)), 'gap': None})
                continue
            # Duration:   61.120 seconds
            dur_m = re.match(r'Duration:\s*([0-9\.]+) seconds', ln)
            if dur_m:
                duration = float(dur_m.group(1))
                continue
            # Lower Bnd:  446
            lb_final_m = re.match(r'Lower Bnd:\s*(\d+)', ln)
            if lb_final_m:
                final_lb = int(lb_final_m.group(1))
                continue
            # Upper Bnd:  432
            ub_final_m = re.match(r'Upper Bnd:\s*(\d+)', ln)
            if ub_final_m:
                final_ub = int(ub_final_m.group(1))
                continue
            # Gap:        0.031
            gap_m = re.match(r'Gap:\s*([0-9\.]+)', ln)
            if gap_m:
                final_gap = float(gap_m.group(1))
                continue

        # Append final progress entry if data available
        if duration is not None and final_lb is not None and final_ub is not None:
            prog.append({
                'time': duration,
                'bound': final_lb,
                'best': final_ub,
                'gap': final_gap
            })

        parsed.append({'file': run['file'], 'progress': prog})

    return parsed


def extract_bounds_at_cutoffs(parsed_runs, cutoffs):
    """
    Given parsed runs (list of dicts) and list of cutoff times,
    returns two dicts: lower_cutoffs and upper_cutoffs:
    { cutoff: { filename: lb } }, { cutoff: { filename: ub } }
    """
    lb_dict = {c: {} for c in cutoffs}
    ub_dict = {c: {} for c in cutoffs}
    for run in parsed_runs:
        fname = run['file'].rjust(7, '0')
        # if '247' not in fname:
        #     continue
        for c in cutoffs:
            entries = [e for e in run['progress'] if e['time'] <= c]
            # print(entries)
            lb, ub = None, None
            if entries:
                lbs = [e['bound'] for e in entries if e['bound'] is not None]
                ubs = [e['best'] for e in entries if e['best'] is not None]
                if lbs:
                    lb = lbs[-1]
                if ubs:
                    ub = ubs[-1]
            lb_dict[c][fname] = lb
            ub_dict[c][fname] = ub
    # print(lb_dict)
    # print(ub_dict)
    return ub_dict, lb_dict # swap


def plot_bounds(lb_dict, ub_dict):
    """
    Plots LB and UB for each file across all cutoffs.
    X-axis: file index; Y-axis: makespan.
    """
    cutoffs = sorted(lb_dict.keys())
    files = sorted(lb_dict[cutoffs[0]].keys())

    
    start_file = '194.txt'
    end_file   = '289.txt'
    start_idx = files.index(start_file)
    end_idx   = files.index(end_file)
    files = files[start_idx:end_idx+1]
    x = list(range(1, len(files) + 1))

    plt.figure()
    for c in cutoffs:
        lbs = [lb_dict[c][f] for f in files]
        ubs = [ub_dict[c][f] for f in files]
        plt.plot(x, lbs, marker='o', label=f'LB @ {c}s')
        plt.plot(x, ubs, marker='s', label=f'UB @ {c}s')

    plt.xlabel('File number')
    plt.xticks(x, files, rotation=45)
    plt.ylabel('Makespan')
    plt.title('Makespan UB/LB across Files for Various Cutoffs')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    log_file = "../stage8/ddo-fjs-rel/log-8-5-60.log"
    cutoffs = [1.1, 11, 111]
    runs = parse_concatenated_log(log_file)
    lb_dict, ub_dict = extract_bounds_at_cutoffs(runs, cutoffs)
    plot_bounds(lb_dict, ub_dict)
