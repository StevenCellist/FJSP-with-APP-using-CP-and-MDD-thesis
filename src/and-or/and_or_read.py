from dataclasses import dataclass
import argparse

ProcessingData = list[tuple[int, int, bool]]
Arc = tuple[int, int]

@dataclass
class Instance:
    """
    The FJSPLIB instance data.

    Parameters
    ----------
    num_jobs
        The number of jobs.
    num_machines
        The number of machines.
    num_operations
        The number of operations.
    jobs
        A list of job data, each job consisting of a list of operation indices.
    precedences
        A list of tuples consisting of two operation indices, representing the
        precedence relationship of two operations.
    setups
        A list of tuples consisting of a machine index, two operation indices,
        and the setup time between the two operations on that machine.
    """

    num_jobs: int
    num_machines: int
    num_operations: int
    jobs: list[list[ProcessingData]]
    precedences: list[Arc]
    
def parse_instance_file_to_tuple(filename):
    """
    Parses a flexible AJSP instance file (with machine flexibility) and returns a tuple:
      (num_jobs, num_machines, total_operations, jobs_ops, precedences)
    
    The file format is as follows:
      - First line: <num_jobs> <num_machines>
      - Then, for each job:
            Job <job_id> <num_or_subgraphs>
        For each or‑subgraph:
            OR <branch_count>
          For each branch:
            If branch is SINGLE, one line of the form:
              SINGLE <op1> <op2> ... <op5>
            where each <op> is represented as:
              k m1 t1 m2 t2 ... mk tk
            If branch is SPLIT, then three lines appear:
              SPLIT
              SUB1 <count> <op1> ... <op_count>
              SUB2 <count> <op1> ... <op_count>
            and the branch’s operations are the concatenation of SUB1’s and SUB2’s operations.
    
    Dummy nodes:
      - A dummy start node (machine 0, time 0) is inserted at the beginning of each job.
      - A dummy end node (machine 0, time 0) is inserted at the end of each job.
    
    In the returned data structure:
      - Each operation is represented as (k, alternatives),
        where k is the number of alternatives and alternatives is a list of (machine, processing_time).
      - Precedences is a list of tuples (from_op_index, to_op_index, relation),
        with relation either "and" (within a branch) or "or" (linking branches between or‑subgraphs or connecting dummy nodes).
    """
    global_ops = []    # Flat list of all operations (each is (k, alternatives))
    prec_list = []     # List of (from_idx, to_idx, relation)
    jobs_ops = []      # List of jobs; each job is a list of indices into global_ops

    # Helper: parse operations from a list of tokens.
    # tokens: list of tokens representing one or more operations.
    # Returns a list of operations, where each operation is (k, alternatives)
    def parse_ops_from_tokens(tokens):
        ops = []
        i = 0
        while i < len(tokens):
            k = int(tokens[i])
            i += 1
            alternatives = []
            for _ in range(k):
                m = int(tokens[i])
                t = int(tokens[i+1])
                alternatives.append((m, t))
                i += 2
            ops.append((k, alternatives))
        return ops

    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Read header: first line is "num_jobs num_machines"
    header = lines[0].split()
    num_jobs, num_machines = int(header[0]), int(header[1])
    line_idx = 1

    # Process each job.
    for j in range(num_jobs):
        job_indices = []  # global operation indices for operations in this job

        # Create dummy start node for this job.
        dummy_start = (1, [(0, 0)], False)  # one alternative: machine 0, processing time 0.
        start_idx = len(global_ops)
        global_ops.append(dummy_start)
        job_indices.append(start_idx)

        # Expect job header: "Job <job_id> <num_or_subgraphs>"
        parts = lines[line_idx].split()
        num_or_subgraphs = int(parts[2])
        line_idx += 1

        # For storing branch info per or-subgraph for precedence connections.
        # Each entry is a list of branch tuples: (first_op_idx, last_op_idx, [list of op indices])
        job_or_info = []

        # Process each or‑subgraph in the job.
        for or_sub in range(num_or_subgraphs):
            # Read OR subgraph header: "OR <branch_count>"
            parts = lines[line_idx].split()
            branch_count = int(parts[1])
            line_idx += 1

            branches_info = []  # branch info for current or‑subgraph

            for _ in range(branch_count):
                tokens = lines[line_idx].split()
                if tokens[0] == "SINGLE":
                    # Remove "SINGLE" token and parse the remaining tokens.
                    op_tokens = tokens[1:]
                    ops = parse_ops_from_tokens(op_tokens)
                    line_idx += 1
                elif tokens[0] == "SPLIT":
                    line_idx += 1  # skip "SPLIT" line
                    # Parse SUB1 line.
                    tokens_sub1 = lines[line_idx].split()
                    op_tokens1 = tokens_sub1[2:]  # ignore "SUB1" and count
                    ops1 = parse_ops_from_tokens(op_tokens1)
                    line_idx += 1
                    # Parse SUB2 line.
                    tokens_sub2 = lines[line_idx].split()
                    op_tokens2 = tokens_sub2[2:]  # ignore "SUB2" and count
                    ops2 = parse_ops_from_tokens(op_tokens2)
                    line_idx += 1
                    # The branch's operations are the concatenation of SUB1's and SUB2's operations.
                    ops = ops1 + ops2
                else:
                    raise ValueError(f"Unexpected branch type in line: {lines[line_idx]}")
                
                branch_start = len(global_ops)
                branch_indices = []
                # Append each operation in this branch to the global list.
                for k, alt in ops:
                    global_ops.append((k, alt, True))
                    branch_indices.append(len(global_ops) - 1)
                    job_indices.append(len(global_ops) - 1)
                branch_end = branch_indices[-1]
                # Add internal "and" precedences within the branch.
                for idx in range(len(branch_indices) - 1):
                    prec_list.append((branch_indices[idx], branch_indices[idx+1], "and"))
                branches_info.append((branch_indices[0], branch_indices[-1], branch_indices))
            
            # Add inter or‑subgraph precedence edges.
            if not job_or_info:
                # First or‑subgraph: add an "or" precedence from dummy start to each branch's first op.
                for (_, _, branch_indices) in branches_info:
                    prec_list.append((start_idx, branch_indices[0], "or"))
            else:
                # For every branch in previous or‑subgraph, add an "or" edge to every branch's first op in current.
                prev_or = job_or_info[-1]
                for (_, _, prev_branch) in prev_or:
                    for (cur_first, _, cur_branch) in branches_info:
                        prec_list.append((prev_branch[-1], cur_branch[0], "or"))
            job_or_info.append(branches_info)
        
        # Create dummy end node for this job.
        dummy_end = (1, [(0, 0)], True)  # machine 0, time 0.
        end_idx = len(global_ops)
        global_ops.append(dummy_end)
        job_indices.append(end_idx)

        # From every branch in the final or‑subgraph, add an "and" precedence edge to dummy end.
        final_or = job_or_info[-1]
        for (_, _, branch_indices) in final_or:
            prec_list.append((branch_indices[-1], end_idx, "and"))
        
        jobs_ops.append([global_ops[i] for i in job_indices])
    
    total_ops = len(global_ops)
    return Instance(num_jobs, num_machines, total_ops, jobs_ops, prec_list)


# Example usage:
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Parse a flexible AJSP instance file with dummy start/end nodes into a tuple."
    )
    parser.add_argument("filename", type=str, help="Path to the instance .txt file.")
    args = parser.parse_args()
    
    num_jobs, num_machines, total_ops, jobs_ops, precedences = parse_instance_file_to_tuple(args.filename)
    print("Parsed instance with dummy nodes:")
    print(f"  Number of jobs: {num_jobs}")
    print(f"  Number of machines: {num_machines}")
    print(f"  Total number of operations (including dummies): {total_ops}")
    print("\nJobs (each as a list of operations, where an operation is (k, alternatives)):")
    for i, job in enumerate(jobs_ops, start=1):
        print(f"  Job {i}:")
        for op in job:
            print(f"    {op}")
    print("\nPrecedences (from, to, relation):")
    for p in precedences:
        print(f"  {p}")
