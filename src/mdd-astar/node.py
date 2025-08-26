import large.machines as M
import large.jobs as J
from util import *

class State:
    def __init__(self, val = 0):
        # serial number
        self._val = val

        # selected jobs
        self._j = set()
        
        # path taken up until this state
        self._p = []
        
        # finish time vector of machines given the selected jobs
        self._v = [0 for _ in range(len(M.machines.keys()))]

        # last performed actions per machine
        self._a = ['' for _ in range(len(M.machines.keys()))]

        # string-representation of schedule
        self._g = ['' for _ in range(len(M.machines.keys()))]
        return
    
    def __copy__(self):
        newState = State()
        newState._j = self._j.copy()
        newState._p = self._p[:]
        newState._v = self._v[:]
        newState._a = self._a[:]
        newState._g = self._g[:]
        return newState
    
    def add(self, opt):
        (n, m, l) = opt.split('-')
        
        # if job already processed, stop
        if n in self._j:
            return False
        
        self._j.add(n)
        self._p += [f"{n}-{m}-{l}"]
        job = J.jobs[n][m]['machines'][int(l)]
        
        for i in range(1, len(job['M']) - 1):
            if self._a[job['M'][i]] == '':
                continue
            prevI = M.machines[job['M'][i]].index(self._a[job['M'][i]])
            currI = M.machines[job['M'][i]].index(J.jobs[n][m]['actions'][i])
            self._v[job['M'][i]] += M.setup[job['M'][i]][currI][prevI]

            # printing
            self._g[job['M'][i]] += '-' * M.setup[job['M'][i]][currI][prevI]

        # printing
        before = self._v[:]

        self._v = mult(job['matrix'], self._v)
        self._v = padB(job['matrix'], self._v)

        # printing
        for i in range(N):
            l = self._v[i] - before[i] - job['matrix'][i][i]
            self._g[i] += ' ' * l
            self._g[i] += str(n) * job['matrix'][i][i]

        for i in range(1, len(job['M']) - 1):
            self._a[job['M'][i]] = J.jobs[n][m]['actions'][i]

        return True
    
    def __repr__(self):
        s = ""
        s += ('-' * (self.makespan + 5)) + "\n"
        for i in range(1, N - 1):
            s += (self._g[i]) + " " * (self.makespan - self._v[i]) + f" ({self._v[i]:2})\n"
        s += ('-' * (self.makespan + 5))
        return(s)
    
    @property
    def makespan(self):
        return max(self._v)
    
    @property
    def jobs(self):
        return self._j
    
    @property
    def path(self):
        return self._p
    
    @property
    def vector(self):
        self._v = [0 if self._v[i] == -1 else self._v[i] for i in range(len(self._v))]
        return self._v