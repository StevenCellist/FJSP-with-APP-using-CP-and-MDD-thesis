from and_or_read import parse_instance_file_to_tuple
from pyjobshop.Model import Model
from pyjobshop.plot import plot_machine_gantt
import matplotlib.pyplot as plt

file = "afjsp\\m05_j05_or3_f1_01.afjsp"

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
with open('cpoptimizer_output.txt', 'w') as logfile:
  r = m.solve(solver=solver, display=True, log_file=logfile, num_workers=1, time_limit=60)
  
print(f"{file: <30} | ", end = '')
print(f"{round(r.runtime, 2): >10}s | {int(r.objective): >6} | {int(r.lower_bound): >6} ({solver})")

plot_machine_gantt(r.best, m.data(), plot_labels=True)
plt.show()