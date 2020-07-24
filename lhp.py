#!/usr/bin/python3
import sys
from collections import deque, defaultdict
import random
import subprocess
import matplotlib.pyplot as plt

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


    # print("==== adjacency list ====")
    # print(al)

    # print("==== bfs tree ====")
    print("Building BFS tree")
    t = bfs_tree([0,1,2], al)
    # print(t)
    # print(faces)

    print("Finding Sperner triangle")
    tau = sperner_triangle([faces[0][2]], [faces[0][1]], [faces[0][0]], al, t)
    print(tau)

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

    # draw all colours
    colours = [None]*n
    colours[0] = 'red'
    colours[1] = 'green'
    colours[2] = 'blue'
    for v in range(n):
        p = [v]
        while not colours[v]:
            v = t[v][0]
            p.append(v)
        c = colours[v]
        for v in p:
            colours[v] = c
        x = [points[v][0] for v in p]
        y = [points[v][1] for v in p]
        m = ['.','None'][n > 200]
        for i in range(len(p)-1):
            plt.plot(x, y, color=c, lw=1, marker=m)

    # # draw sperner triangle
    # x = [(points[tau[i]][0], points[tau[(i+1)%3]][0]) for i in range(3)]
    # y = [(points[tau[i]][1], points[tau[(i+1)%3]][1]) for i in range(3)]
    # plt.fill(x, y, facecolor='lightsalmon', edgecolor='orangered', linewidth=0.5)
    # plt.plot(x, y, 'g')

    plt.axis('off')
    # plt.xlim(-0.3, 0.3)
    # plt.ylim(-0.3, 0.3)
    plt.gca().set_aspect('equal', adjustable='box')
    # plt.plot([1, 2, 3, 4])
    # plt.show()

    plt.savefig('nice-one.pdf')
