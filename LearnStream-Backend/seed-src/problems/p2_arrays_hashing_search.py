"""
Problem pack 2: arrays, hashing, prefix sums, two pointers, sliding window,
sorting, binary search and matrices.
13 EASY, 13 MEDIUM, 7 HARD.
"""
import math
import random
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque


# ---------------------------------------------------------------- helpers
def _j(a):
    return " ".join(map(str, a))


def _arr(n, a, *extra):
    lines = [str(n), _j(a)]
    lines.extend(str(e) for e in extra)
    return "\n".join(lines) + "\n"


def _mat(rows):
    return "\n".join(_j(r) for r in rows)


def _rand_list(seed, n, lo, hi):
    r = random.Random(seed)
    return [r.randint(lo, hi) for _ in range(n)]


def _ints(s):
    return list(map(int, s.split()))


# ======================================================================
# EASY
# ======================================================================

# 1. Second Largest Distinct Element
def solve_second_largest(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    u = sorted(set(a))
    return "NONE" if len(u) < 2 else str(u[-2])


# 2. Rotate Array Right
def solve_rotate(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    k = d[1 + n] % n
    return _j(a[n - k:] + a[:n - k])


# 3. Move Zeroes to the End
def solve_move_zeroes(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    nz = [x for x in a if x != 0]
    return _j(nz + [0] * (n - len(nz)))


# 4. Remove Duplicates from Sorted Array
def solve_remove_dups(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    out = []
    for x in a:
        if not out or out[-1] != x:
            out.append(x)
    return str(len(out)) + "\n" + _j(out)


# 5. Find the Missing Number
def solve_missing(s):
    d = _ints(s)
    n = d[0]
    return str(n * (n + 1) // 2 - sum(d[1:1 + n]))


# 6. Majority Element
def solve_majority(s):
    d = _ints(s)
    n = d[0]
    cand, cnt = None, 0
    for x in d[1:1 + n]:
        if cnt == 0:
            cand = x
        cnt += 1 if x == cand else -1
    return str(cand)


# 7. Nearby Duplicate Within K
def solve_nearby_dup(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    k = d[1 + n]
    last = {}
    for i, x in enumerate(a):
        if x in last and i - last[x] <= k:
            return "YES"
        last[x] = i
    return "NO"


# 8. Best Time to Buy and Sell Stock
def solve_stock(s):
    d = _ints(s)
    n = d[0]
    best, lo = 0, None
    for p in d[1:1 + n]:
        if lo is None or p < lo:
            lo = p
        best = max(best, p - lo)
    return str(best)


# 9. Merge Two Sorted Arrays
def solve_merge(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    m = d[1 + n]
    b = d[2 + n:2 + n + m]
    i = j = 0
    out = []
    while i < n and j < m:
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return _j(out)


# 10. Range Sum Queries
def solve_range_sum(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    q = d[1 + n]
    p = [0]
    for x in a:
        p.append(p[-1] + x)
    out = []
    idx = 2 + n
    for _ in range(q):
        l, r = d[idx], d[idx + 1]; idx += 2
        out.append(p[r] - p[l - 1])
    return "\n".join(map(str, out))


# 11. First and Last Position in Sorted Array
def solve_first_last(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    q = d[1 + n]
    out = []
    for t in d[2 + n:2 + n + q]:
        lo = bisect_left(a, t)
        if lo == n or a[lo] != t:
            out.append("-1 -1")
        else:
            out.append(f"{lo} {bisect_right(a, t) - 1}")
    return "\n".join(out)


# 12. Spiral Matrix Traversal
def solve_spiral(s):
    d = _ints(s)
    r, c = d[0], d[1]
    m = [d[2 + i * c:2 + (i + 1) * c] for i in range(r)]
    top, bot, left, right = 0, r - 1, 0, c - 1
    out = []
    while top <= bot and left <= right:
        for j in range(left, right + 1):
            out.append(m[top][j])
        top += 1
        for i in range(top, bot + 1):
            out.append(m[i][right])
        right -= 1
        if top <= bot:
            for j in range(right, left - 1, -1):
                out.append(m[bot][j])
            bot -= 1
        if left <= right:
            for i in range(bot, top - 1, -1):
                out.append(m[i][left])
            left += 1
    return _j(out)


# 13. Rotate Matrix 90 Degrees Clockwise
def solve_rotate_matrix(s):
    d = _ints(s)
    n = d[0]
    m = [d[1 + i * n:1 + (i + 1) * n] for i in range(n)]
    rot = [[m[n - 1 - j][i] for j in range(n)] for i in range(n)]
    return _mat(rot)


# ======================================================================
# MEDIUM
# ======================================================================

# 14. Maximum Subarray Sum
def solve_kadane(s):
    d = _ints(s)
    n = d[0]
    best = cur = d[1]
    for x in d[2:1 + n]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return str(best)


# 15. Product of Array Except Self (mod)
MOD = 10 ** 9 + 7


def solve_product_except_self(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    pre = [1] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] * a[i] % MOD
    out = [0] * n
    suf = 1
    for i in range(n - 1, -1, -1):
        out[i] = pre[i] * suf % MOD
        suf = suf * a[i] % MOD
    return _j(out)


# 16. Count Subarrays with Sum K
def solve_subarray_sum_k(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    k = d[1 + n]
    seen = defaultdict(int)
    seen[0] = 1
    p = cnt = 0
    for x in a:
        p += x
        cnt += seen[p - k]
        seen[p] += 1
    return str(cnt)


# 17. Count Distinct Zero-Sum Triplets
def solve_3sum(s):
    d = _ints(s)
    n = d[0]
    a = sorted(d[1:1 + n])
    cnt = 0
    for i in range(n - 2):
        if i > 0 and a[i] == a[i - 1]:
            continue
        if a[i] > 0:
            break
        lo, hi = i + 1, n - 1
        while lo < hi:
            t = a[i] + a[lo] + a[hi]
            if t < 0:
                lo += 1
            elif t > 0:
                hi -= 1
            else:
                cnt += 1
                v = a[lo]
                while lo < hi and a[lo] == v:
                    lo += 1
                v = a[hi]
                while lo < hi and a[hi] == v:
                    hi -= 1
    return str(cnt)


# 18. Container With Most Water
def solve_container(s):
    d = _ints(s)
    n = d[0]
    h = d[1:1 + n]
    i, j, best = 0, n - 1, 0
    while i < j:
        best = max(best, min(h[i], h[j]) * (j - i))
        if h[i] < h[j]:
            i += 1
        else:
            j -= 1
    return str(best)


# 19. Longest Consecutive Sequence
def solve_longest_consecutive(s):
    d = _ints(s)
    n = d[0]
    st = set(d[1:1 + n])
    best = 0
    for x in st:
        if x - 1 not in st:
            y = x
            while y + 1 in st:
                y += 1
            best = max(best, y - x + 1)
    return str(best)


# 20. Kth Largest Element
def solve_kth_largest(s):
    d = _ints(s)
    n = d[0]
    a = sorted(d[1:1 + n], reverse=True)
    k = d[1 + n]
    return str(a[k - 1])


# 21. Group Anagrams
def solve_group_anagrams(s):
    t = s.split()
    n = int(t[0])
    c = Counter("".join(sorted(w)) for w in t[1:1 + n])
    sizes = sorted(c.values(), reverse=True)
    return str(len(sizes)) + "\n" + _j(sizes)


# 22. Search in Rotated Sorted Array
def solve_rotated_search(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    q = d[1 + n]
    pos = {x: i for i, x in enumerate(a)}
    return "\n".join(str(pos.get(t, -1)) for t in d[2 + n:2 + n + q])


# 23. Integer Square Root
def solve_isqrt(s):
    d = _ints(s)
    t = d[0]
    return "\n".join(str(math.isqrt(x)) for x in d[1:1 + t])


# 24. Minimum Ship Capacity
def solve_ship(s):
    d = _ints(s)
    n = d[0]
    w = d[1:1 + n]
    days = d[1 + n]

    def ok(cap):
        used, cur = 1, 0
        for x in w:
            if cur + x > cap:
                used += 1
                cur = 0
            cur += x
        return used <= days

    lo, hi = max(w), sum(w)
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return str(lo)


# 25. Set Matrix Zeroes
def solve_set_zeroes(s):
    d = _ints(s)
    r, c = d[0], d[1]
    m = [d[2 + i * c:2 + (i + 1) * c] for i in range(r)]
    zr = {i for i in range(r) if 0 in m[i]}
    zc = {j for j in range(c) if any(m[i][j] == 0 for i in range(r))}
    out = [[0 if (i in zr or j in zc) else m[i][j] for j in range(c)] for i in range(r)]
    return _mat(out)


# 26. Submatrix Sum Queries
def solve_2d_prefix(s):
    d = _ints(s)
    r, c = d[0], d[1]
    P = [[0] * (c + 1) for _ in range(r + 1)]
    for i in range(r):
        row = d[2 + i * c:2 + (i + 1) * c]
        acc = 0
        for j in range(c):
            acc += row[j]
            P[i + 1][j + 1] = P[i][j + 1] + acc
    idx = 2 + r * c
    q = d[idx]; idx += 1
    out = []
    for _ in range(q):
        r1, c1, r2, c2 = d[idx:idx + 4]; idx += 4
        out.append(P[r2][c2] - P[r1 - 1][c2] - P[r2][c1 - 1] + P[r1 - 1][c1 - 1])
    return "\n".join(map(str, out))


# ======================================================================
# HARD
# ======================================================================

def _fmt_half(doubled):
    sign = "-" if doubled < 0 else ""
    a = abs(doubled)
    return f"{sign}{a // 2}.{5 if a % 2 else 0}"


# 27. Median of Two Sorted Arrays
def solve_median(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    m = d[1 + n]
    b = d[2 + n:2 + n + m]
    c = sorted(a + b)
    t = n + m
    if t % 2:
        dbl = 2 * c[t // 2]
    else:
        dbl = c[t // 2 - 1] + c[t // 2]
    return _fmt_half(dbl)


# 28. Sliding Window Maximum
def solve_window_max(s):
    d = _ints(s)
    n, k = d[0], d[1]
    a = d[2:2 + n]
    dq = deque()
    out = []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(a[dq[0]])
    return _j(out)


# 29. Minimum Window Substring
def solve_min_window(s):
    lines = s.split()
    src, t = lines[0], lines[1]
    need = Counter(t)
    missing = len(t)
    left = 0
    best = None
    for right, ch in enumerate(src):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while need[src[left]] < 0:
                need[src[left]] += 1
                left += 1
            if best is None or right - left + 1 < best[1] - best[0]:
                best = (left, right + 1)
            need[src[left]] += 1
            missing += 1
            left += 1
    return "-1" if best is None else src[best[0]:best[1]]


# 30. Trapping Rain Water
def solve_trap(s):
    d = _ints(s)
    n = d[0]
    h = d[1:1 + n]
    i, j = 0, n - 1
    lm = rm = 0
    total = 0
    while i <= j:
        if lm <= rm:
            lm = max(lm, h[i])
            total += lm - h[i]
            i += 1
        else:
            rm = max(rm, h[j])
            total += rm - h[j]
            j -= 1
    return str(total)


# 31. First Missing Positive
def solve_first_missing_positive(s):
    d = _ints(s)
    n = d[0]
    st = set(d[1:1 + n])
    x = 1
    while x in st:
        x += 1
    return str(x)


# 32. Count Subarrays with Sum in Range
def solve_range_sum_count(s):
    d = _ints(s)
    n = d[0]
    a = d[1:1 + n]
    lo, hi = d[1 + n], d[2 + n]
    P = [0]
    for x in a:
        P.append(P[-1] + x)
    vals = sorted(set(P))
    m = len(vals)
    tree = [0] * (m + 1)

    def add(i):
        i += 1
        while i <= m:
            tree[i] += 1
            i += i & -i

    def pref(i):  # count of inserted with compressed index < i
        r = 0
        while i > 0:
            r += tree[i]
            i -= i & -i
        return r

    cnt = 0
    for p in P:
        L = bisect_left(vals, p - hi)
        R = bisect_right(vals, p - lo)
        if R > L:
            cnt += pref(R) - pref(L)
        add(bisect_left(vals, p))
    return str(cnt)


# 33. Subarrays with Exactly K Distinct
def solve_exact_k_distinct(s):
    d = _ints(s)
    n, k = d[0], d[1]
    a = d[2:2 + n]

    def at_most(k):
        if k <= 0:
            return 0
        cnt = defaultdict(int)
        left = distinct = total = 0
        for right, x in enumerate(a):
            if cnt[x] == 0:
                distinct += 1
            cnt[x] += 1
            while distinct > k:
                y = a[left]
                cnt[y] -= 1
                if cnt[y] == 0:
                    distinct -= 1
                left += 1
            total += right - left + 1
        return total

    return str(at_most(k) - at_most(k - 1))


# ======================================================================
# Test data generators
# ======================================================================

def _big(seed, n, lo, hi, *extra):
    return _arr(n, _rand_list(seed, n, lo, hi), *extra)


def _sorted_big(seed, n, lo, hi, *extra):
    return _arr(n, sorted(_rand_list(seed, n, lo, hi)), *extra)


def _missing_test(seed, n):
    r = random.Random(seed)
    a = list(range(n + 1))
    a.remove(r.randint(0, n))
    r.shuffle(a)
    return _arr(n, a)


def _majority_test(seed, n, maj):
    r = random.Random(seed)
    cnt = n // 2 + 1
    a = [maj] * cnt + [r.randint(-10 ** 9, 10 ** 9) for _ in range(n - cnt)]
    r.shuffle(a)
    return _arr(n, a)


def _range_query_test(seed, n, q):
    r = random.Random(seed)
    a = [r.randint(-1000, 1000) for _ in range(n)]
    lines = [str(n), _j(a), str(q)]
    for _ in range(q):
        l = r.randint(1, n); rr = r.randint(l, n)
        lines.append(f"{l} {rr}")
    return "\n".join(lines) + "\n"


def _first_last_test(seed, n, q):
    r = random.Random(seed)
    a = sorted(r.randint(0, 5000) for _ in range(n))
    qs = [r.randint(-5, 5005) for _ in range(q)]
    return "\n".join([str(n), _j(a), str(q), _j(qs)]) + "\n"


def _matrix_test(seed, r, c, lo, hi, zero_p=0.0):
    rnd = random.Random(seed)
    rows = []
    for _ in range(r):
        row = []
        for _ in range(c):
            if zero_p and rnd.random() < zero_p:
                row.append(0)
            else:
                row.append(rnd.randint(lo, hi))
        rows.append(row)
    return rows


def _rmat(r, c, rows):
    return f"{r} {c}\n" + _mat(rows) + "\n"


def _square(n, rows):
    return f"{n}\n" + _mat(rows) + "\n"


def _rotated_test(seed, n, q):
    r = random.Random(seed)
    a = sorted(r.sample(range(-10 ** 6, 10 ** 6), n))
    k = r.randint(0, n - 1)
    a = a[k:] + a[:k]
    qs = [r.choice(a) if r.random() < 0.6 else r.randint(-10 ** 6, 10 ** 6) for _ in range(q)]
    return "\n".join([str(n), _j(a), str(q), _j(qs)]) + "\n"


def _consecutive_test(seed, n):
    r = random.Random(seed)
    a = []
    while len(a) < n:
        start = r.randint(-10 ** 9, 10 ** 9 - 1000)
        ln = r.randint(1, 300)
        a.extend(range(start, start + ln))
    a = a[:n]
    a += [r.choice(a) for _ in range(n // 10)]
    r.shuffle(a)
    return _arr(len(a), a)


def _anagram_test(seed, n):
    r = random.Random(seed)
    words = [''.join(r.choice("abcde") for _ in range(r.randint(1, 5))) for _ in range(n)]
    return str(n) + "\n" + " ".join(words) + "\n"


def _isqrt_test(seed, t):
    r = random.Random(seed)
    xs = []
    for _ in range(t):
        kind = r.random()
        if kind < 0.3:
            b = r.randint(1, 10 ** 9)
            xs.append(b * b + r.choice([-1, 0, 1]))
        elif kind < 0.6:
            xs.append(r.randint(0, 10 ** 18))
        else:
            xs.append(r.randint(0, 10 ** r.randint(1, 18)))
    xs.append(10 ** 18)
    xs.append(999999999999999999)
    return str(len(xs)) + "\n" + "\n".join(map(str, xs)) + "\n"


def _prefix2d_test(seed, r, c, q):
    rnd = random.Random(seed)
    rows = _matrix_test(seed, r, c, -1000, 1000)
    lines = [f"{r} {c}", _mat(rows), str(q)]
    for _ in range(q):
        r1 = rnd.randint(1, r); r2 = rnd.randint(r1, r)
        c1 = rnd.randint(1, c); c2 = rnd.randint(c1, c)
        lines.append(f"{r1} {c1} {r2} {c2}")
    return "\n".join(lines) + "\n"


def _two_sorted(seed, n, m, lo, hi):
    r = random.Random(seed)
    a = sorted(r.randint(lo, hi) for _ in range(n))
    b = sorted(r.randint(lo, hi) for _ in range(m))
    return "\n".join([str(n), _j(a), str(m), _j(b)]) + "\n"


def _window_test(seed, n, k, lo, hi):
    return f"{n} {k}\n" + _j(_rand_list(seed, n, lo, hi)) + "\n"


def _min_window_big(seed, n, tl):
    r = random.Random(seed)
    src = ''.join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n))
    t = ''.join(r.choice("abcdefghijklmnopqrstuvwxyzABC") for _ in range(tl))
    # t is satisfiable: its uppercase letters are planted near one center
    center = r.randrange(2000, n - 2000)
    src = list(src)
    for ch in t:
        if ch.isupper():
            src[center + r.randrange(-1500, 1500)] = ch
    return ''.join(src) + "\n" + t + "\n"


def _terrain(seed, n):
    r = random.Random(seed)
    h, cur = [], 5000
    for _ in range(n):
        cur = max(0, min(9999, cur + r.randint(-300, 300)))
        h.append(cur)
    return _arr(n, h)


def _fmp_test(seed, n):
    r = random.Random(seed)
    a = list(range(1, n // 2))
    a += [r.randint(-10 ** 9, 10 ** 9) for _ in range(n - len(a))]
    a.remove(n // 3)
    a.append(n // 3 + 1)
    r.shuffle(a)
    return _arr(len(a), a)


# ======================================================================
# PROBLEMS
# ======================================================================

PROBLEMS = [
    # ------------------------------------------------------------ EASY
    {
        "title": "Second Largest Distinct Element",
        "difficulty": "EASY",
        "tags": "Arrays",
        "description": (
            "Given an array of integers, find the second largest distinct value in it. "
            "Duplicates count only once, so in [5, 5, 3] the largest value is 5 and the second largest distinct value is 3. "
            "If the array has fewer than two distinct values, print NONE."
        ),
        "input_format": "The first line contains an integer n.\nThe second line contains n space-separated integers.",
        "output_format": "Print the second largest distinct value, or the word NONE if it does not exist.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9",
        "solve": solve_second_largest,
        "tests": [
            "6\n12 35 1 10 34 1\n",
            "4\n7 7 7 7\n",
            "1\n42\n",
            "5\n-3 -1 -7 -1 -2\n",
            "3\n10 5 10\n",
            "2\n-1000000000 1000000000\n",
            _big(201, 15000, -10 ** 9, 10 ** 9),
        ],
    },
    {
        "title": "Rotate Array to the Right",
        "difficulty": "EASY",
        "tags": "Arrays",
        "description": (
            "Rotate an array to the right by k steps: each step moves the last element to the front. "
            "For example, rotating [1, 2, 3, 4, 5] right by 2 gives [4, 5, 1, 2, 3]. "
            "Note that k can be much larger than n."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.\nThe third line contains k.",
        "output_format": "Print the rotated array as n space-separated integers on one line.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9\n0 <= k <= 10^9",
        "solve": solve_rotate,
        "tests": [
            "5\n1 2 3 4 5\n2\n",
            "3\n-1 -100 3\n4\n",
            "1\n9\n1000000000\n",
            "4\n1 2 3 4\n0\n",
            "4\n1 2 3 4\n4\n",
            "6\n5 5 1 5 2 2\n999999999\n",
            _big(202, 15000, -10 ** 9, 10 ** 9, 123456789),
        ],
    },
    {
        "title": "Move Zeroes to the End",
        "difficulty": "EASY",
        "tags": "Arrays,Two Pointers",
        "description": (
            "Move all zeroes in the array to the end while keeping the relative order of the non-zero elements. "
            "For example, [0, 1, 0, 3, 12] becomes [1, 3, 12, 0, 0]. "
            "Try to do it in place with a single pass."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.",
        "output_format": "Print the resulting array as n space-separated integers on one line.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9",
        "solve": solve_move_zeroes,
        "tests": [
            "5\n0 1 0 3 12\n",
            "6\n4 -2 0 0 7 0\n",
            "1\n0\n",
            "1\n5\n",
            "4\n0 0 0 0\n",
            "5\n1 2 3 4 5\n",
            _arr(15000, [x if i % 3 else 0 for i, x in enumerate(_rand_list(203, 15000, -10 ** 9, 10 ** 9))]),
        ],
    },
    {
        "title": "Remove Duplicates from Sorted Array",
        "difficulty": "EASY",
        "tags": "Arrays,Two Pointers",
        "description": (
            "You are given an array sorted in non-decreasing order. Remove the duplicates so that each value appears only once, "
            "keeping the order. Print how many unique values remain, followed by the unique values themselves. "
            "For example, [1, 1, 2, 3, 3] becomes [1, 2, 3], so the answer is 3."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers in non-decreasing order.",
        "output_format": "On the first line print the number of unique values m.\nOn the second line print the m unique values, space-separated, in increasing order.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9",
        "solve": solve_remove_dups,
        "tests": [
            "5\n1 1 2 3 3\n",
            "10\n0 0 1 1 1 2 2 3 3 4\n",
            "1\n-5\n",
            "4\n8 8 8 8\n",
            "5\n-3 -2 -1 0 1\n",
            "6\n-7 -7 -7 2 2 9\n",
            _sorted_big(204, 20000, -5000, 5000),
        ],
    },
    {
        "title": "Find the Missing Number",
        "difficulty": "EASY",
        "tags": "Arrays,Math,Hashing",
        "description": (
            "An array contains n distinct numbers taken from the range 0 to n (inclusive), so exactly one number in that range is missing. "
            "Find the missing number. For example, with n = 3 and array [3, 0, 1], the missing number is 2."
        ),
        "input_format": "The first line contains n.\nThe second line contains n distinct space-separated integers, each between 0 and n.",
        "output_format": "Print the missing number.",
        "constraints": "1 <= n <= 10^5\n0 <= a[i] <= n, all a[i] distinct",
        "solve": solve_missing,
        "tests": [
            "3\n3 0 1\n",
            "9\n9 6 4 2 3 5 7 0 1\n",
            "1\n0\n",
            "1\n1\n",
            "5\n0 1 2 3 4\n",
            "5\n5 4 3 2 1\n",
            _missing_test(205, 30000),
        ],
    },
    {
        "title": "Majority Element",
        "difficulty": "EASY",
        "tags": "Arrays,Hashing",
        "description": (
            "Find the element that appears more than n/2 times in the array (strictly more than half). "
            "Such an element is guaranteed to exist. "
            "For example, in [2, 2, 1, 1, 1, 2, 2] the majority element is 2. "
            "Can you solve it in O(n) time and O(1) extra space?"
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.",
        "output_format": "Print the majority element.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9\nA majority element always exists.",
        "solve": solve_majority,
        "tests": [
            "7\n2 2 1 1 1 2 2\n",
            "3\n3 2 3\n",
            "1\n-8\n",
            "5\n-1 -1 -1 -1 -1\n",
            "6\n4 9 4 9 4 4\n",
            "5\n1 7 7 2 7\n",
            _majority_test(206, 15001, -123456789),
        ],
    },
    {
        "title": "Nearby Duplicate Within K",
        "difficulty": "EASY",
        "tags": "Arrays,Hashing,Sliding Window",
        "description": (
            "Determine whether there are two different indices i and j such that a[i] == a[j] and |i - j| <= k. "
            "For example, in [1, 2, 3, 1] with k = 3 the two 1s are 3 positions apart, so the answer is YES; with k = 2 it would be NO."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.\nThe third line contains k.",
        "output_format": "Print YES if such a pair exists, otherwise print NO.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9\n0 <= k <= 10^5",
        "solve": solve_nearby_dup,
        "tests": [
            "4\n1 2 3 1\n3\n",
            "6\n1 2 3 1 2 3\n2\n",
            "1\n5\n1\n",
            "3\n7 7 7\n0\n",
            "2\n-4 -4\n1\n",
            "5\n1 2 3 4 5\n100000\n",
            _arr(20000, list(range(1, 20001)), 100000),
            _arr(20000, [i % 5000 for i in range(20000)], 5000),
            _arr(20000, [i % 5000 for i in range(20000)], 4999),
        ],
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "difficulty": "EASY",
        "tags": "Arrays,Greedy",
        "description": (
            "prices[i] is the price of a stock on day i. You may buy one share on one day and sell it on a later day. "
            "Find the maximum profit you can make. If no profit is possible, print 0. "
            "For example, for prices [7, 1, 5, 3, 6, 4] the best is to buy at 1 and sell at 6 for a profit of 5."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers, the prices.",
        "output_format": "Print the maximum profit.",
        "constraints": "1 <= n <= 10^5\n0 <= prices[i] <= 10^9",
        "solve": solve_stock,
        "tests": [
            "6\n7 1 5 3 6 4\n",
            "5\n7 6 4 3 1\n",
            "1\n100\n",
            "4\n5 5 5 5\n",
            "2\n0 1000000000\n",
            "8\n3 8 1 2 9 0 4 6\n",
            _big(208, 20000, 0, 10 ** 9),
        ],
    },
    {
        "title": "Merge Two Sorted Arrays",
        "difficulty": "EASY",
        "tags": "Arrays,Two Pointers,Sorting",
        "description": (
            "You are given two arrays, each sorted in non-decreasing order. Merge them into a single sorted array. "
            "For example, merging [1, 3, 5] and [2, 3, 6] gives [1, 2, 3, 3, 5, 6]. "
            "Aim for O(n + m) time using two pointers."
        ),
        "input_format": "The first line contains n.\nThe second line contains n sorted integers.\nThe third line contains m.\nThe fourth line contains m sorted integers.",
        "output_format": "Print the n + m merged values, space-separated, on one line.",
        "constraints": "1 <= n, m <= 10^5\n-10^9 <= values <= 10^9",
        "solve": solve_merge,
        "tests": [
            "3\n1 3 5\n3\n2 3 6\n",
            "2\n-5 10\n4\n-7 -5 0 20\n",
            "1\n1\n1\n1\n",
            "3\n1 2 3\n2\n4 5\n",
            "2\n8 9\n3\n1 2 3\n",
            "4\n0 0 0 0\n1\n0\n",
            _two_sorted(209, 9000, 8000, -10 ** 9, 10 ** 9),
        ],
    },
    {
        "title": "Range Sum Queries",
        "difficulty": "EASY",
        "tags": "Arrays,Prefix Sum",
        "description": (
            "Given an array and q queries, each query asks for the sum of the elements from position l to position r (1-indexed, inclusive). "
            "For example, for [3, -1, 4, 1, 5] the query (2, 4) gives -1 + 4 + 1 = 4. "
            "There are many queries, so precompute prefix sums to answer each one in O(1)."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.\nThe third line contains q.\nEach of the next q lines contains two integers l and r.",
        "output_format": "For each query, print the sum on its own line.",
        "constraints": "1 <= n, q <= 10^5\n-10^9 <= a[i] <= 10^9\n1 <= l <= r <= n\nSums may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_range_sum,
        "tests": [
            "5\n3 -1 4 1 5\n3\n2 4\n1 5\n3 3\n",
            "4\n1000000000 1000000000 1000000000 1000000000\n2\n1 4\n2 3\n",
            "1\n-7\n1\n1 1\n",
            "6\n0 0 0 0 0 0\n2\n1 6\n4 5\n",
            "5\n-5 -4 -3 -2 -1\n4\n1 1\n1 5\n2 4\n5 5\n",
            _range_query_test(210, 20000, 10000),
            _range_query_test(211, 300, 300),
        ],
    },
    {
        "title": "First and Last Position in Sorted Array",
        "difficulty": "EASY",
        "tags": "Arrays,Binary Search",
        "description": (
            "Given an array sorted in non-decreasing order and several target values, find the first and last index (0-indexed) of each target. "
            "If the target is not present, print -1 -1. "
            "For example, in [5, 7, 7, 8, 8, 10] the target 8 occupies indices 3 to 4. Use binary search to answer each query in O(log n)."
        ),
        "input_format": "The first line contains n.\nThe second line contains n sorted integers.\nThe third line contains q.\nThe fourth line contains q space-separated targets.",
        "output_format": "For each target print two integers, the first and last index, separated by a space, on its own line.",
        "constraints": "1 <= n, q <= 10^5\n-10^9 <= values <= 10^9",
        "solve": solve_first_last,
        "tests": [
            "6\n5 7 7 8 8 10\n3\n8 6 5\n",
            "5\n2 2 2 2 2\n2\n2 3\n",
            "1\n1\n2\n1 0\n",
            "7\n-3 -3 -1 0 0 0 9\n4\n-3 0 9 10\n",
            "4\n1 2 3 4\n4\n4 3 2 1\n",
            _first_last_test(212, 20000, 15000),
        ],
    },
    {
        "title": "Spiral Matrix Traversal",
        "difficulty": "EASY",
        "tags": "Matrix,Simulation",
        "description": (
            "Print all elements of an r x c matrix in spiral order: go right along the top row, down the right column, left along the bottom row, "
            "up the left column, and repeat inward. "
            "For the matrix with rows [1 2 3], [4 5 6], [7 8 9], the spiral order is 1 2 3 6 9 8 7 4 5."
        ),
        "input_format": "The first line contains r and c.\nEach of the next r lines contains c space-separated integers.",
        "output_format": "Print all r * c elements in spiral order, space-separated, on one line.",
        "constraints": "1 <= r, c <= 300\n-10^9 <= values <= 10^9",
        "solve": solve_spiral,
        "tests": [
            "3 3\n1 2 3\n4 5 6\n7 8 9\n",
            "3 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n",
            "1 1\n7\n",
            "1 5\n1 2 3 4 5\n",
            "4 1\n1\n2\n3\n4\n",
            "2 3\n-1 -2 -3\n-4 -5 -6\n",
            "4 2\n1 2\n3 4\n5 6\n7 8\n",
            _rmat(200, 180, _matrix_test(213, 200, 180, 0, 999)),
        ],
    },
    {
        "title": "Rotate Matrix 90 Degrees Clockwise",
        "difficulty": "EASY",
        "tags": "Matrix",
        "description": (
            "Rotate an n x n matrix by 90 degrees clockwise. "
            "For example, rows [1 2], [3 4] become rows [3 1], [4 2]. "
            "A neat in-place trick is to transpose the matrix and then reverse every row."
        ),
        "input_format": "The first line contains n.\nEach of the next n lines contains n space-separated integers.",
        "output_format": "Print the rotated matrix: n lines, each with n space-separated integers.",
        "constraints": "1 <= n <= 300\n-10^9 <= values <= 10^9",
        "solve": solve_rotate_matrix,
        "tests": [
            "3\n1 2 3\n4 5 6\n7 8 9\n",
            "2\n1 2\n3 4\n",
            "1\n-5\n",
            "4\n5 1 9 11\n2 4 8 10\n13 3 6 7\n15 14 12 16\n",
            "3\n0 0 0\n0 0 0\n0 0 0\n",
            "2\n-1000000000 1000000000\n7 -7\n",
            _square(150, _matrix_test(214, 150, 150, -9999, 9999)),
        ],
    },

    # ------------------------------------------------------------ MEDIUM
    {
        "title": "Maximum Subarray Sum",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Dynamic Programming,Kadane",
        "description": (
            "Find the largest possible sum of a non-empty contiguous subarray. "
            "For example, in [-2, 1, -3, 4, -1, 2, 1, -5, 4] the subarray [4, -1, 2, 1] has the largest sum, 6. "
            "If every element is negative, the answer is the largest single element. Aim for O(n) using Kadane's algorithm."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.",
        "output_format": "Print the maximum subarray sum.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9\nThe answer may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_kadane,
        "tests": [
            "9\n-2 1 -3 4 -1 2 1 -5 4\n",
            "5\n-8 -3 -6 -2 -5\n",
            "1\n-1\n",
            "1\n10\n",
            "5\n1000000000 1000000000 -1 1000000000 1000000000\n",
            "6\n0 0 0 0 0 0\n",
            "7\n2 -1 2 -1 2 -10 5\n",
            _big(215, 15000, -10 ** 9, 10 ** 9),
        ],
    },
    {
        "title": "Product of Array Except Self",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Prefix Sum",
        "description": (
            "For every index i, compute the product of all array elements except a[i], modulo 1000000007. "
            "For example, for [1, 2, 3, 4] the answer is [24, 12, 8, 6]. "
            "Do it without division, using prefix and suffix products; note that the array may contain zeros."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated non-negative integers.",
        "output_format": "Print n space-separated integers: the i-th is the product of all elements except a[i], taken modulo 1000000007.",
        "constraints": "2 <= n <= 10^5\n0 <= a[i] <= 10^9\nIntermediate products overflow 64-bit integers, so reduce modulo 1000000007 after every multiplication.",
        "solve": solve_product_except_self,
        "tests": [
            "4\n1 2 3 4\n",
            "5\n2 1 0 3 4\n",
            "2\n5 7\n",
            "3\n0 0 9\n",
            "4\n1000000000 1000000000 1000000000 1000000000\n",
            "5\n1 1 1 1 1\n",
            _big(216, 15000, 0, 10 ** 9),
        ],
    },
    {
        "title": "Count Subarrays with Sum K",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Hashing,Prefix Sum",
        "description": (
            "Count how many contiguous subarrays have a sum exactly equal to k. The array may contain negative numbers and zeros. "
            "For example, in [1, 1, 1] with k = 2 there are 2 such subarrays. "
            "A hash map of prefix-sum frequencies gives an O(n) solution."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.\nThe third line contains k.",
        "output_format": "Print the number of subarrays whose sum equals k.",
        "constraints": "1 <= n <= 10^5\n-1000 <= a[i] <= 1000\n-10^9 <= k <= 10^9\nThe count may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_subarray_sum_k,
        "tests": [
            "3\n1 1 1\n2\n",
            "6\n3 4 7 2 -3 1\n7\n",
            "1\n5\n5\n",
            "1\n5\n-5\n",
            "5\n0 0 0 0 0\n0\n",
            "6\n1 -1 1 -1 1 -1\n0\n",
            _big(217, 50000, -3, 3, 2),
            _arr(40000, [0] * 40000, 0),
        ],
    },
    {
        "title": "Count Distinct Zero-Sum Triplets",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Two Pointers,Sorting",
        "description": (
            "Count the number of distinct triplets of values (x, y, z) with x <= y <= z such that x + y + z = 0 and the three values "
            "can be taken from three different positions in the array. Triplets with the same three values count once. "
            "For example, [-1, 0, 1, 2, -1, -4] has two such triplets: (-1, -1, 2) and (-1, 0, 1). "
            "Sort the array and use two pointers for an O(n^2) solution."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.",
        "output_format": "Print the number of distinct zero-sum triplets.",
        "constraints": "1 <= n <= 3000\n-10^5 <= a[i] <= 10^5",
        "solve": solve_3sum,
        "tests": [
            "6\n-1 0 1 2 -1 -4\n",
            "5\n0 0 0 0 0\n",
            "1\n0\n",
            "2\n-1 1\n",
            "3\n1 2 3\n",
            "8\n-2 -2 0 0 2 2 4 -4\n",
            "9\n-5 1 4 -3 2 1 -1 0 3\n",
            _big(218, 2500, -2000, 2000),
        ],
    },
    {
        "title": "Container With Most Water",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Two Pointers,Greedy",
        "description": (
            "You are given n vertical lines; line i is at x = i and has height h[i]. Choose two lines that, together with the x-axis, "
            "form a container holding the most water. The amount is min(h[i], h[j]) * (j - i). "
            "For heights [1, 8, 6, 2, 5, 4, 8, 3, 7] the best container holds 49 units. Use two pointers moving inward."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated heights.",
        "output_format": "Print the maximum amount of water.",
        "constraints": "2 <= n <= 10^5\n0 <= h[i] <= 10^9\nThe answer may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_container,
        "tests": [
            "9\n1 8 6 2 5 4 8 3 7\n",
            "2\n1 1\n",
            "2\n0 1000000000\n",
            "5\n4 4 4 4 4\n",
            "6\n1 2 3 4 5 6\n",
            "4\n1000000000 1 1 1000000000\n",
            _big(219, 50000, 1, 9999),
        ],
    },
    {
        "title": "Longest Consecutive Sequence",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Hashing",
        "description": (
            "Find the length of the longest run of consecutive integer values that all appear in the array (order in the array does not matter). "
            "For example, [100, 4, 200, 1, 3, 2] contains 1, 2, 3, 4, so the answer is 4. Duplicates count once. "
            "Aim for O(n) with a hash set."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.",
        "output_format": "Print the length of the longest consecutive sequence.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9",
        "solve": solve_longest_consecutive,
        "tests": [
            "6\n100 4 200 1 3 2\n",
            "10\n0 3 7 2 5 8 4 6 0 1\n",
            "1\n-7\n",
            "4\n5 5 5 5\n",
            "5\n-2 -1 0 1 2\n",
            "6\n10 30 20 40 50 60\n",
            _consecutive_test(220, 15000),
            _arr(30000, list(range(30000, 0, -1))),
        ],
    },
    {
        "title": "Kth Largest Element",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Sorting",
        "description": (
            "Find the k-th largest element in the array. This is the k-th element in sorted descending order, so duplicates are counted "
            "separately. For example, in [3, 2, 1, 5, 6, 4] the 2nd largest is 5, and in [3, 2, 3, 1, 2, 4, 5, 5, 6] the 4th largest is 4."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.\nThe third line contains k.",
        "output_format": "Print the k-th largest element.",
        "constraints": "1 <= k <= n <= 10^5\n-10^9 <= a[i] <= 10^9",
        "solve": solve_kth_largest,
        "tests": [
            "6\n3 2 1 5 6 4\n2\n",
            "9\n3 2 3 1 2 4 5 5 6\n4\n",
            "1\n-1\n1\n",
            "5\n7 7 7 7 7\n3\n",
            "5\n-5 -1 -3 -2 -4\n5\n",
            "4\n1 2 3 4\n1\n",
            _big(221, 15000, -10 ** 9, 10 ** 9, 7777),
        ],
    },
    {
        "title": "Group Anagrams",
        "difficulty": "MEDIUM",
        "tags": "Hashing,Strings,Sorting",
        "description": (
            "Two words are anagrams if one can be rearranged to form the other. Group the given words so that each group contains words "
            "that are anagrams of each other (identical words belong to the same group). "
            "Print the number of groups and the group sizes in non-increasing order. "
            "For example, eat tea tan ate nat bat forms groups {eat, tea, ate}, {tan, nat}, {bat}, giving 3 groups of sizes 3 2 1."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated words of lowercase English letters.",
        "output_format": "On the first line print the number of groups g.\nOn the second line print the g group sizes, space-separated, in non-increasing order.",
        "constraints": "1 <= n <= 10^5\n1 <= length of each word <= 10\nTotal length of all words <= 2 * 10^5",
        "solve": solve_group_anagrams,
        "tests": [
            "6\neat tea tan ate nat bat\n",
            "5\nlisten silent enlist google gogole\n",
            "1\na\n",
            "4\nabc abc abc abc\n",
            "5\nab ba abc cab xyz\n",
            "6\na b c d e f\n",
            _anagram_test(222, 30000),
        ],
    },
    {
        "title": "Search in Rotated Sorted Array",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Binary Search",
        "description": (
            "A sorted array of distinct integers has been rotated at an unknown pivot, e.g. [0, 1, 2, 4, 5, 6, 7] might become [4, 5, 6, 7, 0, 1, 2]. "
            "For each query value, print its index (0-indexed) in the rotated array, or -1 if it is not present. "
            "Each query should take O(log n) time using a modified binary search."
        ),
        "input_format": "The first line contains n.\nThe second line contains n distinct integers (a rotated sorted array).\nThe third line contains q.\nThe fourth line contains q space-separated query values.",
        "output_format": "For each query, print the index or -1 on its own line.",
        "constraints": "1 <= n, q <= 10^5\n-10^9 <= values <= 10^9\nAll array values are distinct.",
        "solve": solve_rotated_search,
        "tests": [
            "7\n4 5 6 7 0 1 2\n3\n0 3 4\n",
            "5\n30 40 50 10 20\n4\n10 20 50 35\n",
            "1\n1\n2\n1 0\n",
            "5\n1 2 3 4 5\n3\n1 5 6\n",
            "4\n-1 -5 -4 -3\n4\n-1 -5 -3 -2\n",
            "2\n3 1\n3\n1 3 2\n",
            _rotated_test(223, 15000, 10000),
        ],
    },
    {
        "title": "Integer Square Root",
        "difficulty": "MEDIUM",
        "tags": "Binary Search,Math",
        "description": (
            "For each given non-negative integer N, print floor(sqrt(N)), the largest integer x with x * x <= N. "
            "For example, the answer for 8 is 2 and for 16 is 4. "
            "N can be as large as 10^18, where floating-point square roots can be off by one, so use binary search on integers (careful with overflow when squaring)."
        ),
        "input_format": "The first line contains t, the number of values.\nEach of the next t lines contains one integer N.",
        "output_format": "For each N print floor(sqrt(N)) on its own line.",
        "constraints": "1 <= t <= 10^4\n0 <= N <= 10^18\nN does not fit in 32 bits; use 64-bit integers (BigInt in JavaScript).",
        "solve": solve_isqrt,
        "tests": [
            "3\n8\n16\n1\n",
            "4\n0\n2\n99\n100\n",
            "1\n1000000000000000000\n",
            "3\n999999999999999999\n999999998000000001\n999999998000000000\n",
            "5\n3\n4\n5\n2147395600\n2147483647\n",
            "2\n123456789012345678\n10\n",
            _isqrt_test(224, 1500),
        ],
    },
    {
        "title": "Minimum Ship Capacity",
        "difficulty": "MEDIUM",
        "tags": "Arrays,Binary Search",
        "description": (
            "Packages with weights w[0..n-1] must be shipped in the given order within D days. Each day the ship is loaded with "
            "consecutive packages as long as their total weight does not exceed its capacity. Find the minimum capacity that ships everything within D days. "
            "For weights 1..10 and D = 5 the answer is 15 (days: [1..5], [6,7], [8], [9], [10]). "
            "Binary search on the answer."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated weights.\nThe third line contains D.",
        "output_format": "Print the minimum ship capacity.",
        "constraints": "1 <= D <= n <= 10^5\n1 <= w[i] <= 10^4",
        "solve": solve_ship,
        "tests": [
            "10\n1 2 3 4 5 6 7 8 9 10\n5\n",
            "6\n3 2 2 4 1 4\n3\n",
            "1\n7\n1\n",
            "5\n1 2 3 1 1\n4\n",
            "4\n5 5 5 5\n4\n",
            "4\n5 5 5 5\n1\n",
            _big(225, 40000, 1, 1000, 37),
            _big(226, 40000, 1, 10000, 40000),
        ],
    },
    {
        "title": "Set Matrix Zeroes",
        "difficulty": "MEDIUM",
        "tags": "Matrix,Hashing",
        "description": (
            "Given an r x c matrix, if an element is 0, set its entire row and entire column to 0. "
            "Only zeroes present in the original matrix trigger this; zeroes you create do not spread further. "
            "For example, rows [1 1 1], [1 0 1], [1 1 1] become [1 0 1], [0 0 0], [1 0 1]."
        ),
        "input_format": "The first line contains r and c.\nEach of the next r lines contains c space-separated integers.",
        "output_format": "Print the resulting matrix: r lines, each with c space-separated integers.",
        "constraints": "1 <= r, c <= 300\n-10^9 <= values <= 10^9",
        "solve": solve_set_zeroes,
        "tests": [
            "3 3\n1 1 1\n1 0 1\n1 1 1\n",
            "3 4\n0 1 2 0\n3 4 5 2\n1 3 1 5\n",
            "1 1\n0\n",
            "1 1\n5\n",
            "2 2\n1 2\n3 4\n",
            "2 3\n-1 0 -3\n4 5 6\n",
            "4 1\n1\n0\n3\n4\n",
            _rmat(150, 150, _matrix_test(227, 150, 150, 1, 999, 0.0005)),
        ],
    },
    {
        "title": "Submatrix Sum Queries",
        "difficulty": "MEDIUM",
        "tags": "Matrix,Prefix Sum",
        "description": (
            "Given an r x c matrix and q queries, each query (r1, c1, r2, c2) asks for the sum of all elements in the rectangle with top-left corner "
            "(r1, c1) and bottom-right corner (r2, c2), using 1-indexed rows and columns. "
            "Build a 2D prefix-sum table so that each query is answered in O(1)."
        ),
        "input_format": "The first line contains r and c.\nEach of the next r lines contains c space-separated integers.\nThe next line contains q.\nEach of the next q lines contains r1 c1 r2 c2.",
        "output_format": "For each query, print the rectangle sum on its own line.",
        "constraints": "1 <= r, c <= 500\n1 <= q <= 10^5\n-10^9 <= values <= 10^9\n1 <= r1 <= r2 <= r, 1 <= c1 <= c2 <= c\nSums may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_2d_prefix,
        "tests": [
            "3 3\n1 2 3\n4 5 6\n7 8 9\n3\n1 1 2 2\n2 2 3 3\n1 1 3 3\n",
            "2 4\n3 0 1 4\n5 6 3 2\n2\n1 2 2 3\n2 1 2 4\n",
            "1 1\n-5\n1\n1 1 1 1\n",
            "2 2\n1000000000 1000000000\n1000000000 1000000000\n2\n1 1 2 2\n2 1 2 2\n",
            "3 1\n-1\n-2\n-3\n2\n1 1 3 1\n2 1 3 1\n",
            _prefix2d_test(228, 120, 120, 8000),
        ],
    },

    # ------------------------------------------------------------ HARD
    {
        "title": "Median of Two Sorted Arrays",
        "difficulty": "HARD",
        "tags": "Arrays,Binary Search,Divide and Conquer",
        "description": (
            "Given two sorted arrays, find the median of all n + m values combined. If the total count is odd, the median is the middle value; "
            "if even, it is the average of the two middle values. "
            "For example, [1, 3] and [2] give 2.0, while [1, 2] and [3, 4] give 2.5. "
            "The classic challenge is to do it in O(log(min(n, m))) time."
        ),
        "input_format": "The first line contains n.\nThe second line contains n sorted integers.\nThe third line contains m.\nThe fourth line contains m sorted integers.",
        "output_format": "Print the median with exactly one digit after the decimal point (the median is always a whole number or ends in .5). Examples: 2.0, 2.5, -0.5.",
        "constraints": "1 <= n, m <= 10^5\n-10^9 <= values <= 10^9",
        "solve": solve_median,
        "tests": [
            "2\n1 3\n1\n2\n",
            "2\n1 2\n2\n3 4\n",
            "1\n-1\n1\n0\n",
            "1\n5\n1\n5\n",
            "3\n-5 -3 -1\n3\n-6 -4 -2\n",
            "4\n1 2 3 4\n1\n100\n",
            "1\n1000000000\n1\n999999999\n",
            "3\n0 0 0\n2\n0 0\n",
            _two_sorted(229, 9001, 8000, -10 ** 9, 10 ** 9),
        ],
    },
    {
        "title": "Sliding Window Maximum",
        "difficulty": "HARD",
        "tags": "Arrays,Sliding Window,Deque",
        "description": (
            "A window of size k slides over the array from left to right, one position at a time. For each of the n - k + 1 window positions, "
            "print the maximum value inside the window. "
            "For [1, 3, -1, -3, 5, 3, 6, 7] with k = 3 the maxima are 3 3 5 5 6 7. "
            "A monotonic deque gives an O(n) solution."
        ),
        "input_format": "The first line contains n and k.\nThe second line contains n space-separated integers.",
        "output_format": "Print n - k + 1 space-separated integers, the window maxima from left to right.",
        "constraints": "1 <= k <= n <= 10^5\n-10^9 <= a[i] <= 10^9",
        "solve": solve_window_max,
        "tests": [
            "8 3\n1 3 -1 -3 5 3 6 7\n",
            "5 1\n4 -2 7 0 3\n",
            "1 1\n-9\n",
            "5 5\n2 8 1 8 3\n",
            "6 2\n9 8 7 6 5 4\n",
            "6 3\n4 4 4 4 4 4\n",
            _window_test(230, 40000, 8000, 0, 999),
            "40000 5000\n" + _j(range(40000, 0, -1)) + "\n",
        ],
    },
    {
        "title": "Minimum Window Substring",
        "difficulty": "HARD",
        "tags": "Strings,Hashing,Sliding Window",
        "description": (
            "Given strings s and t, find the shortest substring of s that contains every character of t, including repeats "
            "(if t has two 'a's, the window needs at least two 'a's). Letters are case-sensitive. "
            "If several shortest windows exist, print the leftmost one; if none exists, print -1. "
            "For s = ADOBECODEBANC and t = ABC the answer is BANC."
        ),
        "input_format": "The first line contains s.\nThe second line contains t.\nBoth consist only of English letters (a-z, A-Z).",
        "output_format": "Print the minimum window substring, or -1 if there is none.",
        "constraints": "1 <= |s|, |t| <= 10^5",
        "solve": solve_min_window,
        "tests": [
            "ADOBECODEBANC\nABC\n",
            "a\naa\n",
            "a\na\n",
            "abc\nd\n",
            "aaflslflsldkalskaaa\naaa\n",
            "abcabc\ncba\n",
            "xyzAbBa\nAB\n",
            "aAbBcC\nabc\n",
            _min_window_big(231, 100000, 40),
        ],
    },
    {
        "title": "Trapping Rain Water",
        "difficulty": "HARD",
        "tags": "Arrays,Two Pointers,Prefix Sum",
        "description": (
            "Given n non-negative integers representing an elevation map where each bar has width 1, compute how many units of rain water "
            "are trapped after raining. The water above bar i is min(highest bar to its left, highest bar to its right) minus h[i], if positive. "
            "For [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1] the answer is 6."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated heights.",
        "output_format": "Print the total amount of trapped water.",
        "constraints": "1 <= n <= 10^5\n0 <= h[i] <= 10^9\nThe answer may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_trap,
        "tests": [
            "12\n0 1 0 2 1 0 1 3 2 1 2 1\n",
            "6\n4 2 0 3 2 5\n",
            "1\n5\n",
            "2\n3 0\n",
            "5\n1 2 3 4 5\n",
            "4\n7 7 7 7\n",
            "5\n1000000000 0 0 0 1000000000\n",
            _terrain(232, 40000),
        ],
    },
    {
        "title": "First Missing Positive",
        "difficulty": "HARD",
        "tags": "Arrays,Hashing",
        "description": (
            "Find the smallest positive integer that does not appear in the array. "
            "For example, for [3, 4, -1, 1] the answer is 2, and for [7, 8, 9, 11, 12] the answer is 1. "
            "The real challenge is to do it in O(n) time with O(1) extra space by using the array itself as a hash table."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.",
        "output_format": "Print the smallest missing positive integer.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9",
        "solve": solve_first_missing_positive,
        "tests": [
            "4\n3 4 -1 1\n",
            "5\n7 8 9 11 12\n",
            "1\n1\n",
            "1\n-3\n",
            "3\n1 2 3\n",
            "6\n2 2 1 1 3 3\n",
            "5\n0 -1 -2 2 1000000000\n",
            _fmp_test(233, 20000),
            _arr(20000, list(range(20000, 0, -1))),
        ],
    },
    {
        "title": "Count Subarrays with Sum in Range",
        "difficulty": "HARD",
        "tags": "Arrays,Prefix Sum,Binary Indexed Tree,Divide and Conquer",
        "description": (
            "Count the contiguous non-empty subarrays whose sum lies within [lo, hi] inclusive. The array may contain negative numbers. "
            "For example, for [-2, 5, -1] with lo = -2 and hi = 2 there are 3 such subarrays: [-2], [-1] and [-2, 5, -1]. "
            "An O(n^2) scan is too slow; use prefix sums with a merge sort or a Fenwick tree for O(n log n)."
        ),
        "input_format": "The first line contains n.\nThe second line contains n space-separated integers.\nThe third line contains lo and hi.",
        "output_format": "Print the number of subarrays whose sum is between lo and hi inclusive.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= a[i] <= 10^9\n-10^14 <= lo <= hi <= 10^14\nPrefix sums and the count may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_range_sum_count,
        "tests": [
            "3\n-2 5 -1\n-2 2\n",
            "5\n1 2 3 4 5\n5 9\n",
            "1\n0\n0 0\n",
            "1\n7\n8 10\n",
            "4\n0 0 0 0\n0 0\n",
            "4\n1000000000 1000000000 1000000000 1000000000\n2000000000 3000000000\n",
            "6\n-3 -3 -3 -3 -3 -3\n-9 -6\n",
            _big(234, 40000, -50, 50, "-30 40"),
        ],
    },
    {
        "title": "Subarrays with Exactly K Distinct Values",
        "difficulty": "HARD",
        "tags": "Arrays,Hashing,Sliding Window",
        "description": (
            "Count the contiguous subarrays that contain exactly k distinct values. "
            "For example, [1, 2, 1, 2, 3] with k = 2 has 7 such subarrays: [1,2], [2,1], [1,2], [2,3], [1,2,1], [2,1,2], [1,2,1,2]. "
            "Hint: exactly(k) = atMost(k) - atMost(k - 1), and atMost can be computed with a sliding window."
        ),
        "input_format": "The first line contains n and k.\nThe second line contains n space-separated integers.",
        "output_format": "Print the number of subarrays with exactly k distinct values.",
        "constraints": "1 <= k <= n <= 10^5\n-10^9 <= a[i] <= 10^9\nThe count may exceed the 32-bit integer range; use 64-bit integers.",
        "solve": solve_exact_k_distinct,
        "tests": [
            "5 2\n1 2 1 2 3\n",
            "5 3\n1 2 1 3 4\n",
            "1 1\n-4\n",
            "4 1\n6 6 6 6\n",
            "4 2\n6 6 6 6\n",
            "5 5\n1 2 3 4 5\n",
            _window_test(235, 40000, 12, 1, 30),
            _window_test(236, 40000, 1, 1, 2),
        ],
    },
]
