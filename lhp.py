#!/usr/bin/python3
"""Layered H-partitions

An implementation of layered H-partitions for planar graphs, i.e., the Product Structure Theorem for planar graphs.  The algorithm implemented here closely follows the algorithm described in this paper: https://arxiv.org/abs/2004.02530
"""
import collections

"""A light wrapper around list that allows for constant-time slices."""
class list_slice(object):
    def __init__(self, a, start = None, stop=None):
        if start == None:
            start = 0
        if stop == None:
            stop = len(a)
        self.a, self.start, self.stop = a, start, stop

    def __len__(self):
        return self.stop-self.start

    def __getitem__(self, i):
        if type(i) == slice:
            if i.step != 1 and i.step != None:
                raise IndexError("only steps of 1 are supported")
            start, stop = i.start, i.stop
            if start == None:
                start = 0
            elif start < 0:
                start = len(self) + start
            if stop == None:
                stop = len(self)
            elif stop < 0:
                stop = len(self) + stop
            return list_slice(self.a, self.start + start, self.start + stop)
        i = len(self)+i if i < 0 else i
        return self.a[self.start+i]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __repr__(self):
        return "list_slice([{}])".format(", ".join(repr(x) for x in self))

    def untranslate(self, i):
        """Convert from an into self.a to an index into self"""
        return i - self.start

"""Store a set of integers

This data structure stores integers from the set -1,..,n so that integers can be inserted and the predecessor and successor of any integer can be found in constant time.  Any sequence of insertions takes O(n log n) time.
"""
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
        x = -1
        x = self.successor(-1)
        while x < self.n:
            yield x
            x = self.successor(x+1)

    def __repr__(self):
        return "IntegerSet({},[{}])".format(self.n,
                                             ",".join(str(x) for x in self))

"""Nearest Marked Ancestor data Structure

Preprocesses a rooted tree so that we can mark any node whose parent is marked and so that we can find the nearest marked ancestor of any node in constant time. Any sequence of mark operations takes O(n log n) time.

The input is a forest with vertex set 0,...,n-1 and list of roots that should be initially marked.  The input format for the forest (tree) is a list of length n, where tree[i][0] is the parent of i (or -1 if i is a root) and tree[i][1:] are the children of i.

This performs an Euler tour of the forest so that each edge e gets mapped to an interval [a(e),b(e)].  If some edge e' is a descendant of e than [a(e'),b(e')] is strictly contained in [a(e),b(e)].
"""
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

"""An implementation of breadth-first-search

This implementation takes a list of roots that form the depth-0 nodes of the breadth-first-search forest.  The output format is compatible with the MarkedAncestorStruct structure.
"""
def bfs_forest(succ, roots):
    t = [list() for _ in succ]
    for v in roots:
        t[v].append(-1)
    q = collections.deque(roots)
    seen = set(roots)  # TODO: array would be faster
    while len(q) > 0:
        v = q.pop()
        for w in succ[v]:
            if w not in seen:
                seen.add(w)
                q.appendleft(w)
                t[w].append(v)  # sets w's parent to v
                t[v].append(w)  # makes w a child of v
    return t


# Unused, more documentation about the the forest representation we use
def parent(t, v):
    return t[v][0]

# Unused, more documentation about the the forest representation we use
def children(t, v):
    return t[v][1:]

# Taken from here: https://stackoverflow.com/questions/652276/is-it-possible-to-create-anonymous-objects-in-python
class AnonObj(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


"""Get the smallest integer c>=0 that is not in colours"""
def free_colour(colours):
    return min(set(range(len(colours)+1)).difference(colours))

"""The tripod partition class

This is the object that the algorithm constructs from a planar triangulation.  The input is a planar triangulation with vertex set 0,...,n-1 [where n := len(succ)].  The argument succ is a list of dictionaries so that succ[u][v] is the third vertex w of the triangle uvw that lies to the left of the directed edge uv.  The structure obtained from this is described in the README
"""
class tripod_partition(object):
    def __init__(self, succ, worst_case=True, roots=[2,1,0]):
        self.succ = succ
        self.worst_case = worst_case

        self.t = bfs_forest(succ, roots)
        self.nma = MarkedAncestorStruct(self.t, roots)

        self.tripod_map = [None] * len(succ)
        self.index_map = [None] * len(succ)  # allows constant time path splits
        self.colours = [4] * len(succ)
        for i in range(len(roots)):
            self.tripod_map[roots[i]] = (0, i, 0)
            self.index_map[roots[i]] = 0
            self.set_colour(roots[i], i)

        paths = [[x] for x in roots]
        self.tripods = [paths]
        self.tripod_colours = [3]
        paths = [list_slice(p) for p in paths]
        self.tripod_tree = [[1]]

        self.compute(paths)

        # these are used only during the computation
        del self.index_map
        self.nma = AnonObj(nearest_marked_ancestor = lambda x: x)

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
        ti = len(self.tripods)
        self.tripods.append(tripod)

        # colour the tripod with a colour not used by tau
        c = free_colour([self.get_colour(tau[i]) for i in range(3)])
        self.tripod_colours.append(c)

        # map and colour the vertices in the tripod
        for i in range(3):
            path = tripod[i]
            for j in range(len(path)-1):
                v = path[j]
                self.tripod_map[v] = (ti, i, j)
                self.set_colour(v, c)

        p = list()
        for i in range(3):
            # split paths[i] into two paths p[i][0] and p[i][1]
            v = tripod[i][-1]  # tripod leg i attaches to paths[i] at v
            j = self.index_map[v]  # tell us where v is in paths[i].a
            jprime = paths[i].untranslate(j)
            # paths[i][0] is prefix of paths[i] up to and including v
            # paths[i][1] is suffix of paths[i] beginning at v
            p.append((paths[i][:jprime+1], paths[i][jprime:]))
        q = [None]*3
        children = [None]*3
        self.tripod_tree.append(children)
        for i in range(3):
            q[0] = p[i][1]
            q[1] = p[(i+1)%3][0]
            q[2] = list_slice(tripod[(i+1)%3][-2::-1] + tripod[i][:-1])
            for j in range(len(q[2])):
                v = q[2][j]
                self.index_map[v] = j
            m = len(self.tripods)
            self.compute(q)
            if m < len(self.tripods):
                children[i] = m
        # if the tripod is empty and has no children then discard this node
        # not strictly necessary, but saves a lot of clutter
        if not sum([children[i] or len(tripod[i]) > 1 for i in range(3)]):
            self.tripods.pop()
            self.tripod_colours.pop()
            self.tripod_tree.pop()

    def tripod_path(self, v):
        path = list()
        while not self.nma.is_marked(v):
            path.append(v)
            v = self.t[v][0]  # v := parent(v)
        path.append(v)
        return path

    def sperner_triangle(self, e):
        """Find the trichromatic triangle starting from the portal e"""
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
        """Find the trichromatic triangle searching from 3 portals"""
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
