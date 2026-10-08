---
id: dsa-coding
title: Data Structures and Algorithms for Data Roles
tier: 4
priority: should-know
sources: [obenner/data-structure.md, obenner/sql.md, cookbook]
---

# Data Structures and Algorithms for Data Roles

## Say it in one line
For data-engineering and analyst screens, DSA means hash maps, arrays, strings and complexity vocabulary — not competitive-programming graph theory.

## Must be able to recite
- **Time and space complexity** — Big-O is the growth rate of work and memory as input grows; quote it for every solution you give, because not saying it is the usual mark-down.
- **Array vs linked list** — an array is contiguous with O(1) indexing and expensive inserts, a linked list is scattered with O(1) inserts at a known node but O(n) lookup and no indexing.
- **Hash map** — key-to-slot function giving O(1) average lookup and insert, O(n) worst case; it is the answer to almost every "count", "dedupe" or "have I seen this" question.
- **Collision resolution** — separate chaining keeps a list per bucket, open addressing probes for another free slot; probing degrades badly past about half full, hence rehashing.
- **Set** — an unordered collection with no duplicates and O(1) membership, the right structure for dedupe and for "which keys are in A but not B".
- **Stack** — LIFO with push/pop, used for recursion frames, undo, balanced parentheses and postfix evaluation.
- **Queue and deque** — a queue is FIFO with insert at the rear and delete at the front; a deque allows both ends, and a circular queue reuses the array by wrapping.
- **Heap / priority queue** — a complete binary tree obeying the heap-order property, giving O(log n) insert and O(1) peek at the min or max; it is how you take top-k without sorting everything.
- **Binary search** — halves a sorted, randomly indexable collection in O(log n); it cannot be applied to a linked list because there is no way to reach the middle element.
- **Two pointers** — walk a sorted array from both ends or with a lead-lag pair to replace a nested loop, turning O(n²) into O(n).
- **Sliding window** — maintain a running aggregate over a moving contiguous range so each element is added and removed once, O(n) instead of recomputing per window.
- **Sorting** — comparison sorts cannot beat O(n log n); "stable" means equal keys keep their input order, which matters when you sort by one column then another.
- **Tree traversals** — preorder is root-left-right, inorder is left-root-right, postorder is left-right-root, level order is breadth-first; inorder on a BST returns sorted order.
- **BFS vs DFS** — BFS explores level by level using a queue and finds the fewest-edge path, DFS goes deep using a stack or recursion and backtracks; both visit each vertex and edge once.
- **Recursion** — a function defined in terms of a simpler case of itself, running on the call stack; every recursion has an iterative equivalent, which needs an explicit stack.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a data structure and why do you need one? — A way of organising data that captures both the items and the relationships between them, so you can pick algorithms that exploit that structure.
- ★ What is the difference between an abstract data type, a data type and a data structure? — The ADT is the specification (values plus operations), the data type is a concrete implementation of it, and a data structure is the arrangement of variables in memory that realises it.
- ★ Array vs linked list — advantages of each? — Arrays give O(1) indexed access but fixed size and costly insertion or deletion; linked lists grow dynamically and insert cheaply, but cost a pointer per node and O(n) search.
- ★ Stack vs array? — A stack is a dynamic LIFO discipline where only the top is reachable; an array is a fixed-size indexed container where any position is reachable, and an array can be the storage for a stack.
- Why can you not binary search a sorted linked list? — There is no way to index the middle element, so each "jump" costs a traversal and the O(log n) advantage disappears.
- ★ Define a stack and a queue, and give applications. — Stack is LIFO (recursion, string reversal, balanced parentheses, expression evaluation), queue is FIFO (print jobs, call queues, shared-resource access).
- ★ What is a priority queue and how does it differ from a queue? — Removal order is by priority rather than arrival, and it is normally implemented as a binary heap; the classic motivation is a scheduler that must let short or important jobs jump the line.
- What is the minimum number of queues needed to implement a priority queue? — Two: one holding the data and one holding the priorities.
- Which data structure does recursion use, and why? — The call stack, because LIFO order is exactly what is needed to remember the return address of each caller.
- ★ How do you reverse a linked list? — Walk it once keeping previous, current and next pointers, repointing each node's next to previous; O(n) time, O(1) space.
- How do you check whether a linked list is circular? — Run a slow and a fast pointer; if they meet there is a cycle, if the fast pointer reaches null there is not.
- What are the types of queues? — Linear, circular (rear wraps to the front so the array is reused) and double-ended.
- Define a circular list and a doubly linked list, and their downsides. — A circular list has the last node pointing to the first, a doubly linked list stores previous and next; both make traversal flexible but cost extra pointers and risk infinite loops if the terminating condition is wrong.
- ★ What is hashing, a hash function and a hash table? — Hashing maps a key to a fixed-size value; the hash function converts the key to an index; the hash table is the array of buckets, giving lookup time independent of the number of stored items.
- ★ What is a collision and how do you resolve it? — Two keys hashing to the same slot; resolve with separate chaining (a list per bucket) or open addressing (linear probing, quadratic probing, double hashing).
- What are the limitations of linear and quadratic probing? — Linear probing suffers primary clustering so runs of full slots grow; quadratic probing removes primary clustering but gives no guarantee of finding a free slot once the table is about half full.
- What is rehashing and why is it needed? — Rebuilding the table with a larger size and re-inserting every key when the load factor gets high, because probe lengths blow up as the table fills.
- ★ What are the properties of a binary heap? — The structure property (a complete binary tree, filled left to right) and the heap-order property (every parent is smaller than or equal to its children in a min-heap); insertion percolates up and deletion percolates down.
- ★ What are the binary tree traversals and what does each produce? — Preorder, inorder, postorder and level order; inorder on a binary search tree yields the keys in sorted order.
- Why is search in a binary search tree more efficient than in an ordinary binary tree? — Because the key ordering lets you discard one whole subtree at each comparison, giving O(log n) on a balanced tree instead of O(n).
- What is an AVL tree, what is the balance factor, and when do you rebalance? — A height-balanced BST; the balance factor is the height difference between subtrees, and you rotate when it exceeds one, with four rotation cases (LL, RR, LR, RL).
- ★ Which data structure does a relational database use for its internal storage and indexes? — A B-tree or B+-tree of order m, because it keeps height low and reads a whole page per node, which suits disk and page-based access.
- ★ BFS or DFS — what is the difference and when do you use each? — BFS spreads outward level by level and is the choice for shortest hop count, DFS follows one path to the end and backtracks, and is the choice for reachability, cycle detection and topological order.
- ★ What is a spanning tree and a minimum spanning tree, and does an MST give the shortest path? — A spanning tree connects all vertices without cycles, the minimum one does so at lowest total edge weight via Kruskal or Prim; it does not give the shortest path between two specific nodes.
- Define the graph vocabulary: directed, undirected, weighted, degree, path, cycle, acyclic. — Edges have direction or not, may carry weights, in/out degree counts edges at a vertex, a path is a sequence of adjacent vertices, a cycle is a path back to its start, and an acyclic graph has none.
- When is a directed graph strongly versus weakly connected? — Strongly connected means every vertex reaches every other along directed edges; weakly connected means that only holds if you ignore direction.
- ★ What is a set, a disjoint-set (union-find), and what is it used for? — A set is an unordered duplicate-free collection; disjoint sets partition elements with a representative each, and union-find with union-by-weight and path compression tracks connected components, duplicate pages and MST construction.
- What is infix, prefix and postfix notation, and why do postfix expressions need no parentheses? — Three ways of ordering operators against operands; in postfix or prefix the operator order alone fixes the evaluation order, so precedence and associativity rules are unnecessary.
- What is the difference between persistent and ephemeral data structures? — A persistent structure retains its previous versions after an update, an ephemeral one does not; the source's stack-versus-queue example is a poor one — the real distinction is whether old versions survive.
- Primitive versus non-primitive data types? — Primitives are the language's built-ins (int, float, char, double); non-primitives are user-defined or composite types such as structs, lists and objects.
- What are overflow and underflow? — Overflow is inserting into a structure with no free space, underflow is deleting from an empty one; both must be checked before the operation, not after.
- Is it necessary to sort a file before searching it? — Only if you will search it repeatedly: one lookup is cheaper by linear scan, many lookups pay back the sort or an index.
- What is the complexity of the operations you just used? — State it unprompted: dict and set lookup O(1) average, sort O(n log n), heap push/pop O(log n), scan O(n), and give space alongside time. *(not in sources, but standard)*
- Find pairs summing to a target, or the longest window satisfying a condition. — Hash map for the pair problem in one pass, two pointers if the input is sorted, sliding window for the contiguous-range problem; all O(n). *(not in sources, but standard)*
- Given 100M rows, get the top 10 by value, and the count per key. — A heap of size 10 for top-k in O(n log k), and a dict or `collections.Counter` for the counts — and say out loud that in production this is a SQL `GROUP BY` with `ORDER BY … LIMIT`. *(not in sources, but standard)*

## Traps
- Answering a Python interview with C-era material from question banks — malloc versus calloc, void pointers and dangling pointers are not what a data-engineering panel is testing.
- Saying "hash maps are O(1)" and stopping; add "average, O(n) worst case with adversarial collisions, and the key must be hashable".
- Claiming you can binary search a linked list, or that a minimum spanning tree gives the shortest path between two nodes — both are standard trick questions.
- Coding in silence: state the approach and its complexity, then write it, then name one edge case (empty input, duplicates, nulls).
- Over-investing in LeetCode-hard graph and DP problems for a bank data role, where the screen is usually one array or string question plus heavy SQL — spend the time on [[sql-query-patterns]].
- Forgetting that the interviewer wants the data-engineering reflex: if the input is a table, the answer is a `GROUP BY`, not a hand-rolled loop.

## Graph
- **Needs first:** [[python-for-data]]
- **Leads to:** [[sql-query-patterns]]
- **Asked together with:** —
