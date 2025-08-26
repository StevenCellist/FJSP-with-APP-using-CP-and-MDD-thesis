import re
import os
import json
import numpy as np
import pandas as pd

def parse_log(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    text = ''.join(lines)

    # a) Number of variables and constraints
    vc_match = re.search(r'Minimization problem - (\d+) variables, (\d+) constraints', text)
    if not vc_match:
        raise ValueError("Could not find variables and constraints line")
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
            # e.g. *  588   33   0.09s  1  (gap is 31.46%)
            parts = re.split(r'\s+', line)
            # parts[1]: best, parts[3]: time, last part contains gap
            try:
                best = float(parts[1])
                time_str = parts[3]
                time_point = float(time_str.rstrip('s'))
            except (IndexError, ValueError):
                continue
            gap_match = re.search(r'gap is ([\d\.]+)%', line)
            gap = float(gap_match.group(1)) if gap_match else None

            # Update latest time
            latest_time = time_point

            progress.append({
                'time': time_point,
                'bound': current_lb,
                'best': best,
                'gap': gap
            })

    return {
        'variables': variables,
        'constraints': constraints,
        'time_limit': time_limit,
        'workers': workers,
        'status': status,
        'solve_time': solve_time,
        'progress': progress
    }

def summarize_benchmarks(root_dir):
    rows = []

    # iterate over each dataset sub‐directory
    # for dataset in sorted(os.listdir(root_dir)):
    #     ds_path = os.path.join(root_dir, dataset)
    #     if not os.path.isdir(ds_path):
    #         continue
    #     print(dataset)
        
    ds_path = root_dir

    total     = 0
    opt_times = []
    feas_gaps = []
    count_opt = 0
    count_feas= 0

    # iterate over each instance file
    for fname in os.listdir(ds_path):
        if not fname.endswith('.log'):
            continue
        total += 1
        stats = parse_log(os.path.join(ds_path, fname))

        if stats['status'] == 'Optimal':
            count_opt += 1
        else:
            count_feas += 1
        
        # take the final gap from the last progress item
        opt_times.append(stats['solve_time'])
        final_gap = stats['progress'][-1]['gap']
        feas_gaps.append(final_gap)

        print(f"{int(stats['progress'][-1]['bound']): 5}; {int(stats['progress'][-1]['best']): 5}; {str(stats['solve_time']).replace('.', ',')}")

    # compute averages (guard against empty lists)
    avg_time = np.mean(opt_times) if opt_times else np.nan
    avg_gap  = np.mean(feas_gaps) if feas_gaps else np.nan

    rows.append({
        # 'Dataset'        : dataset,
        'Total'          : total,
        'Optimal #'      : count_opt,
        'Avg Time [opt]' : avg_time,
        'Feasible #'     : count_feas,
        'Avg Gap [feas]' : avg_gap
    })

    # build a pandas DataFrame and print it
    df = pd.DataFrame(rows,
                      columns=[
                          'Dataset', 'Total',
                          'Optimal #', 'Avg Time [opt]',
                          'Feasible #', 'Avg Gap [feas]'
                      ])
    # print(df.to_string(index=False))
    return df

def print_latex_summary(df, caption="Summary of CP Optimizer results"):
    """
    Given a DataFrame with columns
      ['Dataset', 'Total', 'Optimal #', 'Avg Time [opt]', 'Feasible #', 'Avg Gap [feas]']
    this will print a complete LaTeX table.
    """
    # Begin table
    print(r"\begin{table}[ht]")
    print(r"\centering")
    print(r"\begin{tabular}{lrrrrr}")
    print(r"\toprule")
    # Column names
    print(r"Dataset & Instances & Optimal \# & Feasible \# & Avg Time & Avg Gap \\")
    print(r"\midrule")
    # Rows
    for _, row in df.iterrows():
        # format floats to 2 decimal places, use '-' for NaNs
        t_opt = f"{row['Avg Time [opt]']:.2f}" if not np.isnan(row['Avg Time [opt]']) else "-"
        g_fea = f"{row['Avg Gap [feas]']:.2f}"  if not np.isnan(row['Avg Gap [feas]'])  else "-"
        print(f"{row['Dataset']} & "
              f"{row['Total']} & "
              f"{row['Optimal #']} & {row['Feasible #']} & "
              f"{t_opt} & {g_fea} \\\\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\caption{" + caption + r"}")
    print(r"\end{table}")


if __name__ == '__main__':
    # data = parse_log("../../../Results/cpoptimizer_8_900/Behnke/01.log")
    # print(json.dumps(data, indent=2))

    # point this at the parent folder containing all the dataset‐dirs
    df = summarize_benchmarks(r"results_ws_100\cpoptimizer_8_60")
    print_latex_summary(df)
