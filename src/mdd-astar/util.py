import large.machines as M

# number of machines
N = len(M.machines.keys())

# add two values, ignoring -1 values
def plus(a, b):
    if a == -1:
        return -1
    a = 0 if a < 0 else a
    b = 0 if b < 0 else b
    return a + b

def mins(a, b):
    if b == -1:
        return -1
    a = 0 if a < 0 else a
    b = 0 if b < 0 else b
    return a - b

# multiply a matrix by a vector
def mult(m, v):
    n = [[-1 for _ in range(N)] for _ in range(N)]
    for i in range(1, N-1):
        for j in range(N):
            n[i][j] = plus(m[i][j], v[j])
    
    for k in range(N):
        v[k] = max(n[k])

    return v

# shift all actions to the right so that they form a tighly coupled chain
# based on the most delayed action
# e.g. if a job consists of actions on machines A, B and C where B is the 'constraint',
# delay action on machine A by that much such that it couples tightly to B
def padB(m, v):
    # calculate the maximum delay of all actions
    d = [0]*N
    for i in range(N):
        d[i] = mins(v[i], m[i][0])
    
    # add offset to all actions such that they are tightly coupled to most delayed action
    os = max(d)
    for i in range(1, N-1):
        if d[i] != -1:
            v[i] += (os - d[i])

    return v


# helper function to check if a job must be considered
# if the job is already processed (in js), it should be skipped
def jFilter(js, desc):
    (n, _, _) = desc.split('-')
    return n not in js
