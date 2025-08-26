import copy

import large.machines as M
import large.jobs as J
from node import State
from util import *

# number of machines
N = len(M.machines.keys())

# first, preprocess all jobs
jobs = {}
for (n, j) in J.jobs.items():                                   # number of job, job
    for (m, r) in j.items():                                    # number of recipe, recipe
        for (l, p) in enumerate(r['machines']):                 # number of production line, production line
            
            # retrieve travel time from machine(lastAction) to machine(nextAction)
            travels = [0 for _ in range(len(p["M"]))]
            for i in range(len(p["M"])):
                travels[i] = M.travel[p["M"][i]][p["M"][i-1]]

            # empty -1 matrix
            matrix = [[-1 for _ in range(N)] for _ in range(N)] 

            # set diagonal to 0
            for i in range(N):
                matrix[i][i] = 0

            # set all processing times on diagonal
            for i in range(len(p["M"])):
                matrix[p["M"][i]][p["M"][i]] = p["P"][i]
            
            # set all off-diagonal values (M[i][j] is the time from starting i to finishing j)
            for i in range(len(p["M"])):
                for j in range(0, i):
                    matrix[p["M"][i]][p["M"][j]] =  p["P"][i]           # processing time of nextAction
                    matrix[p["M"][i]][p["M"][j]] += sum(p["W"][0:i+1])  # nextAction must wait e.g. until first batch of input is released from last action
                    matrix[p["M"][i]][p["M"][j]] += sum(travels[0:i+1]) # this input has to travel from machine(lastAction) to machine(nextAction) as well
                    # matrix[p["M"][i-1]][p["M"][j]]                    # (unused: start when last one finished)

            # set source/sink values to 0 if set (they are considered unrestricted)
            for i in range(N):
                matrix[0]  [i] = 0 if matrix[0]  [i] != -1 else -1
                matrix[N-1][i] = 0 if matrix[N-1][i] != -1 else -1
            
            # save matrix in the main job structure
            p['matrix'] = matrix
            
            # save n-m-l job as an instance under its unique name
            jobs[f"{n}-{m}-{l}"] = p

def levelList(lst, value):
    # Pair each element with its original index
    indexed_lst = [(v, i) for i, v in enumerate(lst)]
    
    # Sort the list based on values
    indexed_lst.sort()
    n = len(indexed_lst)
    
    # Incrementally level elements until we exhaust the value
    i = 0
    while value > 0 and i < n - 1:
        # Determine the difference to the next element in the sorted list
        diff = indexed_lst[i + 1][0] - indexed_lst[i][0]
        # Total amount needed to make indexed_lst[i] equal to indexed_lst[i+1]
        required = diff * (i + 1)
        
        if value >= required:
            # Level up all elements from 0 to i to the level of indexed_lst[i+1]
            for j in range(i + 1):
                indexed_lst[j] = (indexed_lst[j][0] + diff, indexed_lst[j][1])
            value -= required
        else:
            # Distribute the remaining value equally among elements from 0 to i
            equal_share = value // (i + 1)
            remainder = value % (i + 1)
            
            for j in range(i + 1):
                indexed_lst[j] = (indexed_lst[j][0] + equal_share, indexed_lst[j][1])
            for j in range(remainder):
                indexed_lst[j] = (indexed_lst[j][0] + 1, indexed_lst[j][1])
                
            value = 0
        i += 1
    
    # If there's any value left, distribute it among all elements
    if value > 0:
        equal_share = value // n
        remainder = value % n
        
        for j in range(n):
            indexed_lst[j] = (indexed_lst[j][0] + equal_share, indexed_lst[j][1])
        for j in range(remainder):
            indexed_lst[j] = (indexed_lst[j][0] + 1, indexed_lst[j][1])
    
    # Restore the original order based on the indices
    indexed_lst.sort(key=lambda x: x[1])
    
    # Extract the leveled values
    leveled_lst = [val for val, _ in indexed_lst]
    
    return leveled_lst

def addNiv(vector, specs, times):
    for (s, t) in zip(specs, times):
        machines = dict(filter(lambda f : s in f[1], M.machines.items())).keys()
        oldValues = [vector[m] for m in machines]
        newValues = levelList(oldValues, t)
        for (i, m) in enumerate(machines):
            vector[m] = newValues[i]
            
    return vector

def h(state):
    # get all options that could be added
    s = set(J.jobs.keys())
    u = s.difference(state.jobs)
    V = state.vector
    
    # first, process all jobs that have only one recipe
    for k in sorted(u):
        if len(J.jobs[k]) > 1:
            continue
        
        vs = [addNiv(V[:], J.jobs[k]['a']['actions'], J.jobs[k]['a']['machines'][i]['P']) for i in range(len(J.jobs[k]['a']['machines']))]

        # Find the list with the minimum 'maximum' values using tuple comparison
        idx = min(range(len(vs)), key=lambda i: sorted(vs[i], reverse=True))
        V = vs[idx]
        
    # next, process all jobs that have multiple recipes
    for k in sorted(u):
        if len(J.jobs[k]) == 1:
            continue
        
        vs = []
        for r in J.jobs[k]:
            vs += [addNiv(V[:], J.jobs[k][r]['actions'], J.jobs[k][r]['machines'][i]['P']) for i in range(len(J.jobs[k][r]['machines']))]

        # Find the list with the minimum 'maximum' values using tuple comparison
        idx = min(range(len(vs)), key=lambda i: sorted(vs[i], reverse=True))
        V = vs[idx]
    
    return max(V) - state.makespan

def aStar():
    start = State(0)
    num = 1

    openSet = dict()
    gScore = dict()
    fScore = dict()

    openSet[start._val] = start
    gScore[start._val] = 0
    fScore[start._val] = gScore[start._val] + h(start)

    while openSet.keys():
        minF = min(fScore, key = fScore.get)
        current = openSet.pop(minF)
        fScore.pop(minF)
        gScore.pop(minF)
        if len(current.path) == len(J.jobs.keys()):
            print(f"States calculated: {num}")
            print(current.path)
            print(current)
            return

        # check which jobs are still candidates, i.e. neighbours
        # by filtering those descriptors that are not covered by s.jobs
        opts = list(filter(lambda d : jFilter(current.jobs, d), jobs))
        
        # add a copy of the state into the queue 
        # with each copy adding one of the candidates
        for opt in opts:
            neighbor = copy.copy(current)
            neighbor._val = num
            num += 1
            neighbor.add(opt)
            gScore[neighbor._val] = neighbor.makespan
            fScore[neighbor._val] = neighbor.makespan + h(neighbor)
            openSet[neighbor._val] = neighbor

    return

if __name__ == "__main__":
    aStar()

    # # start with single empty state
    # inState = State()
    # queue = [inState]
    # done = []
    # span = []

    # # as long as there are unfinished states, process these
    # while queue:
    #     # get first item from list
    #     s = queue.pop()
        
    #     # if this state covers all jobs, it is done
    #     if len(s.path) == len(J.jobs.keys()):
    #         done += [s]
    #         span += [s.makespan]
    #         continue
        
    #     # check which jobs are still candidates 
    #     # by filtering those descriptors that are not covered by s.jobs
    #     opts = list(filter(lambda d : jFilter(s.jobs, d), jobs))
        
    #     # add a copy of the state into the queue 
    #     # with each copy adding one of the candidates
    #     for opt in opts:
    #         s2 = copy.copy(s)
    #         s2.add(opt)
    #         queue.append(s2)

    # # calculate minimum makespan and its corresponding completed states
    # minSpan = min(span)
    # best = list(filter(lambda compl : True if compl.makespan == minSpan else False, done))

    # # print the interesting info
    # print(f"Paths traced: {len(done)}")
    # print(f"Minimum makespan found: {min(span)}")
    # print(f"This has been achieved by {len(best)} paths:")
    # for (i, state) in enumerate(best):
    #     print(f"Path {i+1}:")
    #     print(f"{state.path}")
    #     print(state)
    #     print()


# """ ideas or questions
# - what do we define as equal states?
# - can we define dominating states?

# - the same 'main' jobs are covered
# - none of the machines finishes later than in the other state
# - identical last actions per machine

# """