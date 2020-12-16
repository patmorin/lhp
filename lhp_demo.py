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
    random.seed(0)
    points = [(-1.5,-1.5), (-1.5,3), (3,-1.5)] \
             + [random_point() for _ in range(n-3)]

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

    print("Building adjacency lists")
    # print(succ)
    for u in range(n):
        v = list(succ[u])[0]  # better way to do this?
        al[u].append(v)
        next = succ[u][v]
        while next != v:
            al[u].append(next)
            next = succ[u][next]
    return succ, al, points


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

    succ, al, points = make_triangulation(n)

    print("Computing tripod decomposition (worst-case)")
    start = time.time_ns()
    tp = lhp.tripod_partition(al, succ, True)
    stop = time.time_ns()
    print("done")
    print("Elapsed time: {}s".format((stop-start)*1e-9))

    print("Computing tripod decomposition (n^2)")
    start = time.time_ns()
    tp = lhp.tripod_partition(al, succ, False)
    stop = time.time_ns()
    print("done")
    print("Elapsed time: {}s".format((stop-start)*1e-9))

    if n > 500:
        print("Not displaying results since n = {} > 500".format(n))
        sys.exit(0)

     # draw graph
    for v in range(len(al)):
        for w in al[v]:
            plt.plot([points[v][0], points[w][0]], [points[v][1], points[w][1]], color='gray', lw=0.2)

    # draw spanning tree
    for v in range(len(tp.t)):
        for w in tp.t[v][1:]:
            plt.plot([points[v][0], points[w][0]], [points[v][1], points[w][1]], color='black', lw=1)

    cmap = ['red', 'green', 'blue', 'darkorange', 'ghostwhite']
    fmap = ['salmon', 'lightgreen', 'lightblue', 'moccasin', 'ghostwhite']

    # Draw sperner triangles
    for k in range(len(tp.sperners)):
        # Draw the Sperner triangle
        # tau.append(tau[0])
        tau = tp.sperners[k]
        c = tp.sperner_colours[k]
        x = [points[tau[i]][0] for i in range(len(tau))]
        y = [points[tau[i]][1] for i in range(len(tau))]
        plt.fill(x, y, facecolor=fmap[c], linewidth=0)

    # Draw tripods
    for tripod in tp.tripods:
        a = tripod[0] + tripod[1] + tripod[2]
        if a and not 0 in a:
            # Draw the legs
            c = tp.colours[a[0]]
            for path in tripod:
                if path:
                    # path = path + [parent(tp.t, path[-1])]
                    x = [points[v][0] for v in path]
                    y = [points[v][1] for v in path]
                    if v not in [0, 1, 2]:
                        x.append(points[tp.t[path[-1]][0]][0])
                        y.append(points[tp.t[path[-1]][0]][1])
                    plt.plot(x, y, color=cmap[c], lw=2)

    for v in range(n):
        c = cmap[tp.colours[v]]
        plt.plot(points[v][0], points[v][1], color=c, lw=1, marker='o')

    plt.axis('off')
    # plt.xlim(-0.3, 0.3)
    # plt.ylim(-0.3, 0.3)
    plt.gca().set_aspect('equal', adjustable='box')
    # plt.plot([1, 2, 3, 4])
    plt.show()

    # plt.savefig('nice-one.pdf')
