#!/usr/bin/python3
import collections


######################################################################
# Data structures supporting fast algorithm
######################################################################
class IntegerSet(object):
    def __init__(self, n, population=[]):
        ans = [-1, n]
        self.answers = [ans]*(n+1)
        for x in population:
            self.add(x)

    def get_n(self):
        return len(self.answers)-1

    n = property(get_n, None)

    def interval(self, x):
        return self.answers[x]

    def successor(self, x):
        return self.answers[x][1]

    def predecessor(self,x):
        return self.answers[x][0]

    def add(self, x):
        ans = self.answers[x]
        a, b = ans
        if b > x:
            if x <= (a+b)//2:
                ans2 = [a, x]
                for i in range(a+1, x+1):
                    self.answers[i] = ans2
                ans[0] = x
            else:
                ans2 = [x, b]
                for i in range(x+1, b+1):
                    self.answers[i] = ans2
                ans[1] = x

    def __iter__(self):
        return IntegerSetIterator(self)

    def __repr__(self):
        return "IntegerSet({},[{}])".format(self.n,
                                             ",".join(str(x) for x in self))

class IntegerSetIterator(object):
    def __init__(self, s):
        self.s = s
        self.x = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.x = self.s.interval(self.x+1)[1]
        if self.x >= self.s.n:
            raise StopIteration()
        return self.x

class MarkedAncestorStruct(object):
    def __init__(self, tree, roots):
        n = len(tree)
        self.tree = tree
        self.intervals = [None]*n

        self.tour = list()
        for r in roots:
            self.euler_tour(r)

        m = len(self.tour)
        self.intset = IntegerSet(m)
        self.marked = [False]*n
        for r in roots:
            self.mark(r)

    def is_marked(self, v):
        return self.marked[v]

    def mark(self, v):
        self.marked[v] = True
        self._mark_node(v)
        for w in self.tree[v][1:]:
            self._mark_node(w)

    def _mark_node(self, w):
        a, b = self.intervals[w]
        self.intset.add(a)
        self.intset.add(b)

    def nearest_marked_ancestor(self, v):
        x = self.intervals[v][1]
        a,b = self.intset.interval(x)
        a = self.tour[b]
        if not self.marked[a]:
            a = self.tree[a][0]
        return a

    def is_marked(self, v):
        return self.marked[v]

    def euler_tour(self, r):
        tour = list()
        stack = list()
        stack.append((r, 1))
        self.intervals[r] = len(self.tour)
        self.tour.append(r)
        while (stack):
            u, i = stack.pop()
            if i < len(self.tree[u]):
                stack.append((u, i+1))
                v = self.tree[u][i]
                stack.append((v, 1))
                self.intervals[v] = len(self.tour)
                self.tour.append(v)
            else:
                self.intervals[u] = (self.intervals[u], len(self.tour))
                self.tour.append(u)
        return tour

######################################################################
# Basic graph algorithm (BFS)
# We use an adjacency list representation of a tree where t[i][0] is
# the parent of i and t[i][1:] are the children of i.
######################################################################
def bfs_forest(al, roots):
    t = [list() for _ in al]
    for v in roots:
        t[v].append(-1)
    q = collections.deque(roots)
    seen = set(roots)
    while len(q) > 0:
        v = q.pop()
        for w in al[v]:
            if w not in seen:
                seen.add(w)
                q.appendleft(w)
                t[w].append(v)  # sets w's parent to v
                t[v].append(w)  # makes w a child of v
    return t

def parent(t, v):
    return t[v][0]

def children(t, v):
    return t[v][1:]

######################################################################
# A few helper functions
######################################################################
""" Get the smallest integer c>=0 that is not in colours """
def free_colour(colours):
    return min(set(range(len(colours)+1)).difference(colours))

""" Split the sequence a into two sequences, the shortest prefix containing x and the longest suffix containing x"""
def split_at(a, x):
    i = a.index(x)
    return a[:i+1], a[i:]


######################################################################
# The algorithm
######################################################################
class tripod_partition(object):
    def __init__(self, al, succ, worst_case=True):
        self.al = al
        self.succ = succ
        roots = [2,1,0]  # has to be a triangular face
        self.t = bfs_forest(al, roots)
        self.worst_case = worst_case

        self.nma = MarkedAncestorStruct(self.t, roots)
        self.colours = [4]*len(self.al)
        for i in range(len(roots)):
            r = roots[i]
            self.set_colour(r, i)

        paths = [[x] for x in roots]
        self.tripods = [paths]
        self.compute(paths)

    """ Compute the partition into tripods """
    def compute(self, paths):
        # paths[0], paths[1] are non-empty, paths[2] may be empty
        if not paths[2]:
            cprime = free_colour([self.colours[paths[0][0]],
                                  self.colours[paths[1][0]]])
            if len(paths[1]) > 1:
                c = self.colours[paths[1][-1]]
                self.colours[paths[1][-1]] = cprime
                self.compute([paths[0], paths[1][:-1], paths[1][-1:]])
                self.colours[paths[1][-1]] = c
            elif len(paths[0]) > 1:
                c = self.colours[paths[0][-1]]
                self.colours[paths[0][-1]] = cprime
                self.compute([paths[0][:-1], paths[0][-1:], paths[1]])
                self.colours[paths[0][-1]] = c
            return

        # Now, paths[i] is non-empty for each i in {0,1,2}

        if self.worst_case:
            # this code guarantees O(n log n) running time
            e = [ (paths[i][-1], paths[(i+1)%3][0]) for i in range(3)]
            tau = self.sperner_triangle_parallel(e)

            # rotate so that tau[i] leads to paths[i]
            tcols = [self.get_colour(tau[i]) for i in range(3)]
            shift = tcols.index(self.colours[paths[0][0]])
            tau = [tau[(shift+i)%3] for i in range(3)]
        else:
            # this code is probably faster in most cases
            e = (paths[0][-1], paths[1][0])
            tau = self.sperner_triangle(e)

        # compute the legs of the tripod
        tripod = [self.tripod_path(tau[i]) for i in range(3)]
        self.tripods.append(tripod)

        # x[i] is point at which tripod[i] attaches to paths[i]
        # p[i] is result of splitting paths[i] at vertex x[i]
        x = list()
        p = list()
        for i in range(3):
            if tripod[i]:
                x.append(parent(self.t, tripod[i][-1]))
            else:
                x.append(tau[i])
            p.append(split_at(paths[i], x[i]))

        # colour the tripod with a colour not used by paths[i]
        c = free_colour([self.get_colour(tau[i]) for i in range(3)])
        for path in tripod:
            for v in path:
                self.set_colour(v, c)

        # recurse on three subproblems
        q = [None]*3
        for i in range(3):
            q[0] = p[i][1]
            q[1] = p[(i+1)%3][0]
            q[2] = tripod[(i+1)%3][::-1] + tripod[i]
            self.compute(q)


    def tripod_path(self, v):
        path = list()
        while not self.nma.is_marked(v):
            path.append(v)
            v = self.t[v][0]
        return path

    def sperner_triangle(self, e):
        c0 = self.get_colour(e[0])
        c1 = self.get_colour(e[1])
        assert(c0 != c1)
        while 1 < 2:
            v = self.succ[e[0]][e[1]]
            c = self.get_colour(v)
            if c != c0 and c != c1:
                return e[0], e[1], v
            if c != c0:
                e = e[0], v
            else:
                e = v, e[1]

    def sperner_triangle_parallel(self, e):
        c0 = [None]*len(e)
        c1 = [None]*len(e)
        for i in range(len(e)):
            c0[i] = self.get_colour(e[i][0])
            c1[i] = self.get_colour(e[i][1])
            assert(c0[i] != c1[i])
        e = e[:]
        while 1 < 2:
            for i in range(len(e)):
                v = self.succ[e[i][0]][e[i][1]]
                c = self.get_colour(v)
                if c != c0[i] and c != c1[i]:
                    return e[i][0], e[i][1], v
                if c != c0[i]:
                    e[i] = e[i][0], v
                else:
                    e[i] = v, e[i][1]

    def set_colour(self, v, c):
        self.nma.mark(v)
        self.colours[v] = c

    def get_colour(self, v):
        a = self.nma.nearest_marked_ancestor(v)
        return self.colours[a]
