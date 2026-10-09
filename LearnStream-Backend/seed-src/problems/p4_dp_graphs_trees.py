"""
Problem pack 4: dynamic programming, graphs, trees, heaps, union-find, tries.
33 problems: 11 EASY, 13 MEDIUM, 9 HARD.
All reference solutions are iterative (no deep recursion).
"""
import random
import heapq
import bisect
from collections import deque

MOD = 10 ** 9 + 7


def _R(seed):
    return random.Random(seed)


def _ints(s):
    return list(map(int, s.split()))


# ---------------------------------------------------------------- generators

def _rand_tree_edges(n, rng, chain=False):
    """Edges of a random tree on nodes 1..n (labels shuffled except node 1 kept as a member)."""
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    edges = []
    for i in range(1, n):
        p = i - 1 if chain else rng.randrange(0, i)
        edges.append((perm[p], perm[i]))
    rng.shuffle(edges)
    return [(u, v) if rng.random() < 0.5 else (v, u) for u, v in edges]


def _tree_input(n, edges):
    return "%d\n" % n + "".join("%d %d\n" % e for e in edges)


def _rand_graph(n, m, rng, allow_self=False):
    out = []
    while len(out) < m:
        u, v = rng.randint(1, n), rng.randint(1, n)
        if u == v and not allow_self:
            continue
        out.append((u, v))
    return out


# =============================================================== EASY

# ---- E1 Climbing Stairs
def solve_climb(s):
    n = int(s.split()[0])
    a, b = 1, 1  # ways(0), ways(1)
    for _ in range(n - 1):
        a, b = b, a + b
    return str(b)


# ---- E2 Min Cost Climbing Stairs
def solve_mincost_stairs(s):
    d = _ints(s)
    n, c = d[0], d[1:1 + d[0]]
    a, b = 0, 0  # cost to stand on step i-2, i-1 (before paying)
    for i in range(2, n + 1):
        a, b = b, min(b + c[i - 1], a + c[i - 2])
    return str(b)


def _gen_mincost(seed, n, hi):
    r = _R(seed)
    return "%d\n%s\n" % (n, " ".join(str(r.randint(0, hi)) for _ in range(n)))


# ---- E3 House Robber
def solve_robber(s):
    d = _ints(s)
    n, a = d[0], d[1:1 + d[0]]
    take, skip = 0, 0
    for x in a:
        take, skip = skip + x, max(take, skip)
    return str(max(take, skip))


# ---- E4 Grid Paths With Obstacles
def solve_grid_paths(s):
    lines = s.split()
    r, c = int(lines[0]), int(lines[1])
    g = lines[2:2 + r]
    dp = [0] * c
    for i in range(r):
        row = g[i]
        for j in range(c):
            if row[j] == '#':
                dp[j] = 0
            elif i == 0 and j == 0:
                dp[j] = 1
            elif j > 0:
                dp[j] = (dp[j] + dp[j - 1]) % MOD
    return str(dp[c - 1] % MOD)


def _gen_grid(seed, r, c, p_block, chars=".#", keep_corners=True):
    rng = _R(seed)
    rows = []
    for i in range(r):
        rows.append("".join(chars[1] if rng.random() < p_block else chars[0] for _ in range(c)))
    if keep_corners:
        rows[0] = chars[0] + rows[0][1:]
        rows[-1] = rows[-1][:-1] + chars[0]
    return "%d %d\n%s\n" % (r, c, "\n".join(rows))


# ---- E5 Flood Fill
def solve_flood(s):
    lines = s.split()
    r, c = int(lines[0]), int(lines[1])
    g = [list(x) for x in lines[2:2 + r]]
    sr, sc, ch = int(lines[2 + r]), int(lines[3 + r]), lines[4 + r]
    old = g[sr][sc]
    if old != ch:
        g[sr][sc] = ch
        dq = deque([(sr, sc)])
        while dq:
            x, y = dq.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < r and 0 <= ny < c and g[nx][ny] == old:
                    g[nx][ny] = ch
                    dq.append((nx, ny))
    return "\n".join("".join(row) for row in g)


def _gen_flood(seed, r, c, letters, p_keep):
    rng = _R(seed)
    g = []
    for i in range(r):
        row = []
        for j in range(c):
            if j > 0 and rng.random() < p_keep:
                row.append(row[-1])
            elif i > 0 and rng.random() < p_keep:
                row.append(g[i - 1][j])
            else:
                row.append(rng.choice(letters))
        g.append(row)
    sr, sc = rng.randrange(r), rng.randrange(c)
    return "%d %d\n%s\n%d %d %s\n" % (r, c, "\n".join("".join(x) for x in g), sr, sc, "z")


# ---- E6 Count Connected Components
class _DSU:
    def __init__(self, n):
        self.p = list(range(n + 1))
        self.sz = [1] * (n + 1)

    def find(self, x):
        p = self.p
        root = x
        while p[root] != root:
            root = p[root]
        while p[x] != root:
            p[x], x = root, p[x]
        return root

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.sz[a] < self.sz[b]:
            a, b = b, a
        self.p[b] = a
        self.sz[a] += self.sz[b]
        return True


def solve_components(s):
    d = _ints(s)
    n, m = d[0], d[1]
    dsu = _DSU(n)
    comps = n
    for i in range(m):
        if dsu.union(d[2 + 2 * i], d[3 + 2 * i]):
            comps -= 1
    return str(comps)


def _graph_input(n, edges, extra_first=""):
    return "%d %d%s\n" % (n, len(edges), extra_first) + "".join("%d %d\n" % e for e in edges)


# ---- E7 Tree Height (parent array)
def solve_tree_height(s):
    d = _ints(s)
    n, par = d[0], d[1:1 + d[0]]
    ch = [[] for _ in range(n + 1)]
    root = 0
    for i, p in enumerate(par, 1):
        if p == 0:
            root = i
        else:
            ch[p].append(i)
    depth = [0] * (n + 1)
    best = 0
    st = [root]
    while st:
        u = st.pop()
        for v in ch[u]:
            depth[v] = depth[u] + 1
            if depth[v] > best:
                best = depth[v]
            st.append(v)
    return str(best)


def _gen_parent_array(seed, n, chain=False):
    rng = _R(seed)
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    par = [0] * (n + 1)
    for i in range(1, n):
        p = i - 1 if chain else rng.randrange(max(0, i - 50) if rng.random() < 0.7 else 0, i)
        par[perm[i]] = perm[p]
    return "%d\n%s\n" % (n, " ".join(map(str, par[1:])))


# ---- E8 K Smallest Elements
def solve_k_smallest(s):
    d = _ints(s)
    n, k, a = d[0], d[1], d[2:2 + d[0]]
    return " ".join(map(str, heapq.nsmallest(k, a)))


def _gen_arr(seed, n, lo, hi, prefix_vals=()):
    rng = _R(seed)
    return " ".join(str(rng.randint(lo, hi)) for _ in range(n))


# ---- E9 Count Words With Prefix (trie)
def solve_prefix_count(s):
    t = s.split()
    n = int(t[0])
    words = t[1:1 + n]
    q = int(t[1 + n])
    qs = t[2 + n:2 + n + q]
    # trie with counts
    nxt = [{}]
    cnt = [0]
    for w in words:
        node = 0
        for ch in w:
            nx = nxt[node].get(ch)
            if nx is None:
                nx = len(nxt)
                nxt[node][ch] = nx
                nxt.append({})
                cnt.append(0)
            node = nx
            cnt[node] += 1
    out = []
    for p in qs:
        node = 0
        for ch in p:
            node = nxt[node].get(ch, -1)
            if node == -1:
                break
        out.append(str(cnt[node]) if node != -1 else "0")
    return "\n".join(out)


def _gen_words(seed, n, q, alpha, maxlen):
    rng = _R(seed)
    words = ["".join(rng.choice(alpha) for _ in range(rng.randint(1, maxlen))) for _ in range(n)]
    qs = []
    for _ in range(q):
        if rng.random() < 0.6:
            w = rng.choice(words)
            qs.append(w[:rng.randint(1, len(w))])
        else:
            qs.append("".join(rng.choice(alpha) for _ in range(rng.randint(1, maxlen))))
    return "%d\n%s\n%d\n%s\n" % (n, "\n".join(words), q, "\n".join(qs))


# ---- E10 Shortest Path in an Unweighted Graph
def solve_bfs_path(s):
    d = _ints(s)
    n, m, src, dst = d[0], d[1], d[2], d[3]
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = d[4 + 2 * i], d[5 + 2 * i]
        adj[u].append(v)
        adj[v].append(u)
    dist = [-1] * (n + 1)
    dist[src] = 0
    dq = deque([src])
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                dq.append(v)
    return str(dist[dst])


# ---- E11 Level Order Traversal of a Tree
def _adj_from_edges(n, d, off):
    adj = [[] for _ in range(n + 1)]
    for i in range(n - 1):
        u, v = d[off + 2 * i], d[off + 1 + 2 * i]
        adj[u].append(v)
        adj[v].append(u)
    return adj


def _bfs_order(n, adj, root=1):
    par = [0] * (n + 1)
    depth = [0] * (n + 1)
    order = [root]
    seen = [False] * (n + 1)
    seen[root] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                par[v] = u
                depth[v] = depth[u] + 1
                order.append(v)
    return order, par, depth


def solve_level_order(s):
    d = _ints(s)
    n = d[0]
    adj = _adj_from_edges(n, d, 1)
    order, par, depth = _bfs_order(n, adj)
    levels = {}
    for u in order:
        levels.setdefault(depth[u], []).append(u)
    return "\n".join(" ".join(map(str, sorted(levels[k]))) for k in sorted(levels))


# =============================================================== MEDIUM

# ---- M1 Coin Change: Minimum Coins
def solve_coin_min(s):
    d = _ints(s)
    n, amt, coins = d[0], d[1], d[2:2 + d[0]]
    INF = float("inf")
    dp = [0] + [INF] * amt
    for c in coins:
        for x in range(c, amt + 1):
            if dp[x - c] + 1 < dp[x]:
                dp[x] = dp[x - c] + 1
    return str(dp[amt] if dp[amt] != INF else -1)


def _gen_coins(seed, n, lo, hi, amt):
    rng = _R(seed)
    coins = rng.sample(range(lo, hi + 1), n)
    return "%d %d\n%s\n" % (n, amt, " ".join(map(str, coins)))


# ---- M2 Coin Change: Number of Ways
def solve_coin_ways(s):
    d = _ints(s)
    n, amt, coins = d[0], d[1], d[2:2 + d[0]]
    dp = [1] + [0] * amt
    for c in coins:
        for x in range(c, amt + 1):
            dp[x] = (dp[x] + dp[x - c]) % MOD
    return str(dp[amt])


# ---- M3 Longest Common Subsequence
def solve_lcs(s):
    a, b = s.split()[:2]
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0] * (len(b) + 1)
        for j, cb in enumerate(b, 1):
            if ca == cb:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = cur[j - 1] if cur[j - 1] > prev[j] else prev[j]
        prev = cur
    return str(prev[-1])


def _rstr(rng, n, alpha):
    return "".join(rng.choice(alpha) for _ in range(n))


def _gen_two_strings(seed, n1, n2, alpha):
    rng = _R(seed)
    return "%s\n%s\n" % (_rstr(rng, n1, alpha), _rstr(rng, n2, alpha))


# ---- M4 Edit Distance
def solve_edit(s):
    a, b = s.split()[:2]
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            if ca == cb:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])
        prev = cur
    return str(prev[-1])


# ---- M5 0/1 Knapsack
def solve_knapsack(s):
    d = _ints(s)
    n, W = d[0], d[1]
    dp = [0] * (W + 1)
    for i in range(n):
        w, v = d[2 + 2 * i], d[3 + 2 * i]
        for x in range(W, w - 1, -1):
            if dp[x - w] + v > dp[x]:
                dp[x] = dp[x - w] + v
    return str(dp[W])


def _gen_knap(seed, n, W, wmax, vmax):
    rng = _R(seed)
    items = ["%d %d" % (rng.randint(1, wmax), rng.randint(1, vmax)) for _ in range(n)]
    return "%d %d\n%s\n" % (n, W, "\n".join(items))


# ---- M6 Decode Ways
def solve_decode(s):
    t = s.split()[0]
    a, b = 1, 1  # ways for prefix len i-2, i-1
    for i in range(len(t)):
        cur = 0
        if t[i] != '0':
            cur = b
        if i >= 1 and t[i - 1] != '0' and 10 <= int(t[i - 1:i + 1]) <= 26:
            cur += a
        a, b = b, cur % MOD
    return str(b)


def _gen_decode(seed, n, zero_p):
    rng = _R(seed)
    out = []
    for i in range(n):
        if rng.random() < zero_p and out and out[-1] in "12":
            out.append("0")
        else:
            out.append(rng.choice("1112223456789"))
    if out[0] == "0":
        out[0] = "1"
    return "".join(out) + "\n"


# ---- M7 Rotting Oranges
def solve_rotting(s):
    t = s.split()
    r, c = int(t[0]), int(t[1])
    g = [list(x) for x in t[2:2 + r]]
    dq = deque()
    fresh = 0
    for i in range(r):
        for j in range(c):
            if g[i][j] == 'R':
                dq.append((i, j, 0))
            elif g[i][j] == 'F':
                fresh += 1
    best = 0
    while dq:
        x, y, tm = dq.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < r and 0 <= ny < c and g[nx][ny] == 'F':
                g[nx][ny] = 'R'
                fresh -= 1
                best = max(best, tm + 1)
                dq.append((nx, ny, tm + 1))
    return str(best if fresh == 0 else -1)


def _gen_oranges(seed, r, c, pe, pr):
    rng = _R(seed)
    rows = []
    for _ in range(r):
        row = []
        for _ in range(c):
            x = rng.random()
            row.append('.' if x < pe else ('R' if x < pe + pr else 'F'))
        rows.append("".join(row))
    return "%d %d\n%s\n" % (r, c, "\n".join(rows))


# ---- M8 Lexicographically Smallest Topological Order
def solve_topo(s):
    d = _ints(s)
    n, m = d[0], d[1]
    adj = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    for i in range(m):
        u, v = d[2 + 2 * i], d[3 + 2 * i]
        adj[u].append(v)
        indeg[v] += 1
    h = [i for i in range(1, n + 1) if indeg[i] == 0]
    heapq.heapify(h)
    out = []
    while h:
        u = heapq.heappop(h)
        out.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(h, v)
    if len(out) < n:
        return "IMPOSSIBLE"
    return " ".join(map(str, out))


def _gen_dag(seed, n, m, cycle=False):
    rng = _R(seed)
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    edges = []
    for _ in range(m):
        i, j = rng.randrange(n), rng.randrange(n)
        if i == j:
            j = (i + 1) % n
        if i > j:
            i, j = j, i
        edges.append((perm[i], perm[j]))
    if cycle:
        edges.append((perm[n - 1], perm[n // 2]))
        edges.append((perm[n // 2], perm[n // 2 + 1]))
        edges.append((perm[n // 2 + 1], perm[n - 1]))
    rng.shuffle(edges)
    return edges


# ---- M9 Minimum Spanning Tree Weight
def solve_mst(s):
    d = _ints(s)
    n, m = d[0], d[1]
    edges = sorted((d[4 + 3 * i], d[2 + 3 * i], d[3 + 3 * i]) for i in range(m))
    dsu = _DSU(n)
    total, used = 0, 0
    for w, u, v in edges:
        if dsu.union(u, v):
            total += w
            used += 1
    return str(total if used == n - 1 else -1)


def _gen_wgraph(seed, n, m, wlo, whi, connected=True, directed=False, allow_self=False):
    rng = _R(seed)
    edges = []
    if connected:
        for u, v in _rand_tree_edges(n, rng):
            edges.append((u, v, rng.randint(wlo, whi)))
    while len(edges) < m:
        u, v = rng.randint(1, n), rng.randint(1, n)
        if u == v and not allow_self:
            continue
        edges.append((u, v, rng.randint(wlo, whi)))
    rng.shuffle(edges)
    return edges


def _wgraph_input(n, edges, extra=""):
    return "%d %d%s\n" % (n, len(edges), extra) + "".join("%d %d %d\n" % e for e in edges)


# ---- M10 Running Median
def solve_running_median(s):
    d = _ints(s)
    n, a = d[0], d[1:1 + d[0]]
    lo, hi = [], []  # lo: max-heap (negated), holds the lower half (size >= hi)
    out = []
    for x in a:
        if lo and x > -lo[0]:
            heapq.heappush(hi, x)
        else:
            heapq.heappush(lo, -x)
        if len(lo) > len(hi) + 1:
            heapq.heappush(hi, -heapq.heappop(lo))
        elif len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        out.append(-lo[0])
    return " ".join(map(str, out))


# ---- M11 Dijkstra
def solve_dijkstra(s):
    d = _ints(s)
    n, m, src = d[0], d[1], d[2]
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v, w = d[3 + 3 * i], d[4 + 3 * i], d[5 + 3 * i]
        adj[u].append((v, w))
    INF = float("inf")
    dist = [INF] * (n + 1)
    dist[src] = 0
    h = [(0, src)]
    while h:
        du, u = heapq.heappop(h)
        if du > dist[u]:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(h, (nd, v))
    return " ".join(str(x) if x != INF else "-1" for x in dist[1:])


# ---- M12 Components After Each Connection
def solve_components_online(s):
    d = _ints(s)
    n, q = d[0], d[1]
    dsu = _DSU(n)
    comps = n
    out = []
    for i in range(q):
        if dsu.union(d[2 + 2 * i], d[3 + 2 * i]):
            comps -= 1
        out.append(comps)
    return "\n".join(map(str, out))


# ---- M13 Tree Diameter
def solve_diameter(s):
    d = _ints(s)
    n = d[0]
    adj = _adj_from_edges(n, d, 1)

    def far(src):
        dist = [-1] * (n + 1)
        dist[src] = 0
        order = [src]
        for u in order:
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    order.append(v)
        best = max(range(1, n + 1), key=lambda x: dist[x])
        return best, dist[best]

    a, _ = far(1)
    _, ans = far(a)
    return str(ans)


# =============================================================== HARD

# ---- H1 Longest Increasing Subsequence
def solve_lis(s):
    d = _ints(s)
    n, a = d[0], d[1:1 + d[0]]
    tails = []
    for x in a:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return str(len(tails))


# ---- H2 Matrix Chain Multiplication
def solve_mcm(s):
    d = _ints(s)
    n, p = d[0], d[1:2 + d[0]]
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(0, n - length + 1):
            j = i + length - 1
            best = None
            pi, pj = p[i], p[j + 1]
            row = dp[i]
            for k in range(i, j):
                c = row[k] + dp[k + 1][j] + pi * p[k + 1] * pj
                if best is None or c < best:
                    best = c
            dp[i][j] = best
    return str(dp[0][n - 1])


# ---- H3 Egg Drop
def _egg(k, n):
    if k == 1:
        return n
    f = [0] * (k + 1)  # f[j] = max floors decidable with m moves and j eggs
    m = 0
    while f[k] < n:
        m += 1
        for j in range(k, 0, -1):
            f[j] = f[j] + f[j - 1] + 1
    return m


def solve_egg(s):
    d = _ints(s)
    t = d[0]
    return "\n".join(str(_egg(d[1 + 2 * i], d[2 + 2 * i])) for i in range(t))


# ---- H4 Bellman-Ford With Negative Cycle Detection
def solve_bellman(s):
    d = _ints(s)
    n, m, src = d[0], d[1], d[2]
    edges = [(d[3 + 3 * i], d[4 + 3 * i], d[5 + 3 * i]) for i in range(m)]
    INF = float("inf")
    dist = [INF] * (n + 1)
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return "NEGATIVE CYCLE"
    return " ".join(str(x) if x != INF else "INF" for x in dist[1:])


def _gen_bf(seed, n, m, neg_cycle=False):
    """Directed graph with potentials so that no negative cycles exist, unless neg_cycle."""
    rng = _R(seed)
    pot = [0] + [rng.randint(0, 1000) for _ in range(n)]
    edges = []
    for _ in range(m):
        u, v = rng.randint(1, n), rng.randint(1, n)
        if u == v:
            continue
        w = rng.randint(0, 50) + pot[u] - pot[v]  # reduced cost >= 0 -> no negative cycle
        edges.append((u, v, w))
    if neg_cycle:
        a, b, c = rng.sample(range(2, n + 1), 3)
        edges.append((1, a, 5))
        edges.append((a, b, 2))
        edges.append((b, c, 3))
        edges.append((c, a, -6))
    rng.shuffle(edges)
    return edges


# ---- H5 Lowest Common Ancestor Queries
def solve_lca(s):
    d = _ints(s)
    n = d[0]
    adj = _adj_from_edges(n, d, 1)
    order, par, depth = _bfs_order(n, adj)
    LOG = max(1, n.bit_length())
    up = [par[:]]
    up[0][1] = 1
    for k in range(1, LOG):
        prev = up[-1]
        up.append([prev[prev[v]] for v in range(n + 1)])
    off = 1 + 2 * (n - 1)
    q = d[off]
    out = []
    for i in range(q):
        u, v = d[off + 1 + 2 * i], d[off + 2 + 2 * i]
        if depth[u] < depth[v]:
            u, v = v, u
        diff = depth[u] - depth[v]
        k = 0
        while diff:
            if diff & 1:
                u = up[k][u]
            diff >>= 1
            k += 1
        if u != v:
            for k in range(LOG - 1, -1, -1):
                if up[k][u] != up[k][v]:
                    u, v = up[k][u], up[k][v]
            u = up[0][u]
        out.append(u)
    return "\n".join(map(str, out))


def _gen_lca(seed, n, q, chain=False):
    rng = _R(seed)
    edges = _rand_tree_edges(n, rng, chain=chain)
    qs = ["%d %d" % (rng.randint(1, n), rng.randint(1, n)) for _ in range(q)]
    return _tree_input(n, edges) + "%d\n%s\n" % (q, "\n".join(qs))


# ---- H6 Counting Shortest Paths
def solve_count_paths(s):
    d = _ints(s)
    n, m = d[0], d[1]
    adj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v, w = d[2 + 3 * i], d[3 + 3 * i], d[4 + 3 * i]
        adj[u].append((v, w))
        adj[v].append((u, w))
    INF = float("inf")
    dist = [INF] * (n + 1)
    ways = [0] * (n + 1)
    dist[1], ways[1] = 0, 1
    h = [(0, 1)]
    while h:
        du, u = heapq.heappop(h)
        if du > dist[u]:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < dist[v]:
                dist[v] = nd
                ways[v] = ways[u]
                heapq.heappush(h, (nd, v))
            elif nd == dist[v]:
                ways[v] = (ways[v] + ways[u]) % MOD
    if dist[n] == INF:
        return "-1"
    return "%d %d" % (dist[n], ways[n] % MOD)


def _gen_grid_graph(seed, side, wlo, whi):
    """Grid graph (many equal-length shortest paths) with node 1 top-left and n bottom-right."""
    rng = _R(seed)
    edges = []
    idx = lambda i, j: i * side + j + 1
    for i in range(side):
        for j in range(side):
            if j + 1 < side:
                edges.append((idx(i, j), idx(i, j + 1), rng.randint(wlo, whi)))
            if i + 1 < side:
                edges.append((idx(i, j), idx(i + 1, j), rng.randint(wlo, whi)))
    rng.shuffle(edges)
    return side * side, edges


# ---- H7 Strongly Connected Components
def solve_scc(s):
    d = _ints(s)
    n, m = d[0], d[1]
    adj = [[] for _ in range(n + 1)]
    radj = [[] for _ in range(n + 1)]
    for i in range(m):
        u, v = d[2 + 2 * i], d[3 + 2 * i]
        adj[u].append(v)
        radj[v].append(u)
    # iterative Kosaraju
    seen = [False] * (n + 1)
    finish = []
    for s0 in range(1, n + 1):
        if seen[s0]:
            continue
        seen[s0] = True
        stack = [(s0, 0)]
        while stack:
            u, i = stack[-1]
            if i < len(adj[u]):
                stack[-1] = (u, i + 1)
                v = adj[u][i]
                if not seen[v]:
                    seen[v] = True
                    stack.append((v, 0))
            else:
                stack.pop()
                finish.append(u)
    comp = [0] * (n + 1)
    sizes = []
    for s0 in reversed(finish):
        if comp[s0]:
            continue
        cid = len(sizes) + 1
        comp[s0] = cid
        st = [s0]
        cnt = 0
        while st:
            u = st.pop()
            cnt += 1
            for v in radj[u]:
                if not comp[v]:
                    comp[v] = cid
                    st.append(v)
        sizes.append(cnt)
    sizes.sort(reverse=True)
    return "%d\n%s" % (len(sizes), " ".join(map(str, sizes)))


def _gen_scc(seed, n, m, groups):
    """Random directed graph with planted cycles inside groups plus random DAG-ish edges."""
    rng = _R(seed)
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    cuts = sorted(rng.sample(range(1, n), groups - 1))
    blocks, prev = [], 0
    for c in cuts + [n]:
        blocks.append(perm[prev:c])
        prev = c
    edges = []
    for b in blocks:
        if len(b) > 1 and rng.random() < 0.8:
            for i in range(len(b)):
                edges.append((b[i], b[(i + 1) % len(b)]))
    pos = {v: i for i, v in enumerate(perm)}
    while len(edges) < m:
        u, v = rng.randint(1, n), rng.randint(1, n)
        if pos[u] > pos[v]:
            u, v = v, u
        if u != v:
            edges.append((u, v))
    rng.shuffle(edges)
    return edges


# ---- H8 Maximum XOR Pair
def solve_max_xor(s):
    d = _ints(s)
    n, a = d[0], d[1:1 + d[0]]
    ans = 0
    for bit in range(29, -1, -1):
        cand = ans | (1 << bit)
        pref = {x >> bit for x in a}
        if any((p ^ (cand >> bit)) in pref for p in pref):
            ans = cand
    return str(ans)


# ---- H9 Sum of Distances in a Tree
def solve_sum_dist(s):
    d = _ints(s)
    n = d[0]
    adj = _adj_from_edges(n, d, 1)
    order, par, depth = _bfs_order(n, adj)
    size = [1] * (n + 1)
    for u in reversed(order):
        if u != 1:
            size[par[u]] += size[u]
    res = [0] * (n + 1)
    res[1] = sum(depth[1:])
    for u in order:
        if u != 1:
            res[u] = res[par[u]] + n - 2 * size[u]
    return " ".join(map(str, res[1:]))


# =============================================================== TESTS

def _t_climb():
    return ["3\n", "5\n", "1\n", "2\n", "10\n", "45\n", "70\n", "90\n"]


def _t_robber():
    r = _R(403)
    big = [r.randint(0, 10000) for _ in range(30000)]
    return ["4\n1 2 3 1\n", "5\n2 7 9 3 1\n", "1\n5\n", "2\n0 0\n",
            "6\n10 1 1 10 1 10\n", "3\n2 1 1\n",
            "30000\n%s\n" % " ".join(map(str, big)),
            "20000\n%s\n" % " ".join(["10000"] * 20000)]


def _t_grid_paths():
    return ["3 3\n...\n.#.\n...\n", "3 4\n....\n.#..\n....\n", "1 1\n.\n", "2 2\n.#\n#.\n",
            "1 5\n.....\n", "2 2\n#.\n..\n", "4 4\n....\n....\n....\n...#\n",
            _gen_grid(404, 300, 300, 0.05), _gen_grid(405, 200, 250, 0.25)]


def _t_flood():
    return ["3 4\naabb\nabbb\naaab\n1 1 x\n", "2 3\nabc\nabc\n0 0 c\n",
            "1 1\nq\n0 0 q\n", "3 3\naaa\naaa\naaa\n2 2 a\n", "3 3\naba\nbab\naba\n1 1 c\n",
            "4 5\nccccc\ncdddc\ncdcdc\nccccc\n2 2 e\n",
            _gen_flood(406, 300, 300, "ab", 0.45), _gen_flood(407, 250, 300, "abc", 0.6)]


def _t_components():
    r = _R(408)
    t = []
    t.append(_graph_input(5, [(1, 2), (2, 3), (4, 5)]))
    t.append(_graph_input(6, [(1, 2), (3, 4), (2, 1)]))
    t.append(_graph_input(1, []))
    t.append(_graph_input(4, []))
    t.append(_graph_input(3, [(1, 1), (2, 3), (3, 2)]))
    t.append(_graph_input(20000, _rand_graph(20000, 14000, r, allow_self=True)))
    t.append(_graph_input(15000, _rand_graph(15000, 15000, r)))
    return t


def _t_tree_height():
    return ["5\n0 1 1 2 2\n", "4\n2 0 2 3\n", "1\n0\n", "3\n0 1 1\n",
            "6\n2 3 4 5 6 0\n", _gen_parent_array(409, 25000, chain=True),
            _gen_parent_array(410, 25000), _gen_parent_array(411, 20000)]


def _t_k_smallest():
    return ["6 3\n7 2 9 4 2 8\n", "5 5\n-3 10 0 -3 5\n", "1 1\n42\n", "4 1\n5 5 5 5\n",
            "5 2\n1000000000 -1000000000 0 999999999 -999999999\n",
            "17000 10\n%s\n" % _gen_arr(412, 17000, -10 ** 9, 10 ** 9),
            "20000 5000\n%s\n" % _gen_arr(413, 20000, -1000, 1000)]


def _t_prefix():
    return ["4\napple\napp\napply\nbanana\n3\napp\nb\ncar\n",
            "3\nto\nto\ntea\n4\nt\nto\nte\ntoo\n",
            "1\na\n2\na\nb\n", "2\nabc\nabd\n3\nab\nabc\nabcd\n",
            _gen_words(414, 10000, 10000, "abc", 8), _gen_words(415, 8000, 8000, "abcdefghij", 12)]


def _t_bfs():
    r = _R(416)
    t = ["6 6 1 5\n1 2\n1 3\n2 4\n3 4\n4 5\n5 6\n", "4 2 1 4\n1 2\n3 4\n", "1 0 1 1\n",
         "3 3 3 3\n1 2\n2 3\n3 1\n", "5 4 1 5\n1 2\n2 3\n3 4\n4 5\n"]
    n = 16000
    e = [(i, i + 1) for i in range(1, n)]
    r.shuffle(e)
    t.append("%d %d 1 %d\n" % (n, len(e), n) + "".join("%d %d\n" % x for x in e))
    e = _rand_graph(15000, 15000, r)
    t.append("%d %d 1 15000\n" % (15000, len(e)) + "".join("%d %d\n" % x for x in e))
    e = _rand_graph(20000, 9000, r)
    t.append("%d %d 7 19999\n" % (20000, len(e)) + "".join("%d %d\n" % x for x in e))
    return t


def _t_level():
    r = _R(417)
    return [_tree_input(7, [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (5, 7)]),
            _tree_input(5, [(3, 1), (1, 5), (5, 2), (4, 1)]),
            "1\n", _tree_input(2, [(2, 1)]),
            _tree_input(6, [(1, 6), (6, 5), (5, 4), (4, 3), (3, 2)]),
            _tree_input(15000, _rand_tree_edges(15000, r)),
            _tree_input(15000, _rand_tree_edges(15000, r, chain=True))]


def _t_coin_min():
    return ["3 11\n1 2 5\n", "1 3\n2\n", "1 0\n7\n", "2 7\n2 4\n", "4 63\n1 5 10 21\n",
            "3 6249\n186 419 83\n",
            _gen_coins(418, 100, 1, 10000, 10000), _gen_coins(419, 50, 500, 3000, 9999),
            _gen_coins(420, 3, 997, 1009, 10000)]


def _t_coin_ways():
    return ["3 5\n1 2 5\n", "1 3\n2\n", "1 0\n10\n", "1 10\n10\n", "4 100\n1 5 10 25\n",
            "2 7\n3 5\n", _gen_coins(421, 50, 1, 1000, 50000), _gen_coins(422, 20, 1, 100, 50000)]


def _t_lcs():
    return ["abcde\nace\n", "abc\ndef\n", "a\na\n", "aaaa\naa\n", "xmjyauz\nmzjawxu\n",
            _gen_two_strings(423, 1500, 1500, "abcd"), _gen_two_strings(424, 1200, 1500, "abcdefghijklmnopqrstuvwxyz"),
            _gen_two_strings(425, 1, 1500, "ab")]


def _t_edit():
    return ["horse\nros\n", "intention\nexecution\n", "a\na\n", "abc\nxyz\n", "a\nabcdef\n",
            "kitten\nsitting\n", _gen_two_strings(426, 1000, 1000, "abc"),
            _gen_two_strings(427, 1000, 800, "abcdefghijklmnopqrstuvwxyz")]


def _t_knap():
    return ["3 50\n10 60\n20 100\n30 120\n", "4 5\n1 1\n3 4\n4 5\n5 7\n", "1 1\n2 100\n",
            "2 10\n10 5\n10 6\n", "3 6\n2 1000000000\n2 1000000000\n2 1000000000\n",
            _gen_knap(428, 100, 10000, 1000, 10 ** 9), _gen_knap(429, 100, 5000, 200, 1000),
            _gen_knap(430, 60, 10000, 10000, 10 ** 6)]


def _t_decode():
    return ["226\n", "12\n", "0\n", "06\n", "10\n", "100\n", "2101\n", "11106\n",
            "1" * 5000 + "\n", _gen_decode(431, 100000, 0.15)]


def _t_rotting():
    return ["3 3\nRFF\nFF.\n.FF\n", "3 3\nRFF\n.FF\nF.F\n", "1 2\n.R\n", "1 1\nF\n",
            "2 2\n..\n..\n", "1 5\nFFFFR\n",
            _gen_oranges(432, 300, 300, 0.1, 0.0005), _gen_oranges(433, 250, 300, 0.0, 0.0002),
            "1 600\nR" + "F" * 599 + "\n"]


def _t_topo():
    t = [_graph_input(5, [(3, 1), (1, 2), (3, 4), (4, 2)]),
         _graph_input(3, [(1, 2), (2, 3), (3, 1)]),
         _graph_input(1, []), _graph_input(4, []),
         _graph_input(4, [(4, 3), (3, 2), (2, 1)]),
         _graph_input(3, [(2, 2)]),
         _graph_input(15000, _gen_dag(434, 15000, 15000)),
         _graph_input(12000, _gen_dag(435, 12000, 14000, cycle=True)),
         _graph_input(15000, _gen_dag(436, 15000, 5000))]
    return t


def _t_mst():
    return [_wgraph_input(4, [(1, 2, 1), (2, 3, 4), (1, 3, 3), (3, 4, 2), (1, 4, 5)]),
            _wgraph_input(4, [(1, 2, 3), (3, 4, 1)]),
            _wgraph_input(1, []), _wgraph_input(2, [(1, 2, 7), (1, 2, 3), (2, 2, 1)]),
            _wgraph_input(3, [(1, 2, 1000000), (2, 3, 1000000), (1, 3, 1000000)]),
            _wgraph_input(5000, _gen_wgraph(437, 5000, 11000, 1, 10 ** 6)),
            _wgraph_input(8000, _gen_wgraph(438, 8000, 10000, 1, 10)),
            _wgraph_input(6000, _gen_wgraph(439, 6000, 9000, 1, 10 ** 6, connected=False))]


def _t_median():
    r = _R(440)
    return ["5\n5 15 1 3 8\n", "4\n2 2 2 2\n", "1\n-7\n", "2\n10 -10\n",
            "6\n1 2 3 4 5 6\n", "6\n6 5 4 3 2 1\n",
            "18000\n%s\n" % _gen_arr(441, 18000, -10 ** 9, 10 ** 9),
            "20000\n%s\n" % " ".join(str(20000 - i) for i in range(20000)),
            "20000\n%s\n" % _gen_arr(442, 20000, 0, 50)]


def _t_dijkstra():
    return [_wgraph_input(5, [(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 5), (3, 4, 8)], " 1"),
            _wgraph_input(3, [(2, 1, 5), (2, 3, 1)], " 2"),
            _wgraph_input(1, [], " 1"), _wgraph_input(3, [(1, 2, 0), (2, 3, 0)], " 1"),
            _wgraph_input(4, [(1, 2, 1000000000), (2, 3, 1000000000), (3, 4, 1000000000)], " 1"),
            _wgraph_input(8000, _gen_wgraph(443, 8000, 9000, 1, 10 ** 9, connected=False), " 1"),
            _wgraph_input(5000, _gen_wgraph(444, 5000, 11000, 0, 1000), " 2500")]


def _t_comp_online():
    r = _R(445)
    return [_graph_input(5, [(1, 2), (3, 4), (2, 1), (2, 3), (5, 5), (4, 5)]),
            _graph_input(3, [(1, 3), (3, 2)]),
            _graph_input(1, [(1, 1)]), _graph_input(4, [(1, 2), (1, 2), (3, 4), (2, 3)]),
            _graph_input(20000, _rand_graph(20000, 15000, r, allow_self=True)),
            _graph_input(10000, [(i, i + 1) for i in range(1, 10000)] + [(1, 10000)] * 10)]


def _t_diameter():
    r = _R(446)
    return [_tree_input(5, [(1, 2), (1, 3), (2, 4), (2, 5)]),
            _tree_input(6, [(1, 2), (2, 3), (3, 4), (2, 5), (5, 6)]),
            "1\n", _tree_input(2, [(1, 2)]),
            _tree_input(5, [(1, 2), (1, 3), (1, 4), (1, 5)]),
            _tree_input(16000, _rand_tree_edges(16000, r)),
            _tree_input(16000, _rand_tree_edges(16000, r, chain=True))]


def _t_lis():
    r = _R(447)
    return ["8\n10 9 2 5 3 7 101 18\n", "6\n0 1 0 3 2 3\n", "1\n5\n", "5\n7 7 7 7 7\n",
            "5\n5 4 3 2 1\n", "6\n-5 -3 -4 0 -1 2\n",
            "25000\n%s\n" % _gen_arr(448, 25000, 0, 10 ** 6),
            "25000\n%s\n" % " ".join(str(i // 2 + r.randint(0, 3)) for i in range(25000)),
            "25000\n%s\n" % " ".join(str(i) for i in range(25000))]


def _t_mcm():
    r = _R(449)
    return ["3\n10 30 5 60\n", "4\n40 20 30 10 30\n", "1\n5 10\n", "2\n1 2 3\n",
            "5\n5 10 3 12 5 50\n",
            "200\n%s\n" % " ".join(str(r.randint(1, 100)) for _ in range(201)),
            "200\n%s\n" % " ".join(["100"] * 201),
            "150\n%s\n" % " ".join(str(r.randint(1, 100)) for _ in range(151))]


def _t_egg():
    r = _R(450)
    big = ["%d %d" % (r.randint(1, 100), r.randint(1, 10 ** 9)) for _ in range(400)]
    big += ["2 %d" % r.randint(10 ** 8, 10 ** 9) for _ in range(50)]
    return ["3\n1 2\n2 6\n3 14\n", "2\n2 100\n2 36\n", "1\n1 1\n", "1\n100 1\n",
            "1\n1 1000000000\n", "3\n2 1000000000\n3 1000000000\n100 1000000000\n",
            "%d\n%s\n" % (len(big), "\n".join(big))]


def _t_bellman():
    return [_wgraph_input(5, [(1, 2, 6), (1, 3, 7), (2, 4, 5), (3, 4, -3), (4, 2, -2), (2, 5, -4)], " 1"),
            _wgraph_input(3, [(1, 2, 1), (2, 3, -2), (3, 2, 1)], " 1"),
            _wgraph_input(4, [(1, 2, 2), (3, 4, -5), (4, 3, 1)], " 1"),
            _wgraph_input(1, [], " 1"),
            _wgraph_input(3, [(2, 1, -1000000), (2, 3, -1000000)], " 2"),
            _wgraph_input(500, _gen_bf(451, 500, 5000), " 1"),
            _wgraph_input(500, _gen_bf(452, 500, 5000, neg_cycle=True), " 1"),
            _wgraph_input(400, [(i, i + 1, -1000) for i in range(399, 0, -1)], " 1")]


def _t_lca():
    return [_tree_input(7, [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (5, 7)]) + "4\n4 5\n7 4\n6 7\n3 3\n",
            _tree_input(4, [(1, 2), (2, 3), (3, 4)]) + "3\n4 2\n1 4\n3 4\n",
            "1\n1\n1 1\n",
            _tree_input(3, [(2, 1), (3, 1)]) + "2\n2 3\n2 2\n",
            _gen_lca(453, 10000, 8000), _gen_lca(454, 10000, 8000, chain=True)]


def _t_count_paths():
    n1, e1 = _gen_grid_graph(455, 85, 1, 1)
    n2, e2 = _gen_grid_graph(456, 80, 1, 2)
    return [_wgraph_input(4, [(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 4, 1), (1, 4, 3)]),
            _wgraph_input(4, [(1, 2, 2), (2, 4, 2), (1, 3, 1), (3, 4, 2), (1, 4, 4)]),
            _wgraph_input(3, [(1, 2, 5)]), _wgraph_input(1, []),
            _wgraph_input(2, [(1, 2, 3), (1, 2, 3), (2, 1, 3)]),
            _wgraph_input(n1, e1), _wgraph_input(n2, e2),
            _wgraph_input(6000, _gen_wgraph(457, 6000, 10000, 1, 5))]


def _t_scc():
    return [_graph_input(5, [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)]),
            _graph_input(6, [(1, 2), (2, 1), (3, 4), (4, 5), (5, 3), (5, 6)]),
            _graph_input(1, []), _graph_input(3, [(1, 1), (1, 2)]),
            _graph_input(4, [(1, 2), (2, 3), (3, 4), (4, 1)]),
            _graph_input(15000, _gen_scc(458, 15000, 15000, 300)),
            _graph_input(15000, [(i, i + 1) for i in range(1, 15000)] + [(15000, 1)]),
            _graph_input(15000, [(i + 1, i) for i in range(1, 15000)])]


def _t_xor():
    r = _R(459)
    return ["6\n3 10 5 25 2 8\n", "3\n1 2 3\n", "2\n0 0\n", "2\n0 1073741823\n",
            "4\n7 7 7 7\n",
            "18000\n%s\n" % _gen_arr(460, 18000, 0, 2 ** 30 - 1),
            "20000\n%s\n" % " ".join(str(r.randint(0, 2 ** 29 - 1) | (2 ** 29 if r.random() < 0.0005 else 0) )
                                     for _ in range(20000))]


def _t_sum_dist():
    r = _R(461)
    return [_tree_input(6, [(1, 2), (1, 3), (3, 4), (3, 5), (3, 6)]),
            _tree_input(4, [(1, 2), (2, 3), (3, 4)]),
            "1\n", _tree_input(2, [(2, 1)]),
            _tree_input(5, [(3, 1), (3, 2), (3, 4), (3, 5)]),
            _tree_input(15000, _rand_tree_edges(15000, r)),
            _tree_input(15000, _rand_tree_edges(15000, r, chain=True))]


# =============================================================== PROBLEMS

PROBLEMS = [
    # ------------------------------------------------------------- EASY
    {
        "title": "Climbing Stairs",
        "difficulty": "EASY",
        "tags": "Dynamic Programming,Math",
        "description": (
            "You are standing at the bottom of a staircase with n steps. In one move you can climb "
            "either 1 step or 2 steps. Count the number of distinct sequences of moves that take you "
            "exactly to the top (step n).\n"
            "Example: for n = 3 there are 3 ways: 1+1+1, 1+2 and 2+1."
        ),
        "input_format": "A single integer n.",
        "output_format": "Print the number of distinct ways to reach step n.",
        "constraints": "1 <= n <= 90\nThe answer can exceed the 32-bit integer range; use a 64-bit integer type.",
        "solve": solve_climb,
        "tests": _t_climb(),
    },
    {
        "title": "Min Cost Climbing Stairs",
        "difficulty": "EASY",
        "tags": "Dynamic Programming",
        "description": (
            "A staircase has n steps numbered 0 to n-1, and stepping on step i costs cost[i]. You may "
            "start on step 0 or step 1 for free (you still pay the cost of the step you stand on before "
            "leaving it). From step i you can move to step i+1 or i+2, paying cost[i]. The top of the "
            "staircase is just beyond step n-1 (position n). Find the minimum total cost to reach the top.\n"
            "Example: cost = [10, 15, 20]: start on step 1, pay 15 and jump two steps to the top. Answer 15."
        ),
        "input_format": "The first line contains n.\nThe second line contains n integers cost[0] .. cost[n-1].",
        "output_format": "Print the minimum cost to reach the top.",
        "constraints": "2 <= n <= 100000\n0 <= cost[i] <= 1000",
        "solve": solve_mincost_stairs,
        "tests": ["3\n10 15 20\n", "10\n1 100 1 1 1 100 1 1 100 1\n", "2\n5 3\n", "2\n0 0\n",
                  "5\n1 1 1 1 1\n", "4\n0 1000 0 1000\n",
                  _gen_mincost(401, 45000, 1000), _gen_mincost(402, 50000, 5)],
    },
    {
        "title": "House Robber",
        "difficulty": "EASY",
        "tags": "Dynamic Programming",
        "description": (
            "Houses along a street contain some amount of money each. A robber wants to maximize the "
            "total amount stolen, but cannot rob two adjacent houses (the alarm would go off). Given the "
            "amounts in each house, find the maximum amount that can be robbed.\n"
            "Example: [2, 7, 9, 3, 1] -> rob houses with 2, 9 and 1 for a total of 12."
        ),
        "input_format": "The first line contains n, the number of houses.\nThe second line contains n integers, the money in each house.",
        "output_format": "Print the maximum amount that can be robbed.",
        "constraints": "1 <= n <= 100000\n0 <= money[i] <= 10000",
        "solve": solve_robber,
        "tests": _t_robber(),
    },
    {
        "title": "Grid Paths With Obstacles",
        "difficulty": "EASY",
        "tags": "Dynamic Programming,Matrix",
        "description": (
            "A robot starts at the top-left cell of an r x c grid and wants to reach the bottom-right cell. "
            "It can only move right or down, one cell at a time. Some cells are blocked ('#') and cannot be "
            "entered; free cells are '.'. Count the number of different paths the robot can take. If the "
            "start or end cell is blocked the answer is 0. Since the answer can be huge, print it modulo 1000000007."
        ),
        "input_format": "The first line contains two integers r and c.\nEach of the next r lines contains a string of c characters, each '.' or '#'.",
        "output_format": "Print the number of paths modulo 1000000007.",
        "constraints": "1 <= r, c <= 300",
        "solve": solve_grid_paths,
        "tests": _t_grid_paths(),
    },
    {
        "title": "Flood Fill",
        "difficulty": "EASY",
        "tags": "Graphs,Breadth-First Search,Matrix",
        "description": (
            "An image is given as a grid of lowercase letters, each letter being a color. Starting from "
            "cell (sr, sc), repaint that cell and every cell connected to it (moving up, down, left or "
            "right through cells of the same original color) with a new color. Print the resulting image. "
            "If the new color equals the original color, the image does not change.\n"
            "Large grids make a recursive fill overflow the stack, so an iterative BFS/DFS is recommended."
        ),
        "input_format": (
            "The first line contains r and c.\nEach of the next r lines contains a string of c lowercase letters.\n"
            "The last line contains sr, sc (0-indexed row and column) and the new color, a lowercase letter."
        ),
        "output_format": "Print the r rows of the resulting image, one per line.",
        "constraints": "1 <= r, c <= 300\n0 <= sr < r, 0 <= sc < c",
        "solve": solve_flood,
        "tests": _t_flood(),
    },
    {
        "title": "Count Connected Components",
        "difficulty": "EASY",
        "tags": "Graphs,Union Find,Depth-First Search",
        "description": (
            "An undirected graph has n vertices numbered 1 to n and m edges. Count the number of connected "
            "components, i.e. the number of groups of vertices where every vertex can reach every other vertex "
            "of its group. An isolated vertex is a component by itself. Edges may repeat and self-loops may appear."
        ),
        "input_format": "The first line contains n and m.\nEach of the next m lines contains two integers u and v, an edge between u and v.",
        "output_format": "Print the number of connected components.",
        "constraints": "1 <= n <= 100000\n0 <= m <= 200000\n1 <= u, v <= n",
        "solve": solve_components,
        "tests": _t_components(),
    },
    {
        "title": "Height of a Tree",
        "difficulty": "EASY",
        "tags": "Trees,Breadth-First Search",
        "description": (
            "A rooted tree has n nodes numbered 1 to n and is given by a parent array: parent[i] is the parent "
            "of node i, and the root has parent 0. The height of the tree is the number of edges on the longest "
            "path from the root down to any node. Compute the height (a single node has height 0).\n"
            "The tree can be a long chain, so an iterative traversal is recommended."
        ),
        "input_format": "The first line contains n.\nThe second line contains n integers parent[1] .. parent[n]. Exactly one of them is 0.",
        "output_format": "Print the height of the tree.",
        "constraints": "1 <= n <= 100000\nThe input always describes a valid rooted tree.",
        "solve": solve_tree_height,
        "tests": _t_tree_height(),
    },
    {
        "title": "K Smallest Elements",
        "difficulty": "EASY",
        "tags": "Heap,Sorting",
        "description": (
            "Given an array of n integers and a number k, print the k smallest elements of the array in "
            "non-decreasing order. Duplicates count separately: if the smallest value appears twice, both "
            "copies are printed. A max-heap of size k solves this in O(n log k)."
        ),
        "input_format": "The first line contains n and k.\nThe second line contains n integers.",
        "output_format": "Print the k smallest elements in non-decreasing order, separated by single spaces.",
        "constraints": "1 <= k <= n <= 100000\n-1000000000 <= a[i] <= 1000000000",
        "solve": solve_k_smallest,
        "tests": _t_k_smallest(),
    },
    {
        "title": "Count Words With Prefix",
        "difficulty": "EASY",
        "tags": "Trie,Strings",
        "description": (
            "You are given a dictionary of n words (words may repeat; each occurrence counts) followed by q "
            "queries. For each query string p, print how many dictionary words start with p. A word counts "
            "as starting with itself.\n"
            "Example: words apple, app, apply, banana; the prefix app matches 3 words."
        ),
        "input_format": (
            "The first line contains n.\nEach of the next n lines contains a word.\n"
            "The next line contains q.\nEach of the next q lines contains a query prefix."
        ),
        "output_format": "For each query print the count on its own line.",
        "constraints": "1 <= n, q <= 20000\nWords and prefixes consist of lowercase letters, length 1 to 20.",
        "solve": solve_prefix_count,
        "tests": _t_prefix(),
    },
    {
        "title": "Shortest Path in an Unweighted Graph",
        "difficulty": "EASY",
        "tags": "Graphs,Breadth-First Search",
        "description": (
            "An undirected graph has n vertices numbered 1 to n and m edges, all of length 1. Find the "
            "minimum number of edges on a path from vertex s to vertex t. If t cannot be reached from s, "
            "print -1. The distance from a vertex to itself is 0."
        ),
        "input_format": "The first line contains n, m, s and t.\nEach of the next m lines contains two integers u and v, an edge between u and v.",
        "output_format": "Print the length of the shortest path, or -1 if t is unreachable.",
        "constraints": "1 <= n <= 100000\n0 <= m <= 200000\n1 <= s, t, u, v <= n",
        "solve": solve_bfs_path,
        "tests": _t_bfs(),
    },
    {
        "title": "Level Order Traversal of a Tree",
        "difficulty": "EASY",
        "tags": "Trees,Breadth-First Search",
        "description": (
            "A tree with n nodes numbered 1 to n is rooted at node 1. Group the nodes by their depth (the root "
            "has depth 0, its children depth 1, and so on) and print one line per depth level, starting with "
            "the root's level. Within a line, print the node numbers in increasing order."
        ),
        "input_format": "The first line contains n.\nEach of the next n-1 lines contains two integers u and v, an edge of the tree.",
        "output_format": "Print one line per level: the node numbers of that level in increasing order, separated by spaces.",
        "constraints": "1 <= n <= 100000\nThe edges always form a tree.",
        "solve": solve_level_order,
        "tests": _t_level(),
    },

    # ------------------------------------------------------------- MEDIUM
    {
        "title": "Coin Change: Minimum Coins",
        "difficulty": "MEDIUM",
        "tags": "Dynamic Programming",
        "description": (
            "You have coins of n distinct denominations and an unlimited supply of each. Find the minimum "
            "number of coins whose values add up exactly to the given amount. If it is impossible, print -1. "
            "An amount of 0 needs 0 coins.\n"
            "Example: coins 1, 2, 5 and amount 11 -> 3 coins (5 + 5 + 1)."
        ),
        "input_format": "The first line contains n and amount.\nThe second line contains n distinct coin values.",
        "output_format": "Print the minimum number of coins, or -1 if the amount cannot be formed.",
        "constraints": "1 <= n <= 100\n0 <= amount <= 10000\n1 <= coin <= 10000",
        "solve": solve_coin_min,
        "tests": _t_coin_min(),
    },
    {
        "title": "Coin Change: Number of Ways",
        "difficulty": "MEDIUM",
        "tags": "Dynamic Programming",
        "description": (
            "You have coins of n distinct denominations and an unlimited supply of each. Count the number of "
            "different combinations of coins that sum exactly to the given amount. The order of coins does not "
            "matter: 1+2 and 2+1 are the same combination. There is exactly 1 way to make amount 0. Print the "
            "count modulo 1000000007.\n"
            "Example: coins 1, 2, 5 and amount 5 -> 4 ways (5, 2+2+1, 2+1+1+1, 1+1+1+1+1)."
        ),
        "input_format": "The first line contains n and amount.\nThe second line contains n distinct coin values.",
        "output_format": "Print the number of combinations modulo 1000000007.",
        "constraints": "1 <= n <= 50\n0 <= amount <= 50000\n1 <= coin <= 50000",
        "solve": solve_coin_ways,
        "tests": _t_coin_ways(),
    },
    {
        "title": "Longest Common Subsequence",
        "difficulty": "MEDIUM",
        "tags": "Dynamic Programming,Strings",
        "description": (
            "A subsequence of a string is obtained by deleting zero or more characters without changing the "
            "order of the remaining ones. Given two strings a and b, find the length of their longest common "
            "subsequence.\n"
            "Example: a = abcde, b = ace -> the longest common subsequence is ace, of length 3."
        ),
        "input_format": "The first line contains string a.\nThe second line contains string b.",
        "output_format": "Print the length of the longest common subsequence.",
        "constraints": "1 <= |a|, |b| <= 1500\nBoth strings consist of lowercase English letters.",
        "solve": solve_lcs,
        "tests": _t_lcs(),
    },
    {
        "title": "Edit Distance",
        "difficulty": "MEDIUM",
        "tags": "Dynamic Programming,Strings",
        "description": (
            "Given two strings a and b, find the minimum number of operations needed to turn a into b. "
            "Allowed operations are: insert a character, delete a character, or replace a character with another.\n"
            "Example: horse -> ros needs 3 operations (replace h with r, delete r, delete e)."
        ),
        "input_format": "The first line contains string a.\nThe second line contains string b.",
        "output_format": "Print the minimum number of operations.",
        "constraints": "1 <= |a|, |b| <= 1000\nBoth strings consist of lowercase English letters.",
        "solve": solve_edit,
        "tests": _t_edit(),
    },
    {
        "title": "0/1 Knapsack",
        "difficulty": "MEDIUM",
        "tags": "Dynamic Programming",
        "description": (
            "You have n items, each with a weight and a value, and a knapsack that can carry a total weight of "
            "at most W. Each item can be taken at most once. Choose items to maximize the total value without "
            "exceeding the weight limit, and print that maximum value (0 if nothing fits)."
        ),
        "input_format": "The first line contains n and W.\nEach of the next n lines contains two integers: the weight and the value of an item.",
        "output_format": "Print the maximum total value.",
        "constraints": (
            "1 <= n <= 100\n1 <= W <= 10000\n1 <= weight <= 10000\n1 <= value <= 1000000000\n"
            "The answer can exceed the 32-bit integer range; use a 64-bit integer type."
        ),
        "solve": solve_knapsack,
        "tests": _t_knap(),
    },
    {
        "title": "Decode Ways",
        "difficulty": "MEDIUM",
        "tags": "Dynamic Programming,Strings",
        "description": (
            "A message of letters was encoded with A=1, B=2, ..., Z=26 and the numbers were written one after "
            "another without separators. Given the digit string, count how many different letter messages "
            "could have produced it. A code may not have a leading zero, so 06 is not a valid code and a lone 0 "
            "cannot be decoded. Print the count modulo 1000000007 (it may be 0).\n"
            "Example: 226 can be BZ (2 26), VF (22 6) or BBF (2 2 6), so the answer is 3."
        ),
        "input_format": "A single line containing the digit string s.",
        "output_format": "Print the number of decodings modulo 1000000007.",
        "constraints": "1 <= |s| <= 100000\ns consists of digits 0-9.",
        "solve": solve_decode,
        "tests": _t_decode(),
    },
    {
        "title": "Rotting Oranges",
        "difficulty": "MEDIUM",
        "tags": "Graphs,Breadth-First Search,Matrix",
        "description": (
            "A grid contains empty cells '.', fresh oranges 'F' and rotten oranges 'R'. Every minute, each "
            "fresh orange that is directly up, down, left or right of a rotten orange becomes rotten. Find the "
            "minimum number of minutes until no fresh orange remains. If some fresh orange can never rot, "
            "print -1. If there are no fresh oranges at the start, the answer is 0."
        ),
        "input_format": "The first line contains r and c.\nEach of the next r lines contains a string of c characters from '.', 'F', 'R'.",
        "output_format": "Print the number of minutes, or -1.",
        "constraints": "1 <= r, c <= 600\nr * c <= 90000",
        "solve": solve_rotting,
        "tests": _t_rotting(),
    },
    {
        "title": "Lexicographically Smallest Topological Order",
        "difficulty": "MEDIUM",
        "tags": "Graphs,Topological Sort,Heap",
        "description": (
            "There are n tasks numbered 1 to n and m requirements of the form u v, meaning task u must be done "
            "before task v. Print an order of all tasks that satisfies every requirement. If several orders "
            "exist, print the lexicographically smallest one (the one whose first task is as small as possible, "
            "then the second, and so on). If no valid order exists because the requirements contain a cycle, "
            "print IMPOSSIBLE."
        ),
        "input_format": "The first line contains n and m.\nEach of the next m lines contains two integers u and v.",
        "output_format": "Print the n task numbers separated by spaces, or the word IMPOSSIBLE.",
        "constraints": "1 <= n <= 100000\n0 <= m <= 200000\n1 <= u, v <= n (u may equal v, which is a cycle)",
        "solve": solve_topo,
        "tests": _t_topo(),
    },
    {
        "title": "Minimum Spanning Tree",
        "difficulty": "MEDIUM",
        "tags": "Graphs,Union Find,Greedy",
        "description": (
            "An undirected weighted graph has n vertices and m edges. A spanning tree connects all n vertices "
            "using n-1 of the edges. Find the minimum possible total weight of a spanning tree (Kruskal's or "
            "Prim's algorithm). If the graph is disconnected, print -1. For n = 1 the answer is 0. Parallel "
            "edges and self-loops may appear."
        ),
        "input_format": "The first line contains n and m.\nEach of the next m lines contains u, v and w: an edge between u and v with weight w.",
        "output_format": "Print the total weight of a minimum spanning tree, or -1.",
        "constraints": (
            "1 <= n <= 100000\n0 <= m <= 200000\n1 <= w <= 1000000\n"
            "The answer can exceed the 32-bit integer range; use a 64-bit integer type."
        ),
        "solve": solve_mst,
        "tests": _t_mst(),
    },
    {
        "title": "Running Median",
        "difficulty": "MEDIUM",
        "tags": "Heap,Data Stream",
        "description": (
            "Numbers arrive one at a time. After each new number, report the median of all numbers seen so "
            "far. When the count k is even, report the lower median, i.e. the element at position k/2 in sorted "
            "order (1-indexed); when k is odd, report the middle element at position (k+1)/2. Two heaps "
            "(a max-heap for the lower half, a min-heap for the upper half) give O(log n) per number.\n"
            "Example: 5 15 1 3 -> medians 5 5 5 3."
        ),
        "input_format": "The first line contains n.\nThe second line contains n integers in arrival order.",
        "output_format": "Print n integers on one line separated by spaces: the median after each insertion.",
        "constraints": "1 <= n <= 100000\n-1000000000 <= a[i] <= 1000000000",
        "solve": solve_running_median,
        "tests": _t_median(),
    },
    {
        "title": "Single Source Shortest Paths",
        "difficulty": "MEDIUM",
        "tags": "Graphs,Shortest Path,Heap",
        "description": (
            "A directed graph has n vertices numbered 1 to n and m edges with non-negative weights. For every "
            "vertex, find the length of the shortest path from the source vertex s (Dijkstra's algorithm). "
            "Print -1 for vertices that cannot be reached. The distance from s to itself is 0."
        ),
        "input_format": "The first line contains n, m and s.\nEach of the next m lines contains u, v and w: a directed edge from u to v with weight w.",
        "output_format": "Print n integers separated by spaces: the distance to vertices 1, 2, ..., n (or -1).",
        "constraints": (
            "1 <= n <= 100000\n0 <= m <= 200000\n0 <= w <= 1000000000\n"
            "Distances can exceed the 32-bit integer range; use a 64-bit integer type."
        ),
        "solve": solve_dijkstra,
        "tests": _t_dijkstra(),
    },
    {
        "title": "Components After Each Connection",
        "difficulty": "MEDIUM",
        "tags": "Union Find,Graphs",
        "description": (
            "There are n computers numbered 1 to n, initially with no cables between them. Cables are added "
            "one at a time; each cable connects two computers (possibly ones that are already connected, or a "
            "computer to itself). After each cable is added, print the number of separate networks (connected "
            "groups of computers). A disjoint-set union (union-find) structure handles each step in nearly O(1)."
        ),
        "input_format": "The first line contains n and q.\nEach of the next q lines contains two integers u and v: a cable between u and v.",
        "output_format": "Print q lines: the number of networks after each cable is added.",
        "constraints": "1 <= n <= 100000\n1 <= q <= 200000\n1 <= u, v <= n",
        "solve": solve_components_online,
        "tests": _t_comp_online(),
    },
    {
        "title": "Diameter of a Tree",
        "difficulty": "MEDIUM",
        "tags": "Trees,Breadth-First Search",
        "description": (
            "The diameter of a tree is the number of edges on the longest path between any two nodes. Given a "
            "tree with n nodes, compute its diameter. A classic approach: run a BFS from any node to find the "
            "farthest node x, then run a BFS from x; the largest distance found is the diameter. The tree may be "
            "a long chain, so an iterative traversal is recommended."
        ),
        "input_format": "The first line contains n.\nEach of the next n-1 lines contains two integers u and v, an edge of the tree.",
        "output_format": "Print the diameter of the tree.",
        "constraints": "1 <= n <= 100000\nThe edges always form a tree.",
        "solve": solve_diameter,
        "tests": _t_diameter(),
    },

    # ------------------------------------------------------------- HARD
    {
        "title": "Longest Increasing Subsequence",
        "difficulty": "HARD",
        "tags": "Dynamic Programming,Binary Search",
        "description": (
            "Given an array of n integers, find the length of the longest strictly increasing subsequence "
            "(elements taken in order, not necessarily adjacent, each strictly greater than the previous). "
            "With n up to 100000 the O(n^2) DP is too slow; use the O(n log n) patience-sorting technique "
            "with binary search.\n"
            "Example: 10 9 2 5 3 7 101 18 -> 2 3 7 101, length 4."
        ),
        "input_format": "The first line contains n.\nThe second line contains n integers.",
        "output_format": "Print the length of the longest strictly increasing subsequence.",
        "constraints": "1 <= n <= 100000\n-1000000000 <= a[i] <= 1000000000",
        "solve": solve_lis,
        "tests": _t_lis(),
    },
    {
        "title": "Matrix Chain Multiplication",
        "difficulty": "HARD",
        "tags": "Dynamic Programming",
        "description": (
            "You must multiply a chain of n matrices M1 x M2 x ... x Mn, where matrix Mi has dimensions "
            "p[i-1] x p[i]. Multiplying an a x b matrix by a b x c matrix costs a*b*c scalar multiplications. "
            "Matrix multiplication is associative, so you may choose any parenthesization. Find the minimum "
            "total number of scalar multiplications.\n"
            "Example: dimensions 10 30 5 60: (M1 M2) M3 costs 10*30*5 + 10*5*60 = 4500, the minimum."
        ),
        "input_format": "The first line contains n.\nThe second line contains n+1 integers p[0] .. p[n].",
        "output_format": "Print the minimum number of scalar multiplications (0 when n = 1).",
        "constraints": (
            "1 <= n <= 200\n1 <= p[i] <= 100\n"
            "The answer can exceed the 32-bit integer range; use a 64-bit integer type."
        ),
        "solve": solve_mcm,
        "tests": _t_mcm(),
    },
    {
        "title": "Egg Drop",
        "difficulty": "HARD",
        "tags": "Dynamic Programming,Math",
        "description": (
            "You have k identical eggs and a building with n floors. There is an unknown floor f (0 <= f <= n) "
            "such that an egg dropped from any floor above f breaks and from any floor at or below f does not. "
            "A broken egg cannot be reused; an unbroken one can. Find the minimum number of drops that "
            "guarantees determining f in the worst case. Hint: instead of asking how many drops n floors need, "
            "ask how many floors m drops with k eggs can cover.\n"
            "Example: with 2 eggs and 100 floors, 14 drops suffice."
        ),
        "input_format": "The first line contains T, the number of test cases.\nEach of the next T lines contains two integers k and n.",
        "output_format": "For each test case print the minimum number of drops on its own line.",
        "constraints": "1 <= T <= 1000\n1 <= k <= 100\n1 <= n <= 1000000000",
        "solve": solve_egg,
        "tests": _t_egg(),
    },
    {
        "title": "Shortest Paths With Negative Edges",
        "difficulty": "HARD",
        "tags": "Graphs,Shortest Path,Bellman-Ford",
        "description": (
            "A directed graph has n vertices and m edges whose weights may be negative. Compute the shortest "
            "distance from the source s to every vertex using the Bellman-Ford algorithm. If a negative-weight "
            "cycle can be reached from s, distances are not well defined: print NEGATIVE CYCLE instead. Negative "
            "cycles that cannot be reached from s do not matter. Print INF for unreachable vertices."
        ),
        "input_format": "The first line contains n, m and s.\nEach of the next m lines contains u, v and w: a directed edge from u to v with weight w.",
        "output_format": "Print the words NEGATIVE CYCLE, or n values separated by spaces: the distance to vertices 1..n, using INF for unreachable ones.",
        "constraints": (
            "1 <= n <= 500\n0 <= m <= 5000\n-1000000 <= w <= 1000000\n"
            "Distances can exceed the 32-bit integer range; use a 64-bit integer type."
        ),
        "solve": solve_bellman,
        "tests": _t_bellman(),
    },
    {
        "title": "Lowest Common Ancestor Queries",
        "difficulty": "HARD",
        "tags": "Trees,Binary Lifting",
        "description": (
            "A tree with n nodes is rooted at node 1. The lowest common ancestor (LCA) of nodes u and v is the "
            "deepest node that is an ancestor of both (a node is an ancestor of itself). Answer q LCA queries. "
            "The tree can be a long chain, so walking up one parent at a time per query is too slow; use binary "
            "lifting (or an Euler tour) and build it iteratively to avoid stack overflow."
        ),
        "input_format": (
            "The first line contains n.\nEach of the next n-1 lines contains two integers u and v, an edge of the tree.\n"
            "The next line contains q.\nEach of the next q lines contains two integers u and v."
        ),
        "output_format": "For each query print the LCA of u and v on its own line.",
        "constraints": "1 <= n <= 100000\n1 <= q <= 100000\nThe edges always form a tree.",
        "solve": solve_lca,
        "tests": _t_lca(),
    },
    {
        "title": "Counting Shortest Paths",
        "difficulty": "HARD",
        "tags": "Graphs,Shortest Path,Dynamic Programming",
        "description": (
            "An undirected graph has n vertices and m edges with positive weights. Find the length of the "
            "shortest path from vertex 1 to vertex n and the number of different shortest paths (two paths are "
            "different if their sequences of edges differ; parallel edges count as different edges). Print the "
            "count modulo 1000000007. If vertex n is unreachable, print -1."
        ),
        "input_format": "The first line contains n and m.\nEach of the next m lines contains u, v and w: an edge between u and v with weight w.",
        "output_format": "Print two integers: the shortest distance and the number of shortest paths modulo 1000000007; or print -1.",
        "constraints": (
            "1 <= n <= 100000\n0 <= m <= 200000\n1 <= w <= 1000000\nu != v\n"
            "The distance can exceed the 32-bit integer range; use a 64-bit integer type."
        ),
        "solve": solve_count_paths,
        "tests": _t_count_paths(),
    },
    {
        "title": "Strongly Connected Components",
        "difficulty": "HARD",
        "tags": "Graphs,Depth-First Search",
        "description": (
            "In a directed graph, a strongly connected component (SCC) is a maximal set of vertices in which "
            "every vertex can reach every other vertex. Every vertex belongs to exactly one SCC (possibly of "
            "size 1). Find the number of SCCs and their sizes. Use Kosaraju's or Tarjan's algorithm; the graph "
            "may contain long paths, so implement the DFS iteratively."
        ),
        "input_format": "The first line contains n and m.\nEach of the next m lines contains two integers u and v: a directed edge from u to v.",
        "output_format": "Print the number of SCCs on the first line.\nOn the second line print the sizes of all SCCs in non-increasing order, separated by spaces.",
        "constraints": "1 <= n <= 100000\n0 <= m <= 200000\n1 <= u, v <= n",
        "solve": solve_scc,
        "tests": _t_scc(),
    },
    {
        "title": "Maximum XOR of Two Numbers",
        "difficulty": "HARD",
        "tags": "Trie,Bit Manipulation",
        "description": (
            "Given n non-negative integers, find the maximum value of a[i] XOR a[j] over all pairs with i < j. "
            "Checking every pair is O(n^2) and too slow; insert the numbers' binary representations (30 bits, "
            "most significant first) into a binary trie and, for each number, greedily walk towards the "
            "opposite bit.\n"
            "Example: 3 10 5 25 2 8 -> 5 XOR 25 = 28."
        ),
        "input_format": "The first line contains n.\nThe second line contains n integers.",
        "output_format": "Print the maximum XOR of two different elements.",
        "constraints": "2 <= n <= 100000\n0 <= a[i] < 2^30 (1073741824)",
        "solve": solve_max_xor,
        "tests": _t_xor(),
    },
    {
        "title": "Sum of Distances in a Tree",
        "difficulty": "HARD",
        "tags": "Trees,Dynamic Programming",
        "description": (
            "A tree has n nodes numbered 1 to n. For every node u, compute the sum of the distances (number of "
            "edges) from u to all other nodes. Running a BFS from each node is O(n^2) and too slow; compute the "
            "answer for one root and then re-root: moving the root from a parent p to its child c changes the "
            "sum by n - 2 * size(c), where size(c) is the size of c's subtree. Use iterative traversals."
        ),
        "input_format": "The first line contains n.\nEach of the next n-1 lines contains two integers u and v, an edge of the tree.",
        "output_format": "Print n integers separated by spaces: the answer for nodes 1, 2, ..., n.",
        "constraints": (
            "1 <= n <= 100000\nThe edges always form a tree.\n"
            "Answers can exceed the 32-bit integer range; use a 64-bit integer type."
        ),
        "solve": solve_sum_dist,
        "tests": _t_sum_dist(),
    },
]
