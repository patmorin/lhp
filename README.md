# An Implementation of the Product Structure Theorem for Planar Graphs

An implementation of layered H-partitions, a.k.a, the Product Structure Theorem for planar graphs.  This implements the algorithm described in [arXiv:2004.02530](https://arxiv.org/abs/2004.02530).

# lhp.py

`lhp.py` is a module that includes the `tripod_partition` class and is also a standalone command-line program.

## The `tripod_partition` class

The useful thing for programmers is the `tripod_partition` class, whose constructor requires an embedding of a planar triangulation *G* with vertex set \{0,..,*n*-1\} and a list of three vertices `outer_face` that lists the vertices of some face in counterlockwise order.

The triangulation *G* must be described as a list `succ` of length *n*. The list entry `succ[i]` is a dictionary that maps each neighbour *j* of *i* onto the neighbour *k* of *i* that appears immediately after *j* when ordering the neighbours of *i* in counterclockwise order around *i*.  Specifically, `(i,j,k)` is a triangular face of *G*.  For any directed edge `ij`, `succ[i][j]` is the third vertex of the face to the left of `ij`.

If you have a standard adjacency list representation of *G* you can use the following function to convert it to the formatted needed by the `tripod_partition` constructor:

    def al2succ(al):
        succ = list()
        for neighbours in al:
            succ.append(dict())
            for i in range(len(neighbours)):
                succ[-1][neighbours[i]] = neighbours[(i+1)%len(neighbours)]
        return succ


After constructing it, the tripod partition has several parts:

- `t`: This is a BFS tree rooted at `roots`, stored in an adjacency list representation.  This tree is represented as a list of length *n*. For each `i` in \{0,...,`n`-1\}, `t[i]` is the list of nodes adjacent to `i` beginning with the parent node, so `t[i][0]` is the parent of `i` in the BFS tree.  The parent of each outer face node is `-1`, so `t[j][0] = -1` for each j in `outer_face`.
- `tripods`: This is a list of *closed tripods*.  Each tripod `tripods[t]` is a list of 3 vertical paths in the BFS tree T called the *legs* of `t`.  Each leg `tripods[t][i]` of each tripod contains a *foot* `tripods[t][i][-1]`.  For each `t>0` each each `i` in \{1,2,3\}, the foot `tripods[t][i][-1]` appears&mdash;not as a foot&mdash;in exactly one other tripod, so  `tripods[t][i][-1]` is contained in `tripods[p][j][:-1]` for some `(p,j)`.  When this happens, `p` is called the *parent tripod* of `t`.  The only exception is the *root tripod* `tripods[0]`, for which `tripods[0][i][-1]=-1` for each `i` in \{0,1,2\}.  The *open* tripod `t` consists of the tripod `t` minus its three feet. The open tripods form a partition of the vertices of *G*, as do the legs of the open tripods; each vertex of *G* appears in exactly one leg of one open tripod.
- `tripod_map`: This is a list of length *n* that maps each *v* vertex of *G* onto a triple `(ti,l,j)` where `ti` is the tripod that contains *v*, `l` is the leg that contains *v* and `j` is the location of *v* in this leg.  So, if `(ti,l,j) = tripod_map[v]` then `tripods[ti][l][j]=v`.
- `tripod_tree`: This is a list of length `len(tripods)` that encodes a 3-ary tree whose nodes are tripods.  This tree has the property that `tripods[i][j][:-1]` (a vertical path in `t`) has no vertex adjacent to any open tripod in the subtree `tripod_tree[i][j]`.  (Leg *j* of the tripod is separated from all tripods contained in subtree *j*.)  A useful property of these tripods is that they are ordered by a preorder traversal of the tripod tree.  If tripod `a` is an ancestor of tripod `t`, then this makes it possible to know, in constant-time, which of the three subtrees of `a` contains `t`.

## Tree decompositions of quotient graphs

A `tripod_partition` induces two quotient graphs: The graph h3 is the graph obtained by contracting each open tripod. The graph h8 is the graph obtained by contracting each leg of each open tripod. The data members `tripod_tree`, `tripods`, and `tripod_map` can be used to obtain a width-3 tree-decomposition of h3 and a width-8 tree decomposition of h8. The `tripod_partition` class includes members functions for doing this:

- `h3parents(t)`: returns a list of (at most 3) tripods that are the parents of t in a width-3 tree decomposition of h3.
- `h8parents(t, i)`: returns a lsit of (at most 8) tripods that are the parents of leg i of tripod t in a width-8 tree decomposition of h8.

The numbering of tripods is such that `p<t` for each `p` in `h3parents(t)` and `(p,j)<(t,i)` for each `(p,j)` in `h3parents(t,i)`.  (Remember that Python does lexicographic comparison of tuples.) 

Each of these functions runs in constant time, but if you intend to do a lot of work with these decompositions, it is worthwhile saving them using something like:

    h3p = [ h3parents(t) for t in range(len(tp.tripods) ]
    h8p = [ h8parents(t,i) for (t,i) in itertools.product(range(len(tp.tripods),range(3)) ]

(In the second case, `h8parents(t,i)==h8p[3*t+i]`.)

## Standalone program

The lhp.py module can also be used as a standalone program that reads a triangulation from stdin and outputs a list of tripods to stdout.

The input represents a graph with vertex set 0,..,.n-1.
- Line 0 of the input is f = 2*n - 4
- Each of lines 1,...,f in the input is a triangular face
The vertices of each triangular face must be listed in counterclockwise order

The output represents the closed tripods in a tripod partition.
- Line 0 is the number k of tripods
- Lines 3i-2, 3i-1, 3i are the legs of tripod i (for each i in {1,...,k})
Each leg of the tripod begins with a vertex of the Sperner triangle and ends at a vertex in one of the three parent tripods.

If f is of the form 2*n - 5, instead of 2*n - 4, then the program assumes that there is an additional face [0,1,2] or [2,1,0] that is missing and adds it. This makes it compatible with `qhull`. In particular, the following command line works:

    rbox y 100 D2 | qhull d Qt i | python3 lhp.py

# lhp_demo.py

Unfortunately, this demo requires `scipy.spatial` (which uses `qhull`) for generating random Delaunay triangulations

    ./lhp_demo.py -h
    Computes a tripod decomposition of a Delaunay triangulation
    Usage: ./lhp_demo.py [-h] [-c] [-r] [-y] [-w] [-b] [-nv] <n>
      -h show this message
      -c use collinear points
      -y use random points in triangle
      -r use random points in disk (default)
      -w use O(n log n) time algorithm (default)
      -b use O(n^2) time algorithm (usually faster)
      -nv don't verify correctness of results
      <n> the number of points to use (default = 10)

If *n* &lt; 500 then this program will show the result in a matplotlib window, producing pictures that look like this:

![tripod decomposition](figs/figure.png "Tripod decomposition")
![tripod decomposition](figs/figure2.png "Tripod decomposition")
![tripod decomposition](figs/figure3.png "Tripod decomposition")

Run `lhp_demo.py -h` for a list of options

# References

For more information on the Product Structure Theorem and the algorithm described here, see the following references:

- [arxiv:1904.04791](https://arxiv.org/abs/1904.04791) introduces the tripod decomposition and uses it to solve an old problem on planar graphs.
- [arxiv:1807.03683](https://arxiv.org/abs/1807.03683) introduces a slightly different tripod decomposition, on which the one described in the previous reference  is based.
- [arxiv:2004.02530](https://arxiv.org/abs/2004.02530) describes the algorithm used in this implementation

The product structure theorem has been used to solve a number of problems on planar graphs, including [queue number](https://arxiv.org/abs/1904.04791), [nonrepetitive colouring](https://arxiv.org/abs/1904.05269), [adjacency labelling](https://arxiv.org/abs/2003.04280), [universal graphs](https://arxiv.org/abs/2010.05779), [vertex ranking](https://arxiv.org/abs/2007.06455) and [p-centered colouring](https://arxiv.org/abs/1907.04586).  You can probably find more on [Google Scholar](https://scholar.google.com/scholar?cites=16964377059594834981).

There are product structure theorems for generalizations of planar graphs, including [bounded-genus and apex-minor-free graphs](https://arxiv.org/abs/1904.04791) and [k-planar graphs](https://arxiv.org/abs/1907.05168).  Most of these ultimately rely on a subroutine computing the product structure of planar graphs like the one given in this implementation.


