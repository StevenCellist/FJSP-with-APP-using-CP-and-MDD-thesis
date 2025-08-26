import random
import argparse
import os

def sample_alternatives(num_machines, avg_flex, std=1):
    """Sample the number of machine alternatives for an operation.
    The result is at least 1 and at most num_machines."""
    if avg_flex == 1:
        return 1
    
    k = max(1, int(round(random.gauss(avg_flex, std))))
    return min(k, num_machines)

def generate_operation(num_machines, avg_flex):
    """
    Generates an operation with a candidate set.
    Returns a tuple of the form (k, [(machine1, time1), ..., (machine_k, time_k)]).
    """
    k = sample_alternatives(num_machines, avg_flex)
    # Randomly choose k distinct machines from the set {1,...,num_machines}
    machines = random.sample(range(1, num_machines+1), k)
    # For each candidate machine, sample a processing time between 2 and 99.
    alternatives = [(m, random.randint(2, 99)) for m in machines]
    return (k, alternatives)

def generate_branch(num_machines, avg_flex, branch_type):
    """
    Generates a branch.
    branch_type: 'single' (one and-subgraph of 5 operations)
                 or 'split' (two and-subgraphs: first 2 ops, then 3 ops)
    Returns a dictionary with key 'type' and an appropriate structure.
    Each operation is represented as (k, [(machine, time), ...]).
    """
    if branch_type == 'single':
        ops = []
        for _ in range(5):
            op = generate_operation(num_machines, avg_flex)
            ops.append(op)
        return {'type': 'single', 'operations': ops}
    elif branch_type == 'split':
        ops1 = []
        ops2 = []
        for _ in range(2):
            op = generate_operation(num_machines, avg_flex)
            ops1.append(op)
        for _ in range(3):
            op = generate_operation(num_machines, avg_flex)
            ops2.append(op)
        return {'type': 'split', 'sub1': ops1, 'sub2': ops2}
    else:
        raise ValueError("Unknown branch type.")

def generate_or_subgraph(num_machines, avg_flex, num_branches):
    """
    Generates an or-subgraph with num_branches.
    Each branch is generated randomly to be either a single and-subgraph or a split branch.
    """
    branches = []
    for _ in range(num_branches):
        branch_type = random.choice(['single', 'split'])
        branch = generate_branch(num_machines, avg_flex, branch_type)
        branches.append(branch)
    return branches

def generate_job(num_machines, avg_flex, num_or_subgraphs):
    """
    Generates a job consisting of num_or_subgraphs.
    For each or-subgraph, the number of branches is chosen uniformly (2 or 3).
    """
    job = []
    for _ in range(num_or_subgraphs):
        num_branches = random.choice([2, 3])
        or_subgraph = generate_or_subgraph(num_machines, avg_flex, num_branches)
        job.append(or_subgraph)
    return job

def write_instance(instance, num_jobs, num_machines, filename):
    """
    Writes the instance to a file.
    Format:
      First line: <num_jobs> <num_machines>
      Then for each job:
         Job <job_id> <number_of_or_subgraphs>
         For each or-subgraph:
             OR <branch_count>
             For each branch:
                If type is single:
                    SINGLE <op1> <op2> ... <op5>
                If type is split:
                    SPLIT
                    SUB1 2 <op1> <op2>
                    SUB2 3 <op3> <op4> <op5>
    
    Each operation is printed as: k m1 t1 m2 t2 ... mk tk
    """
    with open(filename, "w") as f:
        f.write(f"{num_jobs} {num_machines}\n")
        for j, job in enumerate(instance, start=1):
            f.write(f"Job {j} {len(job)}\n")
            for or_sub in job:
                f.write(f"OR {len(or_sub)}\n")
                for branch in or_sub:
                    if branch['type'] == 'single':
                        line = "SINGLE "
                        for op in branch['operations']:
                            k, alternatives = op
                            # Flatten alternatives into a string: k m1 t1 m2 t2 ...
                            op_str = f"{k} " + " ".join(f"{m} {t}" for m, t in alternatives)
                            line += op_str + "   "  # extra spaces to separate operations
                        f.write(line.strip() + "\n")
                    elif branch['type'] == 'split':
                        f.write("SPLIT\n")
                        line_sub1 = "SUB1 2 "
                        for op in branch['sub1']:
                            k, alternatives = op
                            op_str = f"{k} " + " ".join(f"{m} {t}" for m, t in alternatives)
                            line_sub1 += op_str + "   "
                        f.write(line_sub1.strip() + "\n")
                        line_sub2 = "SUB2 3 "
                        for op in branch['sub2']:
                            k, alternatives = op
                            op_str = f"{k} " + " ".join(f"{m} {t}" for m, t in alternatives)
                            line_sub2 += op_str + "   "
                        f.write(line_sub2.strip() + "\n")
        print(f"Instance written to {filename}")

def generate_instance(num_machines, num_jobs, avg_flex, num_or_subgraphs_per_job=1, out_dir="instances", n=0):
    """
    Generates an instance.
      For 5-machine instances, num_or_subgraphs_per_job should be None (jobs always have one or-subgraph).
      For 10-machine (or higher) instances, set num_or_subgraphs_per_job to 1, 2 or 3.
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    instance = []
    for _ in range(num_jobs):
        job = generate_job(num_machines, avg_flex, num_or_subgraphs_per_job)
        instance.append(job)
    
    # Create a filename based on parameters.
    fname = f"m{num_machines:>02}_j{num_jobs:>02}_or{num_or_subgraphs_per_job}_f{int(avg_flex)}_{n:>02}.afjsp"
    full_path = os.path.join(out_dir, fname)
    write_instance(instance, num_jobs, num_machines, full_path)

if __name__ == "__main__":
    random.seed(42)
    
    parser = argparse.ArgumentParser(description="Generate AJSP instance files with machine flexibility.")
    parser.add_argument("--machines", type=int, required=True,
                        help="Number of machines (e.g., 5 or 10)")
    parser.add_argument("--jobs", type=int, required=True,
                        help="Number of jobs. For 5 machines: 5,10,15,20; for 10 machines: 10,15,20 etc.")
    parser.add_argument("--avg_flex", type=float, default=1,
                        help="Average number of machine alternatives per operation (e.g., 3 for average 3 alternatives)")
    parser.add_argument("--or", type=int, dest="or_count", choices=[1,2,3], default=1,
                        help="For multi-machine instances, the common number of or-subgraphs per job.")
    parser.add_argument("--out_dir", type=str, default="instances",
                        help="Output directory for instance files.")
    parser.add_argument("--num", type=int, default=0,
                        help="Number of instances to generate.")
    args = parser.parse_args()
    
    for n in range(args.num + 1):
        generate_instance(args.machines, args.jobs, args.avg_flex, args.or_count, args.out_dir, n)

    # # For 5-machine instances, assume jobs have one or-subgraph.
    # if args.machines == 5:
    #     generate_instances(args.machines, args.jobs, args.avg_flex, num_or_subgraphs_per_job=None, out_dir=args.out_dir)
    # else:
    #     if args.or_count is None:
    #         raise ValueError("For instances with more than 5 machines, please provide --or (1, 2 or 3).")
    #     generate_instances(args.machines, args.jobs, args.avg_flex, num_or_subgraphs_per_job=args.or_count, out_dir=args.out_dir)
