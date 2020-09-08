#!/usr/bin/python3
import sys
from collections import deque, defaultdict
import random
import subprocess
import matplotlib.pyplot as plt


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
        self.tree = tree
        self.intervals = [None]*n
        self.tour = list()
        for r in roots:
            self._euler_tour(r)

        m = len(self.tour)
        self.intset = IntegerSet(m)
        print(self.intset)
        self.marked = [False]*n
        for r in roots:
            self.mark(r)

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

    # TODO: This shouldn't be recursive
    def _euler_tour(self, r):
        i = len(self.tour)
        a = len(self.tour)
        self.tour.append(r)
        for i in range(1, len(self.tree[r])):
            self._euler_tour(self.tree[r][i])
        b = len(self.tour)
        self.tour.append(r)
        self.intervals[r] = (a,b)

def bfs_tree(al, roots):
    q = deque(roots)
    seen = set(roots)
    t = [list() for _ in al]
    for v in q:
        t[v].append(-1)
    while len(q) > 0:
        v = q.pop()
        for w in al[v]:
            if w not in seen:
                seen.add(w)
                q.appendleft(w)
                t[w].append(v)  # sets w's parent to v
                t[v].append(w)  # makes w a child of v
    return t

class layered_h_partition(object):
    def __init__(self, al, succ):
        self.al = al
        self.succ = succ
        roots = [0,1,2]  # has to be a triangular face
        self.t = bfs_tree(al, roots)

        self.nma = MarkedAncestorStruct(self.t, roots)
        self.colours = [None]*len(self.al)
        for i in range(len(roots)):
            r = roots[i]
            self.set_colour(r, i)

        paths = [[x] for x in roots]
        self.partition = paths

        self.compute(paths)

    def compute(self, paths):
        assert(len(paths) == 3)
        p1, p2, p3 = paths
        e = (p2[-1],p1[0])
        self.tau = self.sperner_triangle(e)
        tau = self.tau
        tripod_paths = [self.tripod_path(tau[i]) for i in range(3)]
        self.partition.extend(tripod_paths)
        print(tripod_paths)
        for path in tripod_paths:
            for v in path:
                self.set_colour(v, 3)

        # Continue here identifying q1, q2, and q3.
        z3 := tripod_paths[0][::-1] + tripod_paths[1]
        x2 = self.t[tripod_paths[1][-1]][0]
        z2 = suffix(p2, x2)
        x1 = self.t[tripod_paths[0][0]][0]
        z1 = prefix(p1, x1)
        self.compute(self, [z1, z2, z3])


    def tripod_path(self, v):
        path = list()
        while self.colours[v] == None:
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

    def set_colour(self, v, c):
        self.nma.mark(v)
        self.colours[v] = c

    def get_colour(self, v):
        a = self.nma.nearest_marked_ancestor(v)
        return self.colours[a]




def build_succ(faces):
    succ = [dict() for _ in range(n)]
    for t in faces:
        for i in range(3):
            (u,v,w) = t[i], t[(i+1)%3], t[(i+2)%3]
            if v in succ[u]:
                print("WARNING: Overwriting successor")
                print(u, succ[u], u, v, w)
                return None
            succ[u][v] = w
    return succ

def random_point():
    while 1 < 2:
        x = 2*random.random()-1
        y = 2*random.random()-1
        if x**2 + y**2 < 1:
            return (x, y)



if __name__ == "__main__":
    if len(sys.argv) == 2:
        n = int(sys.argv[1])
    else:
        n = 10

    print("n = {}".format(n))

    print("Calling rbox")
    rbox = subprocess.run(["rbox", "D2", "y", str(n-3)], capture_output=True)
    points = [s.split() for s in rbox.stdout.splitlines()]
    points = [(float(s[0]),float(s[1])) for s in points[2:]]

    points = [(-1.5,-1.5), (-1.5,3), (3,-1.5)] \
             + [random_point() for _ in range(n-3)]

    input = "2\n{}\n".format(n)
    input += "\n".join(["{} {}".format(p[0], p[1]) for p in points])
    input = input.encode('utf8')

    print(input)
    print("Calling qhull")
    qhull = subprocess.run(["qhull", "d", "i"], input=input,
                           capture_output=True)
    lines = qhull.stdout.splitlines()
    f = 1 + int(lines[0])
    faces = [(0,1,2)]  # see note below about orientation of outer face
    for line in lines[1:]:
        t = tuple([int(s) for s in line.split()])
        faces.append(t)

    print("f = {}".format(f))

    # print(faces)
    # print(len(faces))
    al = [list() for _ in range(n)]

    print("Building successor map")
    succ = build_succ(faces)
    # needed because qhull doesn't consistently orient the outer face
    if not succ:
        print("Trying again")
        faces[0] = (2,1,0)
        succ = build_succ(faces)
    if not succ:
        print("ERROR: Unable to build successors")

    print("Building adjacency lists")
    # print(succ)
    for u in range(n):
        v = list(succ[u])[0]  # better way to do this?
        al[u].append(v)
        next = succ[u][v]
        while next != v:
            al[u].append(next)
            next = succ[u][next]



    print("Initializing layered H-partition")
    lhp = layered_h_partition(al, succ)

    # print("==== adjacency list ====")
    # print(al)

    print("done")

     # draw graph
    for v in range(len(al)):
        for w in al[v]:
            plt.plot([points[v][0], points[w][0]], [points[v][1], points[w][1]], color='gray', lw=0.2)

    # draw spanning tree
    # for v in range(len(t)):
    #     for w in t[v][1:]:
    #         plt.plot([points[v][0], points[w][0]], [points[v][1], points[w][1]], 'r')

    # draw sperner paths
    # for i in range(3):
    #     v = tau[i]
    #     while v > 2:
    #         next = t[v][0]
    #         plt.plot([points[v][0], points[next][0]],
    #                  [points[v][1], points[next][1]], color='purple', lw=2)
    #         v = next

    paths = lhp.partition
    for path in lhp.partition:
        x = [points[v][0] for v in path]
        y = [points[v][1] for v in path]
        plt.plot(x, y, color='purple', lw=2)


    cmap = ['red', 'green', 'blue', 'yellow']
    for v in range(n):
        c = cmap[lhp.get_colour(v)]
        # print(c, v)
        plt.plot(points[v][0], points[v][1], color=c, lw=1, marker='o')

    # draw sperner triangle
    tau = lhp.tau
    x = [(points[tau[i]][0], points[tau[(i+1)%3]][0]) for i in range(3)]
    y = [(points[tau[i]][1], points[tau[(i+1)%3]][1]) for i in range(3)]
    plt.fill(x, y, facecolor='lightsalmon', linewidth=0)
    # plt.plot(x, y, 'g')



    plt.axis('off')
    # plt.xlim(-0.3, 0.3)
    # plt.ylim(-0.3, 0.3)
    plt.gca().set_aspect('equal', adjustable='box')
    # plt.plot([1, 2, 3, 4])
    plt.show()

    # plt.savefig('nice-one.pdf')
