from and_or_read import parse_instance_file_to_tuple
from pyjobshop.Model import Model
from pyjobshop.plot import plot_machine_gantt
import matplotlib.pyplot as plt
import os

num_workers = 4
time_limit = 60

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
    
  r = m.solve(solver="cpoptimizer", display=False, num_workers=num_workers, time_limit=time_limit)
  print(f"{file: <30} | ", end = '')
  print(f"{round(r.runtime, 2): >10}s ({r.lower_bound} - {r.objective}) | ", end = '')

  # plot_machine_gantt(r.best, m.data(), plot_labels=True)
  # plt.show()

  # full model
  d = m.data()

  m2 = Model().from_data(d)

  r2 = m2.solve(solver="ortools", display=False, num_workers=num_workers, time_limit=time_limit)
  print(f"{round(r2.runtime, 2): >10}s ({r2.lower_bound} - {r2.objective})  | {round(r.runtime / r2.runtime, 1)}  ({round(r.objective / r2.objective, 2)}) ")

  # plot_machine_gantt(r2.best, m2.data(), plot_labels=True)
  # plt.show()

folder = "afjsp\\"
files = []

for root, _, filenames in os.walk(folder):
  for f in filenames:
    if f.endswith(".afjsp"):
      compare(os.path.join(root, f))