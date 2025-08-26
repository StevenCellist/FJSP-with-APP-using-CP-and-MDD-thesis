from and_or_read import parse_instance_file_to_tuple
from pyjobshop.Model import Model
from pyjobshop.plot import plot_machine_gantt
import matplotlib.pyplot as plt
import os

def compare(file):
  instance = parse_instance_file_to_tuple(file)

  m = Model()

  jobs = [m.add_job() for _ in range(instance.num_jobs)]
  resources = [m.add_machine() for _ in range(instance.num_machines + 1)]

  for job_idx, tasks in enumerate(instance.jobs):
    for task_idx, (k, alts, opt) in enumerate(tasks):
      task = m.add_task(job=jobs[job_idx], name=f"{job_idx}_{task_idx}", optional=opt)

      idx = 0
      for resource_idx, duration in alts:
        m.add_mode(task, resources[resource_idx], duration)
        idx += 1

      if resource_idx == 0:
        if not opt:
          m.mark_flow_source(task)
        else:
          m.mark_flow_sink(task)
      else:
        m.mark_flow_intermediate(task)

  for frm, to, rel in instance.precedences:
    m.add_end_before_start(m.tasks[frm], m.tasks[to])
    
  solver = "ortools"
  r = m.solve(solver=solver, display=False, num_workers=1, time_limit=300)
  print(f"{file: <30} | ", end = '')
  print(f"{round(r.runtime, 2): >10}s | ", end = '')

  # plot_machine_gantt(r.best, m.data(), plot_labels=True)
  # plt.show()

  # full model
  d = m.data()

  # best solution
  sol = enumerate(r.best.tasks)

  # only the tasks that are present
  pres = list(filter(lambda t : t[1].present, sol))
  idcs = [t[0] for t in pres]

  Ts = [d.tasks[i] for i in idcs]
  Ms = list(filter(lambda m : m.task in idcs, d.modes))

  m2 = Model()

  jobs = [m2.add_job() for _ in range(instance.num_jobs)]
  resources = [m2.add_machine() for _ in range(instance.num_machines + 1)]

  for T in Ts:
    task = m2.add_task(job=m2.jobs[T.job], name=T.name)

  for M in Ms:
    m2.add_mode(m2.tasks[idcs.index(M.task)], [m2.resources[i] for i in M.resources], M.duration)

  for frm, to, rel in instance.precedences:
    if frm in idcs and to in idcs:
      m2.add_end_before_start(m2.tasks[idcs.index(frm)], m2.tasks[idcs.index(to)])

  r2 = m2.solve(solver=solver, display=False, num_workers=1, time_limit=300)
  print(f"{round(r2.runtime, 2): >10}s | {round(r.runtime / r2.runtime, 1)}")

  if r.objective != r2.objective:
    print()
    print("Solutions not equal!")

  # plot_machine_gantt(r2.best, m2.data(), plot_labels=True)
  # plt.show()

folder = "afjsp\\"
files = []

for root, _, filenames in os.walk(folder):
  for f in filenames:
    if f.endswith(".afjsp") and "or3" in f:
      compare(os.path.join(root, f))