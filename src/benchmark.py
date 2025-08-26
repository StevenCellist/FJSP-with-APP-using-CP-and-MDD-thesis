import argparse
import warnings
from functools import partial
from multiprocessing import cpu_count
from pathlib import Path
from typing import Optional

import numpy as np
import tomli
from tqdm.contrib.concurrent import process_map

import pyjobshop
from pyjobshop import Result, solve
from pyjobshop.Model import Model, Mode
from pyjobshop.Solution import Solution, TaskData
from pathlib import Path
from read import ProblemVariant, read


def parse_args():
    parser = argparse.ArgumentParser()

    msg = "Location of the instance file."
    parser.add_argument("instances", nargs="+", type=Path, help=msg)

    msg = "Scheduling problem variant to read."
    parser.add_argument(
        "--problem_variant",
        type=ProblemVariant,
        choices=[f.value for f in ProblemVariant],
        help=msg,
    )

    msg = "Directory to store best-found solutions (one file per instance)."
    parser.add_argument("--sol_dir", type=Path, help=msg)

    msg = "Solver to use."
    parser.add_argument(
        "--solver",
        type=str,
        default="ortools",
        choices=["ortools", "cpoptimizer"],
        help=msg,
    )

    msg = "Time limit for solving the instance, in seconds."
    parser.add_argument("--time_limit", type=float, default=float("inf"), help=msg)

    msg = "Whether to display the solver output."
    parser.add_argument("--display", action="store_true", help=msg)

    msg = (
        "Number of worker threads to use for solving a single instance."
        "Default is the number of available CPU cores."
    )
    parser.add_argument("--num_workers_per_instance", type=int, help=msg)

    msg = "Number of instances to solve in parallel. Default is 1."
    parser.add_argument("--num_parallel_instances", type=int, default=1, help=msg)

    msg = """
    Optional parameter configuration file (in TOML format). These parameters
    are passed to the solver as additional solver parameters.
    """
    parser.add_argument("--config_loc", type=Path, help=msg)

    msg = """
    Maximum number of jobs for instances with permutation constraints. This
    is because larger instances cannot be solved in reasonable amount of time.
    """
    parser.add_argument("--permutation_max_jobs", type=int, help=msg)

    return parser.parse_args()


def tabulate(headers: list[str], rows: np.ndarray) -> str:
    """
    Creates a simple table from the given header and row data.
    """
    # These lengths are used to space each column properly.
    lens = [len(header) for header in headers]

    for row in rows:
        for idx, cell in enumerate(row):
            lens[idx] = max(lens[idx], len(str(cell)))

    header = [
        "  ".join(f"{hdr:<{ln}s}" for ln, hdr in zip(lens, headers)),
        "  ".join("-" * ln for ln in lens),
    ]

    content = ["  ".join(f"{c!s:>{ln}s}" for ln, c in zip(lens, r)) for r in rows]

    return "\n".join(header + content)


def write_solution(instance_loc: Path, sol_dir: Path, result: Result):
    with open(sol_dir / (instance_loc.stem + ".sol"), "w") as fh:
        fh.write(f"instance: {instance_loc.name}\n")
        fh.write(f"status: {result.status.value}\n")
        fh.write(f"objective: {result.objective}\n")
        fh.write(f"lower_bound: {result.lower_bound}\n")
        fh.write(f"runtime: {result.runtime}\n")
        fh.write("\n")

        fh.write("task,mode,start,end\n")
        for idx, task in enumerate(result.best.tasks):
            if task is not None:
                fh.write(f"{idx},{task.mode},{task.start},{task.end}\n")
            else:
                fh.write(f"{idx},-1,-1,-1\n")


def _solve(
    instance_loc: Path,
    problem_variant: ProblemVariant,
    solver: str,
    time_limit: float,
    display: bool,
    num_workers_per_instance: int,
    config_loc: Optional[Path],
    sol_dir: Optional[Path],
    permutation_max_jobs: int,
) -> Optional[tuple[str, str, float, float, float]]:
    """
    Solves a single problem instance.
    """
    if config_loc is not None:
        with open(config_loc, "rb") as fh:
            params = tomli.load(fh)
    else:
        params = {}

    if not instance_loc.is_file():
        return

    data = pyjobshop.read(str(instance_loc))
    #if data.permutation and data.num_jobs > permutation_max_jobs:
    #    # For permutation problems we skip instances that are too large.
    #    return

    log_dir = Path(f"/home/bns/thesis/Experiments/{sol_dir.name}/{solver}_{num_workers_per_instance}_{int(time_limit)}/")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = open(f"/home/bns/thesis/Experiments/{sol_dir.name}/{solver}_{num_workers_per_instance}_{int(time_limit)}/{instance_loc.stem}.log", 'w')

    m = Model().from_data(data)
    #p = str(instance_loc)
    #f = p[:p.rfind("/")]
    #P = Path(f + "/est-job-8-1-60" + p[p.rfind("/"):-3] + "sol")

    #print(str(P))
    #if not P.is_file():
    #    return

    #s = eval(open(P).readline())

    #J = max(map(lambda d: d[2], s)) + 1
    #M = max(map(lambda d: d[4], s)) + 1
    #print((M, J), (len(m.resources), len(m.jobs)))

    #fm = [0 for _ in range(M)]
    #fj = [0 for _ in range(J)]

    #sol = []

    def find_mode(modes: list[Mode], task: int, resource: int, duration: int) -> Optional[Mode]:
        return next(
            (i for i, mode in enumerate(modes)
             if mode.task == task
             and mode.duration == duration
             and mode.resources == [resource]),
            None  # default value if no match is found
        )

    #for _, dp, dj, dt, dm in s:
    #    task = m.jobs[dj].tasks[dt]
    #    mode = find_mode(m.modes, task, dm, dp)
    #    if mode == None:
    #        print(f"Error: no mode for task {dj}-{dt} ({task}) on machine {dm} ({dp})")
    #        return
    #    start = max(fm[dm], fj[dj])
    #    end = start + dp
    #    fm[dm] = end
    #    fj[dj] = end
    #    sol.append(TaskData(mode, [dm], start, end))
        
    #print(max(fm), max(fj))
    #sol.sort(key=lambda task: task.mode)

    result = m.solve(
        solver=solver,
        time_limit=time_limit,
        display=display,
        log_file=log_file,
        num_workers=num_workers_per_instance,
    #    initial_solution=Solution(sol),
        **params,
    )
    if sol_dir:
        sol_dir.mkdir(parents=True, exist_ok=True)
        write_solution(instance_loc, sol_dir, result)

    return (
        instance_loc.name,
        result.status.value,
        result.objective,
        result.lower_bound,
        round(result.runtime, 2),
    )


def _check_cpu_usage(
    num_parallel_instances: int, num_workers_per_instance: Optional[int]
):
    """
    Warns if the number of workers per instance times the number of parallel
    instances is greater than the number of available CPU cores
    """
    num_cpus = cpu_count()
    num_workers_per_instance = (
        num_workers_per_instance
        if num_workers_per_instance is not None
        else num_cpus  # uses all CPUs if not set
    )

    if num_workers_per_instance * num_parallel_instances > num_cpus:
        warnings.warn(
            f"Number of workers per instance ({num_workers_per_instance}) "
            f"times number of parallel instances ({num_parallel_instances}) "
            f"is greater than the number of available CPU cores ({num_cpus}). "
            "This may lead to suboptimal performance.",
            stacklevel=2,
        )


def benchmark(instances: list[Path], num_parallel_instances: int, **kwargs):
    """
    Solves the list of instances and prints a table of the results.
    """
    _check_cpu_usage(num_parallel_instances, kwargs.get("num_workers_per_instance"))

    args = sorted(instances)
    func = partial(_solve, **kwargs)

    if len(instances) == 1:
        results = [func(args[0])]
    else:
        results = process_map(
            func,
            args,
            max_workers=num_parallel_instances,
            unit="instance",
        )

    # Filter out the None results (permutation instances that were skipped).
    results = [res for res in results if res is not None]

    dtypes = [
        ("inst", "U37"),
        ("status", "U37"),
        ("obj", float),
        ("lb", float),
        ("time", float),
    ]
    data = np.asarray(results, dtype=dtypes)
    headers = ["Instance", "Status", "Obj.", "LB", "Time (s)"]

    avg_objective = data["obj"].mean()
    avg_runtime = data["time"].mean()

    num_instances = data["status"].size
    num_optimal = np.count_nonzero(data["status"] == "Optimal")
    num_feas = np.count_nonzero(data["status"] == "Feasible") + num_optimal
    num_infeas = num_instances - num_feas

    print("\n", tabulate(headers, data), "\n", sep="")
    print(f"     Avg. objective: {avg_objective:.2f}")
    print(f"      Avg. run-time: {avg_runtime:.2f}s")
    print(f"      Total optimal: {num_optimal}")
    print(f"       Total infeas: {num_infeas}")


def main():
    benchmark(**vars(parse_args()))


if __name__ == "__main__":
    main()
