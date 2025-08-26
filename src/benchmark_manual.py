from pyjobshop.read import read
# from readAlt import read
from pyjobshop.Model import Model
from pyjobshop.plot import plot_machine_gantt
import matplotlib.pyplot as plt
import os

file = r"..\fjsp\fattahi\SFJS3.fjs"

folder = "fjsp\\"
files = [file]

# for root, _, filenames in os.walk(folder):
#     for f in filenames:
#         if f.endswith(".fjs"):
#             # if 'fattahi' in os.path.join(root, f):
#             #     continue
#             # if 'hurink' in os.path.join(root, f):
#             #     continue
#             # if 'kacem' in os.path.join(root, f):
#             #     continue
#             files.append(os.path.join(root, f))

for file in files:
    # print(f"{file: <30} | ", end = '')
    d = read(file, setup=False)
    
    m = Model().from_data(d)
    r = m.solve(solver="cpoptimizer", display=False, num_workers=1, time_limit=10)
    
    # print(f"{round(r.runtime, 2): >10}s | {int(r.objective): >6}")
    print(r)
    
    # sol = list(sorted(r.best.tasks, key = lambda t : t.start))
    # sol = list(map(lambda t : (t.end - t.start, m.tasks[m.modes[t.mode].task].job, m.jobs[m.tasks[m.modes[t.mode].task].job].tasks.index(m.modes[t.mode].task), t.resources[0]), sol))
    # print(sol)

    plot_machine_gantt(r.best, m.data(), plot_labels=True)
    plt.show()