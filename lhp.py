#!/usr/bin/python3
"""Layered H-partitions

An implementation of layered H-partitions for planar graphs, i.e., the Product Structure Theorem for planar graphs.  The algorithm implemented here closely follows the algorithm described in this paper: https://arxiv.org/abs/2004.02530
"""
import sys
import collections
import itertools
import random

"""A light wrapper around list that allows for constant-time slices."""
class list_slice(object):
    def __init__(self, a, start = None, stop=None):
        if start == None:
            start = 0
        if stop == None:
            stop = len(a)
        assert(start <= stop)
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
            assert(start >= 0 and start < len(self))
            assert(stop >= start and stop <= len(self))
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
    def __init__(self, succ, outer_face, worst_case=True, verify=True):
        n = len(succ)
        td = sum([len(a) for a in succ])
        m = td // 2
        f = td // 3
        assert(m == 3*n -6)
        assert(f == 2*n - 4)  # redundant, of course

        self.succ = succ

        roots = outer_face[::-1]
        self.t = bfs_forest(succ, roots)
        self.nma = MarkedAncestorStruct(self.t, roots)

        self.tripod_map = [None] * len(succ)
        self.index_map = [None] * len(succ)  # allows constant time path splits
        self.colours = [4] * len(succ)
        for i in range(len(roots)):
            r = roots[i]
            self.tripod_map[r] = (0, i, 0)
            self.index_map[r] = 0
            self.set_colour(r, i)

        paths = [list_slice([x]) for x in roots]
        self.tripods = [[[x, -1] for x in roots]]
        self.tripod_colours = [0]
        self.tripod_tree = [[1]]

        self._compute(paths, worst_case)

        # These are used only during the computation
        del self.index_map
        del self.nma
        del self.tripod_colours

        # These checks add about 10% to the runtime
        if verify:
            self.verify_results()

    """ Compute the partition into tripods """
    def _compute(self, paths, worst_case):
        # To avoid recursion we implement our own recursion stack.
        # Each stack frame is a list of up to 3 subproblems. Each subproblem
        # contains the index of the parent tripod, the index of the subproblem
        # within this tripod, and the three paths that form a cycle containing
        # the subproblem
        stack = [[(0, 0, paths)]]
        nextsubproblem = stack[0][0]
        while nextsubproblem:
            (parent, r, paths) = nextsubproblem

            # paths[2] is two entire legs of a tripod
            for i in range(len(paths[2])):
                self.index_map[paths[2][i]] = i

            # paths[0] and paths[1] are always non-empty, but not paths[2]
            if not paths[2]:
                # TODO: Handle this case directly, without recolouring
                cprime = free_colour([self.colours[paths[0][0]],
                                  self.colours[paths[1][0]]])
                if len(paths[1]) > 1:
                    paths = [paths[0], paths[1][:-1], paths[1][-1:]]
                else: # len(paths[0]) > 1:
                    paths = [paths[0][1:], paths[1], paths[0][:1]]
                v = paths[2][0]
                self.colours[v] = cprime
                stack[-1][-1] = (parent, r, paths)

            if worst_case:
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

            # add this tripod to the list of tripods
            ti = len(self.tripods)
            self.tripods.append(tripod)
            self.tripod_tree.append([None]*3)
            self.tripod_tree[parent][r] = ti

            # colour the tripod with a colour not used by paths[0,1,2]
            c2 = free_colour([self.get_colour(tau[i]) for i in range(3)])
            self.tripod_colours.append(c2)

            # map and colour the vertices in the tripod
            for i in range(3):
                path = tripod[i]
                for j in range(len(path)-1):
                    v = path[j]
                    self.tripod_map[v] = (ti, i, j)
                    self.set_colour(v, c2)

            # Create the 6 paths that appear on the boundaries of subproblems.
            p = list()
            for i in range(3):
                v = tripod[i][-1]  # tripod leg i attaches to paths[i] at v
                j = self.index_map[v]  # tells us where v is in paths[i].a
                jprime = paths[i].untranslate(j)
                assert(paths[i][jprime] == v)
                # p[i][0] is the prefix of paths[i] up to and including v
                # p[i][1] is the suffix of paths[i] beginning at v
                p.append((paths[i][:jprime+1], paths[i][jprime:]))

            # Create the up to three subproblems generated by this tripod.
            newframe = list()
            for i0 in range(3):
                i = [1, 2, 0][i0]
                q = [None]*3
                q[0] = p[i][1]
                q[1] = p[(i+1)%3][0]
                q[2] = list_slice(tripod[(i+1)%3][-2::-1] + tripod[i][:-1])
                if sum([len(q[i]) for i in range(3)]) >= 3:
                    newframe.append((ti, i0, q))

            if newframe:
                # The next iteration is a "recursive" call
                newframe = newframe[::-1] # solve subproblems in preorder
                stack.append(newframe)
                nextsubproblem = newframe[-1]
            else:
                # We are now returning from one or more "recursive" calls
                nextsubproblem = None
                while stack and not nextsubproblem:
                    frame = stack[-1]
                    parent, r, paths = frame.pop()
                    if len(paths[2]) == 1:
                        v = paths[2][0]
                        self.colours[v] = self.tripod_colours[self.tripod_map[v][0]]
                    if not frame:
                        stack.pop()
                    else:
                        nextsubproblem = frame[-1]
                # TODO: this creates exactly one tripod for each face of
                # the input graph. Many of these tripods are useless: they
                # have no legs and no children. With a bit more work we
                # could avoid creating these tripods and speedup the code

    """ Return the parents of tripod t

        Return the parents of t in the treewidth <= 3 graph formed by
        contracting the tripods.
    """
    def h3parents(self, t):
        if t == 0:
            return []
        return [self.tripod_map[leg[-1]][0] for leg in self.tripods[t]]


    """ Return the parents of leg i of tripod t

        Return the parents of leg i of tripod t in the treewidth <= 8 graph
        formed by contracting each leg of each tripod.
    """
    def h8parents(self, t, i):
        # (t, i) has i parents in tripod t
        parents = [(t, j) for j in range(i)]
        # tripod 1 is adjacent to all three legs of the root
        if t == 1:
            parents.extend([(0, j) for j in range(3)])
            return parents
        # for t > 1, (t, i) is adjacent to two legs of each h3-parent of t
        for p in set(self.h3parents(t)):
            # Tricky: leg j of tripod 1 always attaches to leg j of tripod 0,
            # so if (t, i) is not adjacent to (1, j), then it's not adjacent
            # to (0, j)
            pp = max(p, 1)
            # This uses the fact that a the tripods are numbered by
            # the order they're encountered in a pre-order traversal of
            # self.tripod_tree.
            indexer = self.tripod_tree[pp] + [len(self.tripods)]
            for j in range(len(indexer)-1, -1, -1):
                if indexer[j]:
                    m = indexer[j]
                else:
                    indexer[j] = m
            j = 0
            while indexer[j] > t or indexer[j+1] <= t:
                j += 1
            parents.extend([(p, k) for k in range(3) if k != j])
        return parents

    """ Return a proper 4-colouring of the tripods """
    def colour_tripods(self):
        tripod_colours = [0]
        for t in range(1, len(self.tripods)):
            h3parents = self.h3parents(t)
            c = free_colour([tripod_colours[p] for p in h3parents])
            tripod_colours.append(c)
        return tripod_colours

    def verify_results(self):
        # First make sure the tripods form a partition
        vertices = set()
        for tripod in self.tripods:
            for path in tripod:
                for i in range(len(path)-1):
                    v = path[i]
                    assert(v not in vertices)
                    vertices.add(v)

        # Check the graph obtained by contracting tripods
        for t in range(len(self.tripods)):
            h3parents = self.h3parents(t)
            assert(len(h3parents) <= 3)
            assert(len(h3parents) == 0 or max(h3parents) < t)

        # Check the graph obtained by contracting legs
        h8p = list()
        for (t, i) in itertools.product(range(len(self.tripods)), range(3)):
            h8parents = self.h8parents(t, i)
            assert(len(h8parents) <= 8)
            assert(len(h8parents) == 0 or max(h8parents) < (t,i))
            h8p.append(h8parents)

        # Check that h3 and h8 contain the graphs obtained by contracting
        # tripods and legs, respectively
        for u in range(len(self.succ)):
            (tu, iu, ju) = self.tripod_map[u]
            for v in self.succ[u]:
                # if v < u: continue # no need to check every edge twice
                (tv, iv, jv) = self.tripod_map[v]
                if tu < tv:
                    assert(tu in self.h3parents(tv))
                    assert((tu, iu) in h8p[3*tv+iv])
                elif tv < tu:
                    assert(tv in self.h3parents(tu))
                    assert((tv, iv) in h8p[3*tu+iu])
                elif iu < iv:
                    assert((tu, iu) in h8p[3*tv+iv])
                elif iv < iu:
                    assert((tv, iv) in h8p[3*tu+iu])

    """Return the path from v up in self.t until the first marked node """
    def tripod_path(self, v):
        path = list()
        while not self.nma.is_marked(v):
            path.append(v)
            v = self.t[v][0]  # v = parent(v)
        path.append(v)
        return path

    """Find the trichromatic triangle starting from the portal e"""
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

    """Find the trichromatic triangle searching from 3 portals"""
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

    """Set the colour of v to c"""
    def set_colour(self, v, c):
        self.nma.mark(v)
        self.colours[v] = c

    """Get the colour of the first marked ancestor of v"""
    def get_colour(self, v):
        a = self.nma.nearest_marked_ancestor(v)
        return self.colours[a]



"""Standalone program code

This can also be used as a standalone program that reads a triangulation from stdin and outputs a list of tripods to stdout.

The input represents a graph with vertex set 0,..,.n-1.
- Line 0 of the input is f = 2*n - 4
- Each of lines 1,...,f in the input is a triangular face
The vertices of each triangular face must be listed in counterclockwise order

The output represents the closed tripods in a tripod partition.
- Line 0 is the number k of tripods
- Lines 3i-2, 3i-1, 3i are the legs of tripod i (for each i in {1,...,k})
Each leg of the tripod begins with a vertex of the Sperner triangle and ends
at a vertex in one of the three parent tripods.
"""
if __name__ == "__main__":
    f = int(sys.stdin.readline())
    n = (f+5) // 2
    succ = [dict() for _ in range(n)]
    for _ in range(f):
        line = sys.stdin.readline()
        t = [int(x) for x in line.split()]
        for i in range(3):
            succ[t[i]][t[(i+1)%3]] = t[(i+2)%3]

    # This hack makes it possible to use a command line like
    # rbox y <n-3> D2 | qhull d Qt i | python3 lhp.py
    if f == 2*n-5:
        f += 1
        sys.stderr.write("Warning: One face too few, assuming outerface [0,1,2]\n")
        t = [0, 1, 2]
        if 1 in succ[0]:
            t = t[::-1]
        for i in range(3):
            succ[t[i]][t[(i+1)%3]] = t[(i+2)%3]

    outer_face = [0, next(iter(succ[0])), None]
    outer_face[2] = succ[outer_face[0]][outer_face[1]]
    tp = tripod_partition(succ, outer_face, True)
    print(len(tp.tripods))
    for t in tp.tripods:
        for leg in t:
            print(" ".join([str(v) for v in leg]))
