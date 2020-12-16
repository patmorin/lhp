An implementation of layered H-partitions, a.k.a, the Product Structure Theorem for planar graphs.  This implements the algorithm described in [arXiv:2004.02530](https://arxiv.org/abs/2004.02530).

The useful thing here is the *tripod_decomposition* class, whose constructor requires two descriptions of the same planar triangulation G with vertex set \{0,..,n-1\} and with outer face (2,1,0). The first description is as an an adjacency list, *al*.  The second is as a dictionary, *succ*, that maps each directed edge uv (an ordered pair of integers) onto the third vertex w of the triangle uvw that is to the left of uv.  Equivalently, succ[(u,v)] is the vertex w that appears immediately after v when the vertices adjacent to u are ordered in counterclockwise order.

The algorithm constructs a BFS tree T rooted at [0,1,2].  After constructing it, the tripod decomposition contains a list of *tripods*. Each tripod is a list of 3 vertical paths in the BFS tree T.

As a side-effect, this algorithm computes a 4-colouring of G such that

- all vertices of each tripod have the same colour (so this is really a colouring of the tripods)
- if two tripods have the same colour then there is no edge between them.

The program lhp_demo.py produces pictures that look like this:

![tripod decomposition](figure.png "Tripod decomposition")
