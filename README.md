An implementation of layered H-partitions, a.k.a, the Product Structure Theorem for planar graphs.  This implements the algorithm described in [arXiv:2004.02530](https://arxiv.org/abs/2004.02530).

The useful thing here is the *tripod_decomposition* class, whose constructor requires two descriptions of the same planar triangulation G with vertex set 0,..,n and with outer face (2,1,0). The first description is as an an adjacency list *al*.  The second is as a dictionary that maps each directed edge uv (an ordered pair of integers) onto the third vertex w of the triangle uvw that is to the left of uv.

The algorithm constructs a BFS tree rooted at [0,1,2].  After constructing it, the tripod decomposition contains a list of *tripods*. Each element of *tripods* is a 3-element list and each element of this list is a vertical path in the BFS tree.
