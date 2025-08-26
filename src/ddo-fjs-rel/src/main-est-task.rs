#![allow(dead_code)]
#![allow(non_snake_case)]

use ddo::*;
use std::sync::Arc;
use std::time::Duration;
use std::time::Instant;
use std::env;
use std::error::Error;

/// Our DP state: (layer, machine-finish-times, completed tasks per job)
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct FjsState {
    layer: usize,
    v: Vec<isize>,      // intersection of paths
    u: Vec<isize>,      // union of paths
    f: Vec<usize>,      // machine times
    t: Vec<usize>,      // task times per job
    p: Vec<isize>,      // tasks progress per job
    j: Vec<usize>,      // tasks in each job
    J: usize,           // total number of jobs
    O: Vec<Vec<Vec<(usize, usize)>>>,   // all (machine, time) options
    est: isize,         // estimated makespan
}

/// The full FJS instance
struct Fjs {
    j: Vec<usize>,
    J: usize,
    M: usize,
    O: Vec<Vec<Vec<(usize, usize)>>>,
    s: Vec<Vec<usize>>,
}

impl Problem for Fjs {
    type State = FjsState;

    /// total number of layers = jobs x tasks
    fn nb_variables(&self) -> usize {
        self.j.iter().sum::<usize>()
    }

    /// For each layer, enumerate all (job,task,machine) triples
    fn for_each_in_domain(&self,
        var: Variable, state: &Self::State, f: &mut dyn DecisionCallback)
    {
        for job in 0..self.J {
            for raw in state.v[job]+1..=state.u[job]+1 {
                let task = raw as usize;
                // only if this job still has a task `task` waiting
                if task < self.j[job] {
                    // iterate *only* over the allowed (machine, p_time) pairs
                    for &(machine, p_time) in &self.O[job][task] {
                        f.apply(Decision {
                            variable: var,
                            // pack (job, task, machine) into your isize
                            value: ((p_time << 24) | (job << 16) | (task << 8) | machine) as isize,
                        });
                    }
                }
            }
        }
    }

    fn initial_state(&self) -> Self::State {
        FjsState {
            layer: 0,
            v: vec![-1; self.J],
            u: vec![-1; self.J],
            f: vec![0; self.M],
            t: vec![0; self.J],
            J: self.J,
            j: self.j.clone(),
            p: vec![-1; self.M],
            O: self.O.clone(),
            est: isize::MIN,
        }
    }

    fn initial_value(&self) -> isize { 0 }

    fn transition(&self,
        state: &Self::State, dec: Decision) -> Self::State
    {
        let (_i, dur, job, task, m) = unpack_decision(dec);
        let mut new = state.clone();
        new.layer += 1;
        
        let mut m_time = new.f[m];      // earliest machine time
        let     j_time = new.t[job];    // earliest job time

        let task_num: usize = self.j[..job].iter().sum::<usize>() + task;
        if new.p[m] > -1 {
            let num_tasks: usize = self.j.iter().sum();
            let prev_idx = (new.p[m] as usize) + m * num_tasks;
            m_time += self.s[prev_idx][task_num];
            mu_time += self.s[prev_idx][task_num];
        }
        new.p[m] = task_num as isize;

        new.v[job] = task as isize;
        new.u[job] = task as isize;
        
        new.f[m] = m_time.max(j_time) + dur;    // can only start after previous is finished
        new.t[job] = new.f[m];                  // save finish time of current task

        let mut clone = new.clone();

        // initialize next task index for each job
        let mut next_task = vec![0; self.J];
        for job in 0..self.J {
            next_task[job] = new.v[job] + 1;  // first raw to try for this job
        }

        // keep going until no job has any remaining tasks
        let mut still_work = true;
        while still_work {
            still_work = false;

            for job in 0..self.J {
                // if this job still has a task available...
                if (next_task[job] as usize) < self.j[job] {
                    still_work = true;

                    let task = next_task[job] as usize;

                    // iterate *only* over the allowed (machine, p_time) pairs
                    let mut latest = 0;
                    for &(m, p) in &self.O[job][task] {
                        clone.f[m] = clone.f[m].max(clone.t[job]) + p;
                        latest = latest.max(clone.f[m]);
                    }
                    clone.t[job] = latest;

                    // advance to the next task for this job
                    next_task[job] += 1;
                }
            }
        }
        let est_mk = *clone.f.iter().max().unwrap();
        new.est = -(est_mk as isize);
        
        new
    }

    fn transition_cost(&self,
        _src: &Self::State, next: &Self::State, _dec: Decision) -> isize
    {
        let old_mk = *_src.f.iter().max().unwrap();
        let new_mk = *next.f.iter().max().unwrap();
        -((new_mk - old_mk) as isize)
    }

    fn next_variable(&self, depth: usize,
        _next_layer: &mut dyn Iterator<Item=&Self::State>)
        -> Option<Variable>
    {
        if depth < self.nb_variables() {
            Some(Variable(depth))
        } else {
            None
        }
    }
}

fn pack_decision(v: usize, p: usize, j: usize, t: usize, m: usize) -> Decision {
    Decision { variable: Variable(v), value: ((p << 24) | (j << 16) | (t << 8) | m) as isize }
}

// unpack our packed decision back into job,task,machine
fn unpack_decision(d: Decision) -> (usize,usize,usize,usize,usize) {
    let Decision { variable: v, value: x } = d;
    let y = x as usize;
    let m    = y & 0xff;
    let task = (y >> 8) & 0xff;
    let job  = (y >> 16) & 0xff;
    let dur  = y >> 24;
    (v.id(), dur, job, task, m)
}

/// Relaxation: merge by taking element-wise min of f and max of v.
struct FjsRelax;
impl Relaxation for FjsRelax {
    type State = FjsState;
    fn merge(&self, states: &mut dyn Iterator<Item=&Self::State>) -> Self::State {
        let mut merged = states.next().unwrap().clone();
        for s in states {
            for i in 0..merged.f.len() {
                merged.f[i] = merged.f[i].min(s.f[i]);
            }
            for j in 0..merged.t.len() {
                merged.t[j] = merged.t[j].min(s.t[j]);
            }
            for k in 0..merged.v.len() {
                merged.v[k] = merged.v[k].min(s.v[k]);
                merged.u[k] = merged.u[k].max(s.u[k]);
            }
        }
        let mut clone = merged.clone();

        // initialize next task index for each job
        let mut next_task = vec![0; merged.J];
        for job in 0..merged.J {
            next_task[job] = merged.v[job] + 1;  // first raw to try for this job
        }

        // keep going until no job has any remaining tasks
        let mut still_work = true;
        while still_work {
            still_work = false;

            for job in 0..merged.J {
                // if this job still has a task available...
                if (next_task[job] as usize) < merged.j[job] {
                    still_work = true;

                    let task = next_task[job] as usize;

                    // iterate *only* over the allowed (machine, p_time) pairs
                    let mut latest = 0;
                    for &(m, p) in &merged.O[job][task] {
                        clone.f[m] = clone.f[m].max(clone.t[job]) + p;
                        latest = latest.max(clone.f[m]);
                    }
                    clone.t[job] = latest;

                    // advance to the next task for this job
                    next_task[job] += 1;
                }
            }
        }
        let est_mk = *clone.f.iter().max().unwrap();
        merged.est = -(est_mk as isize);

        merged
    }
    fn relax(&self,
        _src: &Self::State,
        _dst: &Self::State,
        _merged: &Self::State,
        _dec: Decision,
        cost: isize,
    ) -> isize {
        cost
    }
    // fn fast_upper_bound(&self, state: &Self::State) -> isize {

    // }
}

/// Dominance: we group by “v” vector, and say s1 dominates s2 if
/// s1.f[i] ≤ s2.f[i] for all machines.
struct FjsDom;
impl Dominance for FjsDom {
    type State = FjsState;
    type Key   = Vec<isize>;
    fn get_key(&self, state: Arc<Self::State>) -> Option<Self::Key> {
        Some(state.v.clone())
    }
    fn nb_dimensions(&self, _state: &Self::State) -> usize {
        _state.f.len()
    }
    fn get_coordinate(&self, state: &Self::State, dim: usize) -> isize {
        -(state.f[dim] as isize)
    }
    fn use_value(&self) -> bool { false }
}

/// Ranking: prefer smaller makespan
struct FjsRank;
impl StateRanking for FjsRank {
    type State = FjsState;
    fn compare(&self, a: &Self::State, b: &Self::State) -> std::cmp::Ordering {
        a.est.cmp(&b.est)
    }
}

fn main() {
    // Collect command line arguments

    #[cfg(debug_assertions)]
    let args = vec![
        "ddo-fjs-rel".to_string(),
        "C:\\Users\\steve\\Documents\\UU\\Master\\Thesis\\Thesis-code-UU-TNO\\src\\stage4\\fjsp\\fattahi\\SFJS10.fjs".to_string(),
        "1".to_string(),
        "1".to_string(),
    ];

    #[cfg(not(debug_assertions))]
    let args: Vec<String> = env::args().collect();

    if args.len() <= 3 {
        eprintln!("Usage: cargo run -- <M> <J> <num_tasks>");
        std::process::exit(1);
    }

    let path = &args[1];
    let fjsp = read_fjsp(path);
    let (M, J, j, O, s) = match fjsp {
        Ok(vals) => vals,
        Err(e) => {
            eprintln!("Failed to read instance file: {}", e);
            std::process::exit(1);
        }
    };
    
    let problem = Fjs { M, J, j, O, s };
    let relaxation = FjsRelax;
    let ranking = FjsRank;
    let dominance  = SimpleDominanceChecker::new(FjsDom, problem.nb_variables());
    let width = Box::new(FixedWidth(args[2].parse().expect("Invalid width")));//Box::new(FixedWidth(1000));
    let cutoff = TimeBudget::new(Duration::from_secs(args[3].parse().expect("Invalid timeout"))); //NoCutoff;
    let mut fringe = NoDupFringe::new(MaxUB::new(&ranking));

    let mut solver = DefaultCachingSolver::custom(//SeqCachingSolverFc::new(
        &problem,
        &relaxation,
        &ranking,
        width.as_ref(),
        &dominance,
        &cutoff,
        &mut fringe,
        8
    );

    let start = Instant::now();
    let Completion{ is_exact, best_value: _ } = solver.maximize();
    
    let duration = start.elapsed();
    let upper_bound = solver.best_upper_bound();
    let lower_bound = solver.best_lower_bound();
    let gap = solver.gap();
    let best_solution  = solver.best_solution().map(|mut decisions|{
        decisions.sort_unstable_by_key(|d| d.variable.id());
        decisions.iter().map(|&d| unpack_decision(d)).collect::<Vec<_>>()
    });

    println!("Exact:      {}",            is_exact);
    println!("Duration:   {:.3} seconds", duration.as_secs_f32());
    println!("Upper Bnd:  {}",            -upper_bound);
    println!("Lower Bnd:  {}",            -lower_bound);
    println!("Gap:        {:.3}",         gap);
    println!("Solution:   {:?}",          best_solution.unwrap_or_default());
    // println!("Widths:     {:?}",          solver.widths())
}

/// Read a Flexible‐Job‐Shop instance in either the “flat” or the “matrix” format,
/// optionally including Sequence-Dependent Setup Times (s).
pub fn read_fjsp<P: AsRef<std::path::Path>>(
    path: P,
) -> Result<
    (
        usize,                                        // M
        usize,                                        // J
        Vec<usize>,                                   // j
        Vec<Vec<Vec<(usize, usize)>>>,                // O
        Vec<Vec<usize>>,                              // s matrix (rows = total_alternatives, cols = total_operations)
    ),
    Box<dyn Error>,
> {
    // Read all non-blank lines
    let content = std::fs::read_to_string(path)?;
    let lines: Vec<&str> = content.lines()
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .collect();
    let mut pos = 0;

    // Helper: get next line or error
    fn get_line<'a>(lines: &'a [&str], pos: &mut usize, label: &str) -> Result<&'a str, Box<dyn Error>> {
        if *pos < lines.len() {
            let l = lines[*pos];
            *pos += 1;
            Ok(l)
        } else {
            Err(format!("unexpected EOF parsing {}", label).into())
        }
    }

    // Parse header
    let first = get_line(&lines, &mut pos, "header")?;
    let toks: Vec<&str> = first.split_whitespace().collect();

    let (J, M, j, O) = if toks.len() == 1 {
        // MATRIX format
        let J: usize = toks[0].parse()?;
        let M: usize = get_line(&lines, &mut pos, "machines")?.parse()?;
        let j: Vec<usize> = get_line(&lines, &mut pos, "tasks")?
            .split_whitespace().map(str::parse).collect::<Result<_,_>>()?;
        let total_ops: usize = j.iter().sum();
        let mut rows = Vec::with_capacity(total_ops);
        for _ in 0..total_ops {
            let row = get_line(&lines, &mut pos, "op row")?
                .split_whitespace().map(str::parse).collect::<Result<Vec<_>,_>>()?;
            if row.len() != M {
                return Err(format!("expected {} cols, got {}", M, row.len()).into());
            }
            rows.push(row);
        }
        let mut opts = Vec::with_capacity(J);
        let mut ridx = 0;
        for &t in &j {
            let mut ops = Vec::with_capacity(t);
            for _ in 0..t {
                let mut alts = Vec::new();
                for (m, &p) in rows[ridx].iter().enumerate() {
                    if p > 0 { alts.push((m, p)); }
                }
                ridx += 1;
                ops.push(alts);
            }
            opts.push(ops);
        }
        (J, M, j, opts)
    } else {
        // FLAT format
        let header: Vec<usize> = toks.iter().take(2)
            .map(|&s| s.parse()).collect::<Result<_,_>>()?;
        if header.len() < 2 { return Err("flat header: need J M".into()); }
        let (J, M) = (header[0], header[1]);
        let mut j = Vec::with_capacity(J);
        let mut opts = Vec::with_capacity(J);
        for _ in 0..J {
            let parts: Vec<usize> = get_line(&lines, &mut pos, "job line")?
                .split_whitespace().map(str::parse).collect::<Result<_,_>>()?;
            let mut it = parts.into_iter();
            let t = it.next().ok_or("missing task-count")?;
            j.push(t);
            let mut ops = Vec::with_capacity(t);
            for _ in 0..t {
                let a = it.next().ok_or("missing alt-count")?;
                let mut alts = Vec::with_capacity(a);
                for _ in 0..a {
                    let m = it.next().ok_or("missing machine idx")?;
                    let p = it.next().ok_or("missing proc time")?;
                    alts.push((m-1, p));
                }
                ops.push(alts);
            }
            opts.push(ops);
        }
        (J, M, j, opts)
    };

    // Prepare SDST default
    let total_ops: usize = j.iter().sum();
    let total_alts = M * total_ops;
    let mut s = vec![vec![0; total_ops]; total_alts];

    // Try parse SDST block if enough lines remain
    let rem = lines.len().saturating_sub(pos);
    if rem >= total_alts {
        let mut ok = true;
        for i in 0..total_alts {
            if lines[pos + i].split_whitespace().count() != total_ops {
                ok = false;
                break;
            }
        }
        if ok {
            for i in 0..total_alts {
                let row: Vec<usize> = get_line(&lines, &mut pos, "s")?
                    .split_whitespace().map(str::parse).collect::<Result<_,_>>()?;
                s[i] = row;
            }
        }
    }

    Ok((M, J, j, O, s))
}