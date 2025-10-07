## Supporting files

The files in this directory can be used to reproduce or extend results from the paper.

---

- `and-or/` contains files that can generate, read and benchmark FJSP instances with And/Or-networks following the description by Kis (2003).
- `ddo-fjs-app` contains an MDD implementation in DDO for FJSP-APP instances. It can be run through `cargo run --release`, or using the `run_all.sh` file to benchmark a directory with instances. `cargo` will automatically pull all required dependencies.
- `ddo-fjs-blk` contains an MDD implementation in DDO for blocking FJSP instances. It can be run through `cargo run --release`, or using the `run_all.sh` file to benchmark a directory with instances. `cargo` will automatically pull all required dependencies.
- `ddo-fjs-rel` contains an MDD implementation in DDO for FJSP instances, also supporting SDST. It also contains additional source files for the different ranking functions. It can be run through `cargo run --release`, or using the `run_all.sh` file to benchmark a directory with instances. `cargo` will automatically pull all required dependencies.
- `mdd-astar/` contains a pure Python implementation of exact MDDs that are constructed through the A* principle. This is an early Proof-of-Concept.
- `PyJobShop/` contains a modified copy of PyJobShop that includes And/Or-support among others.
- `read/` is a drop-in replacement for PyJobShop's `read`-directory that also supports SDST and And/Or-instances.
- `benchmark.py` can be used with `uv run` (and the `read/` directory) to benchmark a directory with instances and return an overview with useful results such as bounds and runtimes. `uv` will automatically pull all required dependencies. _However_, it will also pull an upstream version of PyJobShop which is different from the version used in our the paper. See the PyJobShop directory for the used version.
- `benchmark_manual.py` can be used to benchmark single files or directories, without any additional processing.
- `cutoff_cp_optimizer.py` is able to parse a directory with CP Optimizer search logs and generate graphs displaying the progression of upper and louwer bounds for different cutoff times.
- `cutoff_ddo.py` is able to parse DDO logs generated using `run_all.sh` files and generate graphs displaying the progression of upper and louwer bounds for different cutoff times.
- `ddo_to_cp.py` can be used to parse (DDO-FJSP) solution files and use these as a warmstart to CP solvers. Works in tandem with `log_to_sol.py`.
- `get_stats.py` can be used to generate quick statistics on a directory with instances such as the minimum and maximum number of machines, jobs, tasks etc.
- `generate_app.py` can be used to generate APP instances from normal FJSP instances as described in our research.
- `log_parser.py` is able to parse DDO logs generated using `run_all.sh` files and returns an overview with useful results such as bounds and runtimes.
- `log_to_sol.py` is able to parse DDO logs generated using `run_all.sh` files and parses the solutions into separate files for warmstarting CP solvers. Works in tandem with `ddo_to_cp.py`.
- `pymdd_fjsp.py` is a pure Python implementation of exact MDDs in PyMDD using instances generated on-the-fly.
- `results_cp_optimizer.py` is able to parse a directory with CP Optimizer search logs and generate tables with average values regarding bounds, runtime etc.
- `results_or_tools.py` is able to parse a directory with OR-Tools search logs and generate tables with average values regarding bounds, runtime etc.

## Reproducing results (`uv run`)
Please refer to the documentation of PyJobShop's Experiments for full information: https://github.com/PyJobShop/Experiments?tab=readme-ov-file#reproducing-results

A copy of this documentation that matches the version here is shown below:

To reproduce all benchmark results, use the `benchmark.py` script which interfaces with the data. For example, to solve all FJSP instances using OR-Tools with a 10-second time limit and 8 cores per instance, run:

```
uv run benchmark.py ../instances/FJSP/*.txt \
  --problem_variant FJSP \
  --solver ortools \
  --time_limit 10 \
  --num_workers_per_instance 8 \
  --display
```

For more configuration options, you can view the help documentation:

```
uv run benchmark.py --help
```