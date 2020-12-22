#!/usr/bin/python3
import sys
import random
import subprocess
import matplotlib.pyplot as plt
import time

import lhp

######################################################################
# Boring routines to build a "random" triangulation
######################################################################
def make_triangulation(n):
    # print("Calling rbox")
    # rbox = subprocess.run(["rbox", "D2", "y", str(n-3)], capture_output=True)
    # points = [s.split() for s in rbox.stdout.splitlines()]
    # points = [(float(s[0]),float(s[1])) for s in points[2:]]

    print("Generating random points")
    # random.seed(0)
    points = [(-1.5,-1.5), (-1.5,3), (3,-1.5)] \
             + [random_point() for _ in range(n-3)]

    points = [(-1.5,-1.5), (-1.5,3), (3,-1.5)] \
             + [(-1 + i/(n-3), -1 + i/(n-3)) for i in range(n-3)]

    # points = [(-1,-1), (0,1), (1,-1)] + [(1/2 + i/n, 0) for i in range(n-3)]


    input = "2\n{}\n".format(n)
    input += "\n".join(["{} {}".format(p[0], p[1]) for p in points])
    input = input.encode('utf8')

    print("Calling qhull")
    qhull = subprocess.run(["qhull", "d", "i"], input=input,
                           capture_output=True)
    lines = qhull.stdout.splitlines()
    f = 1 + int(lines[0])
    faces = [(0,1,2)]  # see note below about orientation of outer face
    for line in lines[1:]:
        t = tuple([int(s) for s in line.split()])
        faces.append(t)

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

    # print("Building adjacency lists")
    # # print(succ)
    # for u in range(n):
    #     v = list(succ[u])[0]  # better way to do this?
    #     al[u].append(v)
    #     next = succ[u][v]
    #     while next != v:
    #         al[u].append(next)
    #         next = succ[u][next]
    return succ, points


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

""" Convert a triangle-based adjacency representation into an adjacency-list representation """
def succ2al(succ):
    al = list()
    for sd in succ:
        al.append(list())
        v0 = next(iter(sd))
        v = v0
        while True: # emulating do ... while v != v0
            al[-1].append(v)
            v = sd[v]
            if v == v0: break
    return al

""" Convert a standard adjacency list embedding of a triangulation into the triangle-based adjacency representation we need """
def al2succ(al):
    succ = list()
    for neighbours in al:
        succ.append(dict())
        for i in range(len(neighbours)):
            succ[-1][neighbours[i]] = neighbours[(i+1)%len(neighbours)]
    return succ

if __name__ == "__main__":
    if len(sys.argv) == 2:
        n = int(sys.argv[1])
    else:
        n = 10

    print("n = {}".format(n))

    succ, points = make_triangulation(n)

    print("Computing tripod decomposition using O(n log n) algorithm")
    start = time.time_ns()
    tp = lhp.tripod_partition(succ, True)
    stop = time.time_ns()
    print("done")
    print("Elapsed time: {}s".format((stop-start)*1e-9))

    print("Computing tripod decomposition using O(n^2) algorithms")
    start = time.time_ns()
    tp = lhp.tripod_partition(succ, False)
    stop = time.time_ns()
    print("done")
    print("Elapsed time: {}s".format((stop-start)*1e-9))

    if n > 500:
        print("Not displaying results since n = {} > 500".format(n))
        sys.exit(0)

    for i in range(len(tp.tripod_tree)):
        # print("tripod {}: {}".format(i, tp.tripods[i]))
        print("children({})={}".format(i, tp.tripod_tree[i]))

    # draw graph
    for v in range(len(succ)):
        for w in succ[v]:
            plt.plot([points[v][0], points[w][0]], [points[v][1], points[w][1]], color='gray', lw=0.2)

    # draw spanning tree
    # for v in range(len(tp.t)):
    #     for w in tp.t[v][1:]:
    #         plt.plot([points[v][0], points[w][0]], [points[v][1], points[w][1]], color='black', lw=1)

    cmap = ['red', 'green', 'blue', 'darkorange', 'ghostwhite']
    fmap = ['salmon', 'lightgreen', 'lightblue', 'moccasin', 'ghostwhite']

    for i in range(len(tp.tripods)):
        tripod = tp.tripods[i]
        c = tp.tripod_colours[i]
        # Draw tripods
        for path in tripod:
            x = [points[v][0] for v in path]
            y = [points[v][1] for v in path]
            plt.plot(x, y, color=cmap[c], lw=2)
        tau = [tripod[i][0] for i in range(3)]
        if i != 0:
            # draw and label sperner triangle
            x = [points[v][0] for v in tau]
            y = [points[v][1] for v in tau]
            if n <= 100:
                plt.fill(x, y, facecolor=fmap[c], lw=0)
            x = sum(x)/3
            y = sum(y)/3
            plt.text(x, y, str(i), horizontalalignment='center',
                     verticalalignment='center', fontsize=min(10,500/n))

            tau2 = sum([tripod[j][:-1][:1] for j in range(3)], [])
            if tau2:
                tau2.append(tau2[0])
                x = [points[v][0] for v in tau2]
                y = [points[v][1] for v in tau2]
                plt.plot(x, y, color=cmap[c], lw=2)

    for v in range(n):
        c = cmap[tp.get_colour(v)]
        plt.plot(points[v][0], points[v][1], color=c, lw=1, marker='o',
                 markersize=min(8,180/n))

    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
