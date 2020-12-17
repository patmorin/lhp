# An Implementation of the Product Structure Theorem for Planar Graphs

An implementation of layered H-partitions, a.k.a, the Product Structure Theorem for planar graphs.  This implements the algorithm described in [arXiv:2004.02530](https://arxiv.org/abs/2004.02530).

The useful thing here is the `tripod_decomposition` class, whose constructor requires an embedding of a planar triangulation G with vertex set \{0,..,*n*-1\} and with outer face (2,1,0).

The graph *G* must be described as a list `succ` of length *n*. The list entry `succ[i]` is a dictionary that maps each neighbour *j* of *i* onto the neighbour *k* of *i* that appears immediately after *j* when ordering the neighbours of *i* in counterclockwise order around *i*.  Specifically, *(i,j,k)* is a triangular face of *G*.  For any directed edge *ij*, `succ[i][j]` is the third vertex of the face to the left of *ij*.

If you have an embedding of G represented as a standard adjacency list you can use the function *al2succ(al)* in lhp_demo.py to convert to the format we need.

After constructing it, the tripod decomposition has several parts:

- `t`: This is a BFS tree rooted at [0, 1, 2].
- `tripods`: This is a list of *tripods*.  Each tripod is a list of 3 vertical paths in the BFS tree T.  The set \{tripods[i][j][:-1] : 0<= i < len(tripods), 0<= j<3 \}  is a partition of the vertices of G.  **Note:** Pay attention to the `[:-1]`; each of these three lists contains one extra vertex that is technically not in the tripod.
- tripod_map: This is a list of length *n* that maps each vertex of *G* onto the tripod that contains it.  So if `k = tripod_map(v)` then `v` is in one of the three paths \{`tripods[i][:-1]` : 0<= i < len(tripods)\}
- tripod_colours: This is a list of length `len(tripods)` that assigns a colour `tripod_colours[i]` in \{0,1,2,3\} to the tripod `i`.  This is a proper colouring in the sense that, if two tripods receive the same colour then there is no edge between them in *G*.
- tripod_tree: This is a list of length `len(tripods)` that encodes a 3-ary tree whose nodes are tripods.  This tree has the property that tripod[i][j] has no vertex adjacent to any tripod in the subtree `tripod_tree[i][j]`.  (Leg *j* of the tripod is separated from all tripods contains in subtree *j*.)

From

The program lhp_demo.py produces pictures that look like this:

![tripod decomposition](figure.png "Tripod decomposition")
