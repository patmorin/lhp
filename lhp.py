import sys
from collections import deque, defaultdict
import random
import subprocess

def bfs_tree(roots, al):
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

def colour_path(v, colours, t):
    path = [v]
    while path[-1] not in colours:
        path.append(t[path[-1]][0])
    c = colours[path[-1]]
    for u in path:
        colours[u] = c

def sperner_triangle(p1, p2, p3, al, t):
    p = (p1, p2, p3)
    colours = dict()
    for i in range(len(p)):
        for v in p[i]:
            colours[v] = i

    e = (p1[-1],p2[0])
    while 1 < 2:
        v = succ[e[0]][e[1]]
        colour_path(v, colours, t)
        if colours[v] != colours[e[0]] and colours[v] != colours[e[1]]:
            return e[0], e[1], v
        if colours[v] != colours[e[0]]:
            e = e[0], v
        elif colours[v] != colours[e[1]]:
            e = v, e[1]



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
    # print(points)

    print("Calling qhull")
    qhull = subprocess.run(["qhull", "d", "i"], input=rbox.stdout, capture_output=True)
    # print(qhull.stdout)
    lines = qhull.stdout.splitlines()
    f = 1 + int(lines[0])
    faces = [(0,1,2)]
    for line in lines[1:]:
        t = tuple([int(s) for s in line.split()])
        faces.append(t)

    print("f = {}".format(f))

    # print(faces)
    # print(len(faces))
    al = [list() for _ in range(n)]

    print("Building successor map")
    succ = [dict() for _ in range(n)]
    for t in faces:
        for i in range(3):
            (u,v,w) = t[i], t[(i+1)%3], t[(i+2)%3]
            if v in succ[u]:
                print("Overwriting successor")
                print(u, succ[u], u, v, w)
            succ[u][v] = w

    print("Building adjacency lists")
    # print(succ)
    for u in range(n):
        v = random.choice(list(succ[u]))
        al[u].append(v)
        next = succ[u][v]
        while next != v:
            al[u].append(next)
            try:
                next = succ[u][next]
            except KeyError:
                print(succ[u])
                sys.exit(-1)


    # print("==== adjacency list ====")
    # print(al)

    # print("==== bfs tree ====")
    print("Building BFS tree")
    t = bfs_tree([0,1,2], al)
    # print(t)
    # print(faces)

    print("Finding Sperner triangle")
    tau = sperner_triangle([2], [1], [0], al, t)
    print(tau)

    print("done")
