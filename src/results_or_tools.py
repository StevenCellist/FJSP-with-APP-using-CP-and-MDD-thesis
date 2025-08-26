import re
import os
import json
import numpy as np
import pandas as pd

def parse_log(file_path):
    with open(file_path, 'r') as f:
        text = f.read()

    # Ensure each record starts on a new line
    text = re.sub(r'(?<!\n)#', r'\n#', text)
    lines = text.splitlines()

    # a) Variables and constraints (from '#Model')
    variables = constraints = None
    for line in lines:
        if line.startswith('#Model'):
            m = re.search(r'var:\d+/(\d+)\s+constraints:\d+/(\d+)', line)
            if m:
                variables = int(m.group(1))
                constraints = int(m.group(2))
                break

    # b) max_time_in_seconds
    m = re.search(r'max_time_in_seconds:\s*(\d+)', text)
    time_limit = int(m.group(1)) if m else None

    # c) num_workers
    m = re.search(r'num_workers:\s*(\d+)', text)
    workers = int(m.group(1)) if m else None

    # e) status
    status = None
    m = re.search(r'status:\s*(OPTIMAL|FEASIBLE)', text)
    if m:
        status = m.group(1).capitalize()

    # f) walltime
    m = re.search(r'walltime:\s*([0-9\.]+)', text)
    walltime = float(m.group(1)) if m else None

    # d) Progress values
    progress = []
    first_bound = True

    for line in lines:
        line = line.strip()
        # LB updates ('#Bound')
        if line.startswith('#Bound'):
            m = re.search(r'#Bound\s+([0-9\.]+)s\s+best:([^\s]+)\s+next:\[([^,]+),([^\]]+)\]', line)
            if not m:
                continue
            time_pt = float(m.group(1))
            best_str = m.group(2)
            lb = float(m.group(3))
            if first_bound or best_str == 'inf':
                ub = 1_000_000.0
                gap = 100.0
                first_bound = False
            else:
                ub = float(best_str)
                gap = (1 - lb/ub) * 100

            progress.append({'time': time_pt, 'bound': lb, 'best': ub, 'gap': gap})

        # UB improvements ('#<iter>')
        elif re.match(r'#\d+', line):
            m = re.search(r'#\d+\s+([0-9\.]+)s\s+best:([0-9\.]+)\s+next:\[([^,]+),', line)
            if not m:
                continue
            time_pt = float(m.group(1))
            ub = float(m.group(2))
            try:
                lb = float(m.group(3))
            except ValueError:
                continue
            gap = (1 - lb/ub) * 100
            progress.append({'time': time_pt, 'bound': lb, 'best': ub, 'gap': gap})

    # g) Final objective and best_bound as last progress entry
    obj = None
    bb = None
    mo = re.search(r'objective:\s*([0-9\.e\+]+)', text)
    mb = re.search(r'best_bound:\s*([0-9\.e\+]+)', text)
    if mo:
        obj = float(mo.group(1))
    if mb:
        bb = float(mb.group(1))
    if obj is not None and bb is not None and walltime is not None:
        final_gap = (1 - bb/obj) * 100 if obj != 0 else 0.0
        progress.append({'time': walltime, 'bound': bb, 'best': obj, 'gap': final_gap})

    return {
        'variables': variables,
        'constraints': constraints,
        'time_limit': time_limit,
        'workers': workers,
        'status': status,
        'solve_time': walltime,
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

        print(f"{int(stats['progress'][-1]['bound']): 5}; {int(stats['progress'][-1]['best']): 5}; {str(round(stats['solve_time'], 2)).replace('.', ',')}")

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

def print_latex_summary(df, caption="Summary of OR-Tools results"):
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
    # data = parse_log("../../../Results/ortools_8_900/behnke/17b.log")
    # print(json.dumps(data, indent=2))

    # point this at the parent folder containing all the dataset‐dirs
    df = summarize_benchmarks(r"results_ws_100\ortools_8_60")
    print_latex_summary(df)