from collections import defaultdict
from pyjobshop.Solution import Solution, TaskData
from pyjobshop.read import read
from pyjobshop.Model import Model, Mode, solve
from typing import Optional

# file = r"C:\Users\steve\Documents\UU\Master\Thesis\Instances\FJSP\1.txt"
file = r"C:\Users\steve\Documents\UU\Master\Thesis\Thesis-code-UU-TNO\src\stage4\fjsp\brandimarte\Mk04.fjs"

d = read(file, setup=False)
m = Model().from_data(d)

ddo = [(1, 2, 0, 5), (2, 3, 0, 6), (1, 1, 0, 5), (2, 11, 0, 3), (1, 11, 1, 5), (2, 2, 1, 2), (1, 1, 1, 5), (1, 2, 2, 6), (5, 9, 0, 4), (2, 12, 0, 5), (2, 4, 0, 6), (2, 2, 3, 3), (6, 8, 0, 0), (1, 12, 1, 2), (2, 5, 0, 5), (9, 10, 0, 7), (1, 12, 2, 5), (1, 5, 1, 2), (1, 5, 2, 6), (5, 13, 0, 4), (1, 13, 1, 5), (5, 7, 0, 3), (1, 5, 3, 5), (6, 8, 1, 0), (2, 13, 2, 3), (1, 8, 2, 2), (5, 12, 3, 4), (5, 5, 4, 3), (6, 10, 1, 0), (7, 6, 0, 5), (9, 4, 1, 6), (5, 7, 1, 4), (1, 4, 2, 2), (3, 10, 2, 1), (9, 8, 3, 7), (2, 7, 2, 2), (5, 14, 0, 3), (2, 7, 3, 5), (6, 3, 1, 0), (2, 14, 1, 6), (2, 8, 4, 3), (1, 7, 4, 5), (1, 8, 5, 5), (2, 10, 3, 3), (2, 8, 6, 6), (7, 2, 4, 2), (1, 2, 5, 2), (6, 9, 1, 0), (9, 5, 5, 7), (2, 9, 2, 6), (6, 0, 0, 0), (7, 8, 7, 2), (5, 9, 3, 3), (2, 8, 8, 2), (9, 4, 3, 7), (9, 7, 5, 6), (6, 11, 2, 0), (7, 5, 6, 2), (1, 5, 7, 5), (6, 1, 2, 0), (9, 14, 2, 7), (1, 1, 3, 2), (9, 0, 1, 6), (2, 1, 4, 2), (3, 14, 3, 1), (1, 0, 2, 2), (2, 1, 5, 5), (1, 14, 4, 6), (6, 5, 8, 0), (2, 0, 3, 3), (2, 1, 6, 6), (7, 4, 4, 2), (6, 9, 4, 0), (2, 4, 5, 2), (9, 0, 4, 7), (9, 3, 2, 6), (1, 3, 3, 2), (6, 14, 5, 0), (5, 4, 6, 3), (3, 0, 5, 1), (5, 3, 4, 3), (5, 0, 6, 4), (1, 0, 7, 5), (7, 6, 1, 2), (7, 11, 3, 0), (1, 6, 2, 5), (2, 6, 3, 5), (1, 6, 4, 2), (8, 11, 4, 0), (2, 11, 5, 6)]

J = max(map(lambda d: d[1], ddo)) + 1
M = max(map(lambda d: d[3], ddo)) + 1
print(M, J)

# Count tasks per job
T = defaultdict(int)
for _, job, task, _ in ddo:
    T[job] = task+1

for job in sorted(T):
    print(f"{T[job]}, ", end = '')
print()

sol = []

fm = [0 for _ in range(M)]
fj = [0 for _ in range(J)]

def find_mode(modes: list[Mode], task: int, resource: int, duration: int) -> Optional[Mode]:
    return next(
        (i for i, mode in enumerate(modes)
         if mode.task == task
         and mode.duration == duration
         and mode.resources == [resource]),
        None  # default value if no match is found
    )

for dp, dj, dt, dm in ddo:
    task = m.jobs[dj].tasks[dt]
    mode = find_mode(m.modes, task, dm, dp)
    if mode == None:
        print(f"Error: no mode for task {dj}-{dt} ({task}) on machine {dm} ({dp})")
    res = m.resources[dm]
    start = max(fm[dm], fj[dj])
    end = start + dp
    fm[dm] = end
    fj[dj] = end
    sol.append(TaskData(mode, res, start, end))

print(max(fm), max(fj))

r = m.solve(solver="ortools", display=False, num_workers=1, time_limit=10, initial_solution=Solution(sol))
# print(f"{file: <30} | ", end = '')
# print(f"{round(r.runtime, 2): >10}s | {int(r.objective): >6}")
print(r)