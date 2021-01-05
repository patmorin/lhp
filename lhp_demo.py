#!/usr/bin/python3
import sys
import time
import random
import itertools
import matplotlib.pyplot as plt
import scipy.spatial

import lhp

def triangulate(points):
    n = len(points)
    dt = scipy.spatial.Delaunay(points)
    assert(dt.npoints == n)
    assert(len(dt.convex_hull) == 3)
    assert(dt.nsimplex == 2*n - 5)
    succ = [dict() for _ in range(n)]
    for t in dt.simplices:
        for i in range(3):
            succ[t[i]][t[(i+1)%3]] = t[(i+2)%3]

    # don't forget the outer face
    of = list(set(itertools.chain.from_iterable(dt.convex_hull)))
    if of[1] in succ[of[0]]:
        of = of[::-1]
    for i in range(3):
        succ[of[i]][of[(i+1)%3]] = of[(i+2)%3]
    return succ, of



######################################################################
# Boring routines to build a "random" triangulation
######################################################################
def make_triangulation(n, data_type):
    print("Generating points")
    random.seed(0)
    if data_type == 0:
        # Use a set of n-3 random points
        points = [(-1.5,-1.5), (-1.5,3), (3,-1.5)] \
                 + [random_point() for _ in range(n-3)]
    elif data_type == 1:
        # Use a set of n-3 collinear points
        points = [(-1.5,-1.5), (-1.5,3), (3,-1.5)] \
                 + [(-1 + i/(n-3), -1 + i/(n-3)) for i in range(n-3)]
    elif data_type == 2:
        points = [(0, 0), (1,1), (1,0)] \
                 + [(random.random(), random.random()) for _ in range(n-3)]
        for i in range(n):
            (x, y) = points[i]
            if x < y:
                points[i] = (y, x)
    else:
        raise ValueError("Invalid argument for data_type")

    n = len(points)
    # random.shuffle(points)

    print("Computing Delaunay triangulation")
    succ, outer_face = triangulate(points)
    return succ, points, outer_face

""" Generate a random point in the unit circle """
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

def usage():
    print("Computes a tripod decomposition of a Delaunay triangulation")
    print("Usage: {} [-h] [-c] [-r] [-y] [-w] [-b] [-nv] <n>".format(sys.argv[0]))
    print("  -h show this message")
    print("  -c use collinear points")
    print("  -y use random points in triangle")
    print("  -r use random points in disk (default)")
    print("  -w use O(n log n) time algorithm (default)")
    print("  -b use O(n^2) time algorithm (usually faster)")
    print("  -nv don't verify correctness of results")
    print("  <n> the number of points to use (default = 10)")

if __name__ == "__main__":
    n = 0
    data_type = 0
    worst_case = True
    verify = True
    for arg in sys.argv[1:]:
        if arg == '-h':
            usage()
        elif arg == '-r':
            data_type = 0   # random
        elif arg == '-c':
            data_type = 1   # collinear
        elif arg == '-y':
            data_type = 2   # random in triangle (like rbox y)
        elif arg == '-w':
            worst_case = True
        elif arg == '-b':
            worst_case = False
        elif arg == '-nv':
            verify = False
        else:
            n = int(arg)

    if n <= 0:
        usage()
        sys.exit(-1)

    s = ["random", "collinear", "uniform"][data_type]
    print("Generating {} point set of size {}".format(s, n))
    succ, points, outer_face = make_triangulation(n, data_type)
    n = len(succ)
    m = sum([len(x) for x in succ]) // 2
    print("n = ", n, " m = ", m)
    assert(m == 3*n - 6)

    s = ["O(n^2)", "O(n log n)"][worst_case]
    s2 = ["", " and verifying results"][verify]
    print("Using {} algorithm{}...".format(s, s2), end='')
    sys.stdout.flush()
    start = time.time_ns()
    tp = lhp.tripod_partition(succ, outer_face, worst_case, verify)
    stop = time.time_ns()
    print("done")
    print("Elapsed time: {}s".format((stop-start)*1e-9))

    if n > 500:
        print("Not displaying results since n = {} > 500".format(n))
        sys.exit(0)

    # Draw graph
    for v in range(len(succ)):
        for w in succ[v]:
            plt.plot([points[v][0], points[w][0]], [points[v][1], points[w][1]], color='gray', lw=0.2)

    for v in range(n):
        plt.plot(points[v][0], points[v][1], color="red", lw=1, marker='o',
                 markersize=min(8,180/n))


    cmap = ['red', 'darkgreen', 'blue', 'orange', 'ghostwhite']
    fmap = ['mistyrose', 'lightgreen', 'lightblue', 'moccasin', 'ghostwhite']

    # Draw tripods
    tripod_colours = tp.colour_tripods()
    for i in range(1, len(tp.tripods)):
        tripod = tp.tripods[i]
        c = tripod_colours[i]
        # Draw legs
        for path in tripod:
            x = [points[v][0] for v in path]
            y = [points[v][1] for v in path]
            plt.plot(x, y, color=cmap[c], lw=2)
        tau = [tripod[i][0] for i in range(3)]
        # Draw and label Sperner triangle
        x = [points[v][0] for v in tau]
        y = [points[v][1] for v in tau]
        if n <= 100:
            plt.fill(x, y, facecolor=fmap[c], lw=0)
        x = sum(x)/3
        y = sum(y)/3
        if n < 250:
            plt.text(x, y, str(i), horizontalalignment='center',
                     verticalalignment='center', fontsize=min(10,500/n))

        tau2 = sum([tripod[j][:-1][:1] for j in range(3)], [])
        if tau2:
            tau2.append(tau2[0])
            x = [points[v][0] for v in tau2]
            y = [points[v][1] for v in tau2]
            plt.plot(x, y, color=cmap[c], lw=2)

    for v in range(n):
        t = tp.tripod_map[v][0]
        c = cmap[tripod_colours[t]]
        plt.plot(points[v][0], points[v][1], color=c, lw=1, marker='o',
                 markersize=min(8,400/n))

    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
