#!/usr/bin/env python3
from pymdd.mdd import MDD
import random
import time

# ---- Problem data ----
random.seed(42)
numMachines = 2
numJobs     = 2
numTasks    = 2
numLayers   = numJobs * numTasks

# Generate processing times: t_p[job][task][machine]
# processing time 0 indicates machine ineligible
maxTime = 10
ineligProb = 0.2  # probability a machine cannot process a task

t_p = [
    [
        [random.randint(1, maxTime) if random.random() > ineligProb else 0
         for _ in range(numMachines)]
        for _ in range(numTasks)
    ]
    for _ in range(numJobs)
]

# initial state: (machine ready‐times tuple, completed matrix as tuple of tuples)
first_times = (0,) * numMachines
first_completed = tuple(tuple(0 for _ in range(numTasks)) for _ in range(numJobs))
first_state = (first_times, first_completed)

# Domain: all (job, task, machine) triples
domain = lambda layer: [
    (job, task, m)
    for job in range(numJobs)
    for task in range(numTasks)
    for m in range(numMachines)
]

# Transition function
def transition(state, decision, layer):
    times, completed = state
    job, task, m = decision

    # already done?
    if completed[job][task]:
        return None

    # precedence: predecessor must be done
    if task > 0 and not completed[job][task - 1]:
        return None

    # eligibility via t_p (0 means cannot process)
    duration = t_p[job][task][m]
    if duration == 0:
        return None

    # schedule start when machine is free
    start_time = times[m]
    end_time   = start_time + duration

    # update times
    new_times = list(times)
    new_times[m] = end_time

    # update completed matrix
    new_completed = [list(row) for row in completed]
    new_completed[job][task] = 1
    new_completed = tuple(tuple(row) for row in new_completed)

    return (tuple(new_times), new_completed)

# Cost = increase in makespan
def cost(state, decision, layer, next_state):
    old_times = state[0]
    new_times = next_state[0]
    return max(new_times) - max(old_times)

# always feasible if state is not None
def feasible(state, layer):
    return state is not None

# Merge states with the same completed matrix: keep the one with minimal makespan
def merge(states, layer):
    return min(states, key=lambda s: max(s[0]))

# ---- Build & solve the MDD ----
mymdd = MDD("flexible-job-shop")
t1 = time.time()
mymdd.compile_top_down(
    numLayers,
    domain,
    transition,
    cost,
    first_state,
    feasible
)
t2 = time.time()
mymdd.reduce_bottom_up(merge)
t3 = time.time()
makespan, path = mymdd.find_shortest_path()
t4 = time.time()

print(f"{numJobs:> 2} - {numTasks:> 2} - {numMachines:> 2} | {round(t4 - t3, 2)}s, {round(t3 - t2, 2)}s, {round(t2 - t1, 2)}s")

# Example: print the randomly generated t_p for inspection
print("Generated processing times (0=ineligible):")
for j in range(numJobs):
    for t in range(numTasks):
        print(f"Job {j}, Task {t}: {t_p[j][t]}")

# ---- Output solution ----
# print(mymdd)  
# shortest_path is (list_of_decisions, total_cost), and total_cost == makespan
print("Minimum makespan:", makespan)
print("Optimal schedule (job→machine):", path)

# (Optional) Export to Graphviz
# mymdd.output_to_dot()
