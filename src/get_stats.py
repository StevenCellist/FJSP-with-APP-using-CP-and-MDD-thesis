from pyjobshop.read import read
import os

# file = r"fjsp-sdst\fattahi\Fattahi_setup_15.fjs"

folder = "Instances/FJSP/Naderi"
files = []

for root, _, filenames in os.walk(folder):
    for f in filenames:
        if f.endswith(".fjs"):
            # if not 'kacem' in os.path.join(root, f):
            #     continue
            # if 'sdata' in os.path.join(root, f):
            #     continue
            files.append(os.path.join(root, f))
            
total_tasks = 0; total_jobs = 0; total_modes = 0
min_jobs = 1000; max_jobs = 0
min_machs = 1000; max_machs = 0
min_ops = 1000; max_ops = 0
flexibility = 0

for file in files:
    # print(f"{file: <25} | ", end = '')
    
    d = read(file, setup=False)
    # print(d.num_tasks, d.num_jobs, d.num_modes, d.num_resources)
    total_jobs += d.num_jobs
    total_tasks += d.num_tasks
    total_modes += d.num_modes
    flexibility += (d.num_modes / d.num_tasks) / d.num_resources
    
    min_jobs = min(min_jobs, d.num_jobs)
    max_jobs = max(max_jobs, d.num_jobs)
    
    min_machs = min(min_machs, d.num_resources)
    max_machs = max(max_machs, d.num_resources)
    
    min_ops = min(min_ops, d.num_tasks)
    max_ops = max(max_ops, d.num_tasks)
    
print(f"Instances: {len(files)}, Jobs: {min_jobs}-{max_jobs}, Machines: {min_machs}-{max_machs}, Operations: {round(total_tasks / total_jobs, 1)}, Machines/ops: {round(total_modes / total_tasks, 1)}, Flexibility: {round(flexibility / len(files), 2)}", )