"""
Problem pack 3: stacks, queues, monotonic stacks, linked lists (as arrays),
greedy, intervals, recursion & backtracking, bit manipulation, simulation.

Each entry's `solve` is the reference solution; expected outputs are produced
by running it on `tests` (see build.py).
"""
import random
from collections import OrderedDict, defaultdict, deque

PROBLEMS = []


def _add(**kw):
    PROBLEMS.append(kw)


def _ints(s):
    return list(map(int, s.split()))


def _tdiv(a, b):
    """Integer division truncating toward zero (C/Java semantics)."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def _arith(a, b, op):
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    return _tdiv(a, b)


def _join(nums):
    return " ".join(map(str, nums))


# =====================================================================
# EASY
# =====================================================================

# ---------------------------------------------------------------- E1
def _valid_parens(inp):
    toks = inp.split()
    t = int(toks[0])
    pair = {')': '(', ']': '[', '}': '{'}
    out = []
    for w in toks[1:1 + t]:
        st = []
        ok = True
        for c in w:
            if c in '([{':
                st.append(c)
            else:
                if not st or st[-1] != pair[c]:
                    ok = False
                    break
                st.pop()
        out.append("YES" if ok and not st else "NO")
    return "\n".join(out)


def _rand_valid_brackets(rng, length):
    opens = length // 2
    st, res = [], []
    close = {'(': ')', '[': ']', '{': '}'}
    while opens or st:
        if opens and (not st or rng.random() < 0.5):
            c = rng.choice('([{')
            st.append(c)
            res.append(c)
            opens -= 1
        else:
            res.append(close[st.pop()])
    return ''.join(res)


def _tests_valid_parens():
    rng = random.Random(101)
    tests = [
        "4\n()\n()[]{}\n(]\n([{}])",
        "3\n([)]\n{[]}\n((",
        "5\n)\n(\n][\n{}\n(((())))",
    ]
    mid = []
    for _ in range(20):
        s = _rand_valid_brackets(rng, 2 * rng.randint(1, 15))
        if rng.random() < 0.5:
            i = rng.randrange(len(s))
            s = s[:i] + rng.choice('()[]{}') + s[i + 1:]
        mid.append(s)
    tests.append("%d\n%s" % (len(mid), "\n".join(mid)))
    big = []
    for i in range(10):
        s = _rand_valid_brackets(rng, 18000)
        if i % 2 == 1:
            j = rng.randrange(len(s))
            s = s[:j] + {'(': ']', ')': '}', '[': ')', ']': '(', '{': '[', '}': ')'}[s[j]] + s[j + 1:]
        big.append(s)
    big.append("(" * 9000 + ")" * 8999)
    tests.append("%d\n%s" % (len(big), "\n".join(big)))
    tests.append("1\n" + "({[" * 3000 + "]})" * 3000)
    return tests


_add(
    title="Valid Parentheses",
    difficulty="EASY",
    tags="Stack,String",
    description=(
        "You are given several strings made only of the characters ( ) [ ] { }. "
        "A string is valid if every opening bracket is closed by a bracket of the same type, "
        "and brackets are closed in the correct order (the most recently opened bracket must be closed first). "
        "For example \"([]{})\" is valid, while \"([)]\" and \"((\" are not. "
        "For each string, decide whether it is valid."
    ),
    input_format=(
        "The first line contains an integer T, the number of strings.\n"
        "Each of the next T lines contains one non-empty string of bracket characters."
    ),
    output_format="For each string print YES if it is valid, otherwise NO, each on its own line.",
    constraints=(
        "1 <= T <= 100\n"
        "1 <= length of each string <= 10^5\n"
        "The total length of all strings is at most 2 * 10^5"
    ),
    solve=_valid_parens,
    tests=_tests_valid_parens(),
)


# ---------------------------------------------------------------- E2
def _min_stack(inp):
    lines = inp.split("\n")
    q = int(lines[0])
    st = []
    out = []
    for line in lines[1:1 + q]:
        p = line.split()
        if p[0] == "push":
            x = int(p[1])
            st.append((x, x if not st or x < st[-1][1] else st[-1][1]))
        elif p[0] == "pop":
            if st:
                st.pop()
        elif p[0] == "top":
            out.append(str(st[-1][0]) if st else "EMPTY")
        else:
            out.append(str(st[-1][1]) if st else "EMPTY")
    return "\n".join(out)


def _tests_min_stack():
    rng = random.Random(202)
    tests = [
        "8\npush 5\npush 3\ngetMin\npush 7\ntop\npop\npop\ngetMin",
        "7\ntop\npush -2\npush 0\npush -3\ngetMin\npop\ngetMin",
        "6\npop\ngetMin\npush 4\npush 4\npop\ngetMin",
    ]

    def rand_ops(n, pushp, lo, hi):
        ops = []
        for _ in range(n):
            r = rng.random()
            if r < pushp:
                ops.append("push %d" % rng.randint(lo, hi))
            elif r < pushp + 0.15:
                ops.append("pop")
            elif r < pushp + 0.3:
                ops.append("top")
            else:
                ops.append("getMin")
        ops.append("getMin")
        return ops

    for n, pp in ((30, 0.45), (2000, 0.5)):
        ops = rand_ops(n, pp, -10 ** 9, 10 ** 9)
        tests.append("%d\n%s" % (len(ops), "\n".join(ops)))
    # large: big stack then many queries
    ops = ["push %d" % rng.randint(-999, 999) for _ in range(13000)]
    for _ in range(12000):
        r = rng.random()
        ops.append("getMin" if r < 0.6 else ("top" if r < 0.9 else "pop"))
    tests.append("%d\n%s" % (len(ops), "\n".join(ops)))
    # decreasing pushes then pops
    ops = ["push %d" % (5000 - i) for i in range(5000)]
    for _ in range(5000):
        ops.append("getMin")
        ops.append("pop")
    ops.append("getMin")
    tests.append("%d\n%s" % (len(ops), "\n".join(ops)))
    return tests


_add(
    title="Min Stack Operations",
    difficulty="EASY",
    tags="Stack,Design,Simulation",
    description=(
        "Simulate a stack that, besides the usual operations, can report its minimum element instantly. "
        "You will process a list of commands: push x puts x on top, pop removes the top element, "
        "top reports the top element and getMin reports the smallest element currently in the stack. "
        "A pop on an empty stack does nothing; top or getMin on an empty stack reports EMPTY. "
        "Try to make every operation run in O(1) time."
    ),
    input_format=(
        "The first line contains an integer Q, the number of commands.\n"
        "Each of the next Q lines contains one command: \"push x\", \"pop\", \"top\" or \"getMin\"."
    ),
    output_format=(
        "For every top and getMin command, print the answer on its own line "
        "(the value, or EMPTY if the stack is empty)."
    ),
    constraints=(
        "1 <= Q <= 2 * 10^5\n"
        "-10^9 <= x <= 10^9\n"
        "There is at least one top or getMin command."
    ),
    solve=_min_stack,
    tests=_tests_min_stack(),
)


# ---------------------------------------------------------------- E3
def _postfix(inp):
    toks = inp.split()
    n = int(toks[0])
    st = []
    for tok in toks[1:1 + n]:
        if tok in ('+', '-', '*', '/'):
            b = st.pop()
            a = st.pop()
            st.append(_arith(a, b, tok))
        else:
            st.append(int(tok))
    return str(st[-1])


def _gen_postfix(rng, nnums, lo=-100, hi=100, bound=10 ** 15):
    toks, st = [], []
    remaining = nnums
    while remaining or len(st) > 1:
        if remaining and (len(st) < 2 or rng.random() < 0.5):
            v = rng.randint(lo, hi)
            toks.append(str(v))
            st.append(v)
            remaining -= 1
        else:
            b = st.pop()
            a = st.pop()
            cands = []
            for op in '+-*/':
                if op == '/' and b == 0:
                    continue
                r = _arith(a, b, op)
                if abs(r) <= bound:
                    cands.append((op, r))
            op, r = rng.choice(cands)
            toks.append(op)
            st.append(r)
    return "%d\n%s" % (len(toks), " ".join(toks))


def _tests_postfix():
    rng = random.Random(303)
    tests = [
        "5\n2 3 + 4 *",
        "9\n5 1 2 + 4 * + 3 -",
        "1\n42",
        "3\n-7 2 /",
        "15\n15 7 1 1 + - / 3 * 2 1 1 + + -",
        _gen_postfix(rng, 12),
        _gen_postfix(rng, 300),
        _gen_postfix(rng, 15000),
    ]
    return tests


_add(
    title="Evaluate Postfix Expression",
    difficulty="EASY",
    tags="Stack,Math",
    description=(
        "In postfix (Reverse Polish) notation every operator comes after its two operands, so no parentheses are needed. "
        "For example \"2 3 + 4 *\" means (2 + 3) * 4 = 20. "
        "Evaluate the given postfix expression. The operators are +, -, * and /, where / is integer division "
        "that truncates toward zero (so 7 / -2 = -3 and -7 / 2 = -3)."
    ),
    input_format=(
        "The first line contains an integer N, the number of tokens.\n"
        "The second line contains N tokens separated by single spaces. A token is either an integer "
        "(possibly negative, like -5) or one of the operators + - * /."
    ),
    output_format="Print the value of the expression.",
    constraints=(
        "1 <= N <= 10^5\n"
        "Every number in the input satisfies -100 <= value <= 100\n"
        "The expression is valid, there is never a division by zero, and every intermediate result "
        "fits in a signed 64-bit integer (absolute value at most 10^15), so use 64-bit integers."
    ),
    solve=_postfix,
    tests=_tests_postfix(),
)


# ---------------------------------------------------------------- E4
def _remove_nth(inp):
    v = _ints(inp)
    n = v[0]
    vals = v[1:1 + n]
    k = v[1 + n]
    idx = n - k
    res = vals[:idx] + vals[idx + 1:]
    return _join(res) if res else "EMPTY"


def _tests_remove_nth():
    rng = random.Random(404)
    tests = [
        "5\n1 2 3 4 5\n2",
        "2\n10 20\n2",
        "1\n7\n1",
        "4\n9 8 7 6\n1",
        "6\n3 3 3 1 3 3\n3",
    ]
    n = 30
    tests.append("%d\n%s\n%d" % (n, _join(rng.randint(-100, 100) for _ in range(n)), 17))
    n = 40000
    tests.append("%d\n%s\n%d" % (n, _join(rng.randint(0, 999) for _ in range(n)), 12345))
    return tests


_add(
    title="Remove Nth Node From End of List",
    difficulty="EASY",
    tags="Linked List,Two Pointers",
    description=(
        "A singly linked list is given by the values of its nodes from head to tail. "
        "Remove the k-th node counted from the end of the list (k = 1 means the last node) and print the resulting list. "
        "For example, removing the 2nd node from the end of 1 -> 2 -> 3 -> 4 -> 5 gives 1 -> 2 -> 3 -> 5. "
        "As a challenge, do it in a single pass using two pointers."
    ),
    input_format=(
        "The first line contains an integer n, the number of nodes.\n"
        "The second line contains n integers, the node values from head to tail.\n"
        "The third line contains the integer k."
    ),
    output_format=(
        "Print the values of the remaining list from head to tail, separated by single spaces. "
        "If the list becomes empty, print EMPTY."
    ),
    constraints=(
        "1 <= n <= 10^5\n"
        "1 <= k <= n\n"
        "-10^9 <= value <= 10^9"
    ),
    solve=_remove_nth,
    tests=_tests_remove_nth(),
)


# ---------------------------------------------------------------- E5
def _merge_lists(inp):
    v = _ints(inp)
    n = v[0]
    a = v[1:1 + n]
    m = v[1 + n]
    b = v[2 + n:2 + n + m]
    i = j = 0
    res = []
    while i < n and j < m:
        if a[i] <= b[j]:
            res.append(a[i])
            i += 1
        else:
            res.append(b[j])
            j += 1
    res.extend(a[i:])
    res.extend(b[j:])
    return _join(res)


def _tests_merge_lists():
    rng = random.Random(505)

    def mk(n, m, lo, hi):
        a = sorted(rng.randint(lo, hi) for _ in range(n))
        b = sorted(rng.randint(lo, hi) for _ in range(m))
        return "%d\n%s\n%d\n%s" % (n, _join(a), m, _join(b))

    tests = [
        "3\n1 2 4\n3\n1 3 4",
        "2\n-5 10\n4\n-7 0 0 20",
        "1\n5\n1\n5",
        "3\n1 2 3\n2\n10 20",
        "2\n100 200\n3\n1 2 3",
        mk(15, 9, -20, 20),
        mk(20000, 15000, -999, 999),
    ]
    return tests


_add(
    title="Merge Two Sorted Lists",
    difficulty="EASY",
    tags="Linked List,Two Pointers",
    description=(
        "You are given two singly linked lists, each sorted in non-decreasing order, as the values of their nodes. "
        "Merge them into one sorted list by splicing the nodes together and print the merged list. "
        "For example, merging 1 -> 2 -> 4 with 1 -> 3 -> 4 gives 1 -> 1 -> 2 -> 3 -> 4 -> 4."
    ),
    input_format=(
        "The first line contains n, the length of the first list.\n"
        "The second line contains n integers in non-decreasing order.\n"
        "The third line contains m, the length of the second list.\n"
        "The fourth line contains m integers in non-decreasing order."
    ),
    output_format="Print the n + m values of the merged list on one line, separated by single spaces.",
    constraints=(
        "1 <= n, m <= 10^5\n"
        "-10^9 <= value <= 10^9"
    ),
    solve=_merge_lists,
    tests=_tests_merge_lists(),
)


# ---------------------------------------------------------------- E6
def _cycle_length(inp):
    v = _ints(inp)
    n = v[0]
    nxt = [0] + v[1:1 + n]
    # Floyd's tortoise and hare
    slow = fast = 1
    while True:
        if nxt[fast] == 0 or nxt[nxt[fast]] == 0:
            return "0"
        slow = nxt[slow]
        fast = nxt[nxt[fast]]
        if slow == fast:
            break
    length = 1
    cur = nxt[slow]
    while cur != slow:
        cur = nxt[cur]
        length += 1
    return str(length)


def _gen_cycle(rng, n, tail, cyc):
    """Path of `tail` nodes then a cycle of `cyc` nodes starting at node 1 (cyc=0: no cycle)."""
    labels = list(range(2, n + 1))
    rng.shuffle(labels)
    path = [1] + labels[:tail + cyc - 1]
    rest = labels[tail + cyc - 1:]
    nxt = [0] * (n + 1)
    for i in range(len(path) - 1):
        nxt[path[i]] = path[i + 1]
    nxt[path[-1]] = path[tail] if cyc else 0
    for x in rest:
        nxt[x] = rng.randint(0, n)
    return "%d\n%s" % (n, _join(nxt[1:]))


def _tests_cycle():
    rng = random.Random(606)
    return [
        "5\n2 3 4 5 3",
        "4\n2 3 4 0",
        "1\n1",
        "1\n0",
        "3\n2 3 1",
        _gen_cycle(rng, 20, 6, 5),
        _gen_cycle(rng, 30, 25, 0),
        _gen_cycle(rng, 30000, 18000, 7000),
        _gen_cycle(rng, 30000, 1, 29999),
    ]


_add(
    title="Linked List Cycle Length",
    difficulty="EASY",
    tags="Linked List,Two Pointers",
    description=(
        "A linked list has nodes numbered 1 to n, and next[i] tells you which node follows node i (0 means node i is the tail). "
        "Starting from the head, node 1, follow the next pointers. Either you eventually reach a node whose next is 0, "
        "or you get stuck going around a cycle forever. "
        "Print the number of nodes in that cycle, or 0 if the list starting at node 1 has no cycle. "
        "Can you solve it with O(1) extra memory (Floyd's tortoise and hare)?"
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n integers next[1], next[2], ..., next[n]."
    ),
    output_format="Print a single integer: the length of the cycle reachable from node 1, or 0 if there is none.",
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= next[i] <= n\n"
        "Nodes not reachable from node 1 may point anywhere and must be ignored."
    ),
    solve=_cycle_length,
    tests=_tests_cycle(),
)


# ---------------------------------------------------------------- E7
def _popcounts(inp):
    v = _ints(inp)
    q = v[0]
    return "\n".join(str(bin(x).count('1')) for x in v[1:1 + q])


def _tests_popcounts():
    rng = random.Random(707)
    tests = [
        "4\n0\n5\n255\n1024",
        "3\n7\n1000000000\n1000000000000000000",
        "1\n1",
    ]
    small = [rng.randint(0, 1000) for _ in range(20)]
    tests.append("%d\n%s" % (len(small), "\n".join(map(str, small))))
    edge = [2 ** 62 - 1, 2 ** 31 - 1, 2 ** 31, 2 ** 32 - 1, 2 ** 59, 10 ** 18 - 1, 576460752303423487]
    tests.append("%d\n%s" % (len(edge), "\n".join(map(str, edge))))
    big = [rng.randint(0, 10 ** 18) for _ in range(9000)]
    tests.append("%d\n%s" % (len(big), "\n".join(map(str, big))))
    return tests


_add(
    title="Count Set Bits",
    difficulty="EASY",
    tags="Bit Manipulation",
    description=(
        "The number of set bits of a non-negative integer is the number of 1s in its binary representation. "
        "For example 13 is 1101 in binary, so it has 3 set bits. "
        "Answer several queries, each asking for the number of set bits of a given number. "
        "Note that the numbers can be as large as 10^18, so they need a 64-bit integer type."
    ),
    input_format=(
        "The first line contains an integer Q, the number of queries.\n"
        "Each of the next Q lines contains one integer x."
    ),
    output_format="For each query print the number of set bits of x on its own line.",
    constraints=(
        "1 <= Q <= 10^5\n"
        "0 <= x <= 10^18"
    ),
    solve=_popcounts,
    tests=_tests_popcounts(),
)


# ---------------------------------------------------------------- E8
def _single_number(inp):
    v = _ints(inp)
    n = v[0]
    x = 0
    for a in v[1:1 + n]:
        x ^= a
    return str(x)


def _tests_single_number():
    rng = random.Random(808)

    def mk(pairs, lo, hi):
        vals = rng.sample(range(lo, hi), pairs + 1)
        arr = vals[:-1] * 2 + [vals[-1]]
        rng.shuffle(arr)
        return "%d\n%s" % (len(arr), _join(arr))

    return [
        "5\n4 1 2 1 2",
        "3\n-7 3 3",
        "1\n42",
        "7\n1000000000 -1000000000 5 -1000000000 1000000000 0 0",
        mk(10, -50, 50),
        mk(5000, -10 ** 9, 10 ** 9),
        mk(14000, 0, 10 ** 5),
    ]


_add(
    title="Single Number",
    difficulty="EASY",
    tags="Bit Manipulation,XOR",
    description=(
        "You are given an array in which every value appears exactly twice, except for one value that appears exactly once. "
        "Find that lonely value. "
        "A neat trick: x XOR x = 0 and x XOR 0 = x, so XOR-ing all the numbers together leaves exactly the single one. "
        "Aim for O(n) time and O(1) extra memory."
    ),
    input_format=(
        "The first line contains an odd integer n.\n"
        "The second line contains n integers."
    ),
    output_format="Print the value that appears exactly once.",
    constraints=(
        "1 <= n < 2 * 10^5, n is odd\n"
        "-10^9 <= value <= 10^9"
    ),
    solve=_single_number,
    tests=_tests_single_number(),
)


# ---------------------------------------------------------------- E9
def _cookies(inp):
    v = _ints(inp)
    n, m = v[0], v[1]
    g = sorted(v[2:2 + n])
    s = sorted(v[2 + n:2 + n + m])
    i = 0
    for size in s:
        if i < n and size >= g[i]:
            i += 1
    return str(i)


def _tests_cookies():
    rng = random.Random(909)

    def mk(n, m, lo, hi):
        return "%d %d\n%s\n%s" % (n, m, _join(rng.randint(lo, hi) for _ in range(n)),
                                  _join(rng.randint(lo, hi) for _ in range(m)))

    return [
        "3 2\n1 2 3\n1 1",
        "2 3\n1 2\n1 2 3",
        "1 1\n5\n4",
        "4 4\n7 7 7 7\n7 7 7 7",
        mk(10, 12, 1, 10),
        mk(8000, 8000, 1, 10 ** 9),
        mk(25000, 20000, 1, 1000),
    ]


_add(
    title="Assign Cookies",
    difficulty="EASY",
    tags="Greedy,Sorting",
    description=(
        "You are a parent with some cookies and some children. Child i has a greed factor g[i]: the smallest cookie "
        "size that will make them happy. Cookie j has size s[j]. Each child can receive at most one cookie and each cookie "
        "can be given to at most one child; a child is content if the cookie they get has size >= their greed factor. "
        "Find the maximum number of content children."
    ),
    input_format=(
        "The first line contains two integers n and m: the number of children and the number of cookies.\n"
        "The second line contains n integers g[1..n].\n"
        "The third line contains m integers s[1..m]."
    ),
    output_format="Print the maximum number of content children.",
    constraints=(
        "1 <= n, m <= 10^5\n"
        "1 <= g[i], s[j] <= 10^9"
    ),
    solve=_cookies,
    tests=_tests_cookies(),
)


# ---------------------------------------------------------------- E10
def _queue_two_stacks(inp):
    lines = inp.split("\n")
    q = int(lines[0])
    inbox, outbox = [], []
    out = []
    for line in lines[1:1 + q]:
        p = line.split()
        cmd = p[0]
        if cmd == "enqueue":
            inbox.append(int(p[1]))
            continue
        if cmd == "size":
            out.append(str(len(inbox) + len(outbox)))
            continue
        if not outbox:
            while inbox:
                outbox.append(inbox.pop())
        if not outbox:
            out.append("EMPTY")
        elif cmd == "dequeue":
            out.append(str(outbox.pop()))
        else:
            out.append(str(outbox[-1]))
    return "\n".join(out)


def _tests_queue():
    rng = random.Random(1010)

    def rand_ops(n, ep):
        ops = []
        for _ in range(n):
            r = rng.random()
            if r < ep:
                ops.append("enqueue %d" % rng.randint(-10 ** 9, 10 ** 9))
            elif r < ep + 0.25:
                ops.append("dequeue")
            elif r < ep + 0.4:
                ops.append("front")
            else:
                ops.append("size")
        ops.append("size")
        return "%d\n%s" % (len(ops), "\n".join(ops))

    return [
        "7\nenqueue 1\nenqueue 2\nfront\ndequeue\nenqueue 3\nsize\ndequeue",
        "6\ndequeue\nenqueue 5\nfront\ndequeue\nfront\nsize",
        "3\nenqueue -4\nenqueue -4\nsize",
        rand_ops(25, 0.4),
        rand_ops(3000, 0.45),
        rand_ops(14000, 0.5),
    ]


_add(
    title="Queue Using Two Stacks",
    difficulty="EASY",
    tags="Queue,Stack,Design,Simulation",
    description=(
        "Implement a first-in-first-out queue using only two stacks (a classic interview exercise), and use it to process a list of commands. "
        "enqueue x adds x to the back, dequeue removes the front element and reports it, front reports the front element "
        "without removing it, and size reports how many elements are in the queue. "
        "If the queue is empty, dequeue and front report EMPTY (and dequeue changes nothing). "
        "Hint: pour the input stack into the output stack only when the output stack is empty, which gives amortized O(1) per operation."
    ),
    input_format=(
        "The first line contains an integer Q, the number of commands.\n"
        "Each of the next Q lines is one of: \"enqueue x\", \"dequeue\", \"front\", \"size\"."
    ),
    output_format=(
        "For every dequeue, front and size command, print the result on its own line "
        "(a value, EMPTY, or the size)."
    ),
    constraints=(
        "1 <= Q <= 10^5\n"
        "-10^9 <= x <= 10^9\n"
        "There is at least one dequeue, front or size command."
    ),
    solve=_queue_two_stacks,
    tests=_tests_queue(),
)


# ---------------------------------------------------------------- E11
def _baseball(inp):
    toks = inp.split()
    n = int(toks[0])
    rec = []
    for t in toks[1:1 + n]:
        if t == '+':
            rec.append(rec[-1] + rec[-2])
        elif t == 'D':
            rec.append(2 * rec[-1])
        elif t == 'C':
            rec.pop()
        else:
            rec.append(int(t))
    return str(sum(rec))


def _gen_baseball(rng, n, bound=10 ** 12):
    rec, toks = [], []
    for _ in range(n):
        choices = ['num', 'num']
        if len(rec) >= 1:
            choices.append('C')
            if abs(2 * rec[-1]) <= bound:
                choices += ['D']
        if len(rec) >= 2 and abs(rec[-1] + rec[-2]) <= bound:
            choices += ['+', '+']
        c = rng.choice(choices)
        if c == 'num':
            x = rng.randint(-30000, 30000)
            rec.append(x)
            toks.append(str(x))
        elif c == 'C':
            rec.pop()
            toks.append('C')
        elif c == 'D':
            rec.append(2 * rec[-1])
            toks.append('D')
        else:
            rec.append(rec[-1] + rec[-2])
            toks.append('+')
    return "%d\n%s" % (n, " ".join(toks))


def _tests_baseball():
    rng = random.Random(1111)
    return [
        "5\n5 2 C D +",
        "8\n5 -2 4 C D 9 + +",
        "2\n1 C",
        "6\n30000 D D D D D",
        _gen_baseball(rng, 15),
        _gen_baseball(rng, 500),
        _gen_baseball(rng, 30000),
    ]


_add(
    title="Baseball Score Keeper",
    difficulty="EASY",
    tags="Stack,Simulation",
    description=(
        "You are keeping score for a game with unusual rules. You process a list of operations, each acting on the record of scores: "
        "an integer x records a new score of x; \"+\" records a new score equal to the sum of the previous two scores; "
        "\"D\" records a new score equal to double the previous score; \"C\" invalidates and removes the previous score. "
        "After all operations, print the sum of all scores on the record. "
        "For example, \"5 2 C D +\" leaves the record [5, 10, 15], whose sum is 30."
    ),
    input_format=(
        "The first line contains an integer N, the number of operations.\n"
        "The second line contains N operations separated by spaces: integers, or the symbols +, D, C."
    ),
    output_format="Print the sum of the scores on the final record (0 if the record is empty).",
    constraints=(
        "1 <= N <= 10^5\n"
        "-30000 <= x <= 30000\n"
        "\"+\" only appears when there are at least two scores on the record; \"D\" and \"C\" only when there is at least one.\n"
        "Every recorded score has absolute value at most 10^12, so use 64-bit integers for the scores and the sum."
    ),
    solve=_baseball,
    tests=_tests_baseball(),
)


# ---------------------------------------------------------------- E12
def _hanoi(inp):
    n = int(inp.split()[0])
    moves = []

    def rec(k, a, b, c):  # move k disks from a to c using b
        if k == 0:
            return
        rec(k - 1, a, c, b)
        moves.append("%d %s %s" % (k, a, c))
        rec(k - 1, b, a, c)

    rec(n, 'A', 'B', 'C')
    return str(len(moves)) + "\n" + "\n".join(moves)


_add(
    title="Tower of Hanoi Moves",
    difficulty="EASY",
    tags="Recursion",
    description=(
        "There are three pegs A, B and C. Peg A holds n disks of different sizes, numbered 1 (smallest) to n (largest), "
        "stacked with the largest at the bottom. Move the whole tower to peg C, moving one disk at a time and never placing a "
        "larger disk on top of a smaller one. "
        "Print the moves of the minimum-length solution (it is unique and uses 2^n - 1 moves). "
        "Recursive idea: move n-1 disks from A to B, move disk n from A to C, then move n-1 disks from B to C."
    ),
    input_format="A single integer n.",
    output_format=(
        "On the first line print the number of moves. Then print each move on its own line in the format \"d X Y\", "
        "meaning disk d is moved from peg X to peg Y."
    ),
    constraints="1 <= n <= 12",
    solve=_hanoi,
    tests=["2", "3", "1", "4", "7", "10", "12"],
)


# =====================================================================
# MEDIUM
# =====================================================================

# ---------------------------------------------------------------- M1
def _next_greater_circular(inp):
    v = _ints(inp)
    n = v[0]
    a = v[1:1 + n]
    res = [-1] * n
    st = []  # indices with decreasing values
    for i in range(2 * n):
        x = a[i % n]
        while st and a[st[-1]] < x:
            res[st.pop()] = x
        if i < n:
            st.append(i)
    return _join(res)


def _tests_nge():
    rng = random.Random(1212)

    def mk(n, lo, hi):
        return "%d\n%s" % (n, _join(rng.randint(lo, hi) for _ in range(n)))

    return [
        "5\n1 2 1 3 2",
        "4\n4 3 2 1",
        "1\n7",
        "3\n5 5 5",
        mk(12, -5, 5),
        mk(2000, -10 ** 9, 10 ** 9),
        "50000\n" + _join([9] * 50000),
        "40000\n" + _join(sorted((rng.randint(0, 99) for _ in range(40000)), reverse=True)),
    ]


_add(
    title="Next Greater Element in a Circular Array",
    difficulty="MEDIUM",
    tags="Stack,Monotonic Stack",
    description=(
        "Given a circular array (the element after the last one is the first one), find for every element the first element "
        "that is strictly greater than it when walking forward from it, wrapping around if needed. "
        "If no such element exists, the answer is -1. "
        "For example in [1, 2, 1, 3, 2] the answers are [2, 3, 3, -1, 3]: the last 2 wraps around and finds 3. "
        "A monotonic stack over two passes solves this in O(n)."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n integers a[0..n-1]."
    ),
    output_format="Print n integers on one line separated by spaces: the next greater element of each position, or -1.",
    constraints=(
        "1 <= n <= 10^5\n"
        "-10^9 <= a[i] <= 10^9"
    ),
    solve=_next_greater_circular,
    tests=_tests_nge(),
)


# ---------------------------------------------------------------- M2
def _daily_temps(inp):
    v = _ints(inp)
    n = v[0]
    t = v[1:1 + n]
    res = [0] * n
    st = []
    for i, x in enumerate(t):
        while st and t[st[-1]] < x:
            j = st.pop()
            res[j] = i - j
        st.append(i)
    return _join(res)


def _tests_daily():
    rng = random.Random(1313)

    def mk(n, lo, hi):
        return "%d\n%s" % (n, _join(rng.randint(lo, hi) for _ in range(n)))

    return [
        "8\n73 74 75 71 69 72 76 73",
        "4\n30 40 50 60",
        "1\n50",
        "5\n90 80 70 60 50",
        mk(15, 30, 40),
        mk(3000, 30, 100),
        "30000\n" + _join([55] * 29999 + [56]),
        "40000\n" + _join(sorted((rng.randint(30, 100) for _ in range(40000)), reverse=True)),
    ]


_add(
    title="Daily Temperatures",
    difficulty="MEDIUM",
    tags="Stack,Monotonic Stack",
    description=(
        "Given the daily temperatures, for each day find how many days you have to wait until a strictly warmer day. "
        "If there is no future day that is warmer, the answer for that day is 0. "
        "For example, for [73, 74, 75, 71, 69, 72, 76, 73] the answer is [1, 1, 4, 2, 1, 1, 0, 0]. "
        "A naive scan for each day is O(n^2); a monotonic stack gives O(n)."
    ),
    input_format=(
        "The first line contains an integer n, the number of days.\n"
        "The second line contains n integers, the temperatures."
    ),
    output_format="Print n integers on one line separated by spaces: the waiting time for each day.",
    constraints=(
        "1 <= n <= 10^5\n"
        "1 <= temperature <= 1000"
    ),
    solve=_daily_temps,
    tests=_tests_daily(),
)


# ---------------------------------------------------------------- M3
def _asteroids(inp):
    v = _ints(inp)
    n = v[0]
    st = []
    for a in v[1:1 + n]:
        alive = True
        while alive and a < 0 and st and st[-1] > 0:
            if st[-1] < -a:
                st.pop()
                continue
            if st[-1] == -a:
                st.pop()
            alive = False
        if alive:
            st.append(a)
    return _join(st) if st else "EMPTY"


def _tests_asteroids():
    rng = random.Random(1414)

    def mk(n, hi):
        arr = []
        for _ in range(n):
            x = rng.randint(1, hi)
            arr.append(x if rng.random() < 0.5 else -x)
        return "%d\n%s" % (n, _join(arr))

    return [
        "3\n5 10 -5",
        "4\n10 2 -5 8",
        "2\n8 -8",
        "4\n-2 -1 1 2",
        "5\n1 2 3 4 -10",
        mk(12, 5),
        mk(3000, 50),
        "40000\n" + _join([1] * 20000 + [-1] * 20000),
        mk(40000, 999),
    ]


_add(
    title="Asteroid Collision",
    difficulty="MEDIUM",
    tags="Stack,Simulation",
    description=(
        "Asteroids are placed in a row. Each one is given by a non-zero integer: its absolute value is its size, and its sign "
        "is its direction (positive moves right, negative moves left). All move at the same speed. "
        "When a right-moving asteroid meets a left-moving one, the smaller one explodes; if they are the same size, both explode. "
        "Asteroids moving in the same direction never meet. Print the state of the row after all collisions. "
        "For example [10, 2, -5, 8] becomes [10, 8]: 2 and -5 collide (2 explodes), then 10 and -5 collide (-5 explodes)."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n non-zero integers, the asteroids from left to right."
    ),
    output_format=(
        "Print the remaining asteroids from left to right, separated by single spaces, or EMPTY if none remain."
    ),
    constraints=(
        "1 <= n <= 10^5\n"
        "1 <= |a[i]| <= 10^9"
    ),
    solve=_asteroids,
    tests=_tests_asteroids(),
)


# ---------------------------------------------------------------- M4
def _decode_string(inp):
    s = inp.strip()
    st = []
    cur = []
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + ord(ch) - 48
        elif ch == '[':
            st.append((cur, num))
            cur, num = [], 0
        elif ch == ']':
            prev, k = st.pop()
            prev.append(''.join(cur) * k)
            cur = prev
        else:
            cur.append(ch)
    return ''.join(cur)


def _gen_encoded(rng, depth, parts, kmax):
    res = []
    for _ in range(rng.randint(1, parts)):
        if depth > 0 and rng.random() < 0.5:
            res.append("%d[%s]" % (rng.randint(1, kmax), _gen_encoded(rng, depth - 1, parts, kmax)))
        else:
            res.append(''.join(rng.choice('abcdefghij') for _ in range(rng.randint(1, 4))))
    return ''.join(res)


def _tests_decode():
    rng = random.Random(1515)
    tests = ["3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef", "abc", "10[x]", "1[a1[b1[c]]]"]
    for depth, parts, kmax, lo, hi in ((3, 3, 4, 20, 300), (5, 4, 12, 30000, 100000)):
        while True:
            s = _gen_encoded(rng, depth, parts, kmax)
            if lo <= len(_decode_string(s)) <= hi:
                tests.append(s)
                break
    tests.append("100[ab2[c]]" + "3[z]")
    tests.append("250[400[q]]")
    return tests


_add(
    title="Decode String",
    difficulty="MEDIUM",
    tags="Stack,String,Recursion",
    description=(
        "An encoded string uses the rule k[text], meaning text repeated exactly k times. Encodings can be nested. "
        "For example \"3[a]2[bc]\" decodes to \"aaabcbc\" and \"3[a2[c]]\" decodes to \"accaccacc\". "
        "Decode the given string. Use a stack (or recursion) to handle the nesting."
    ),
    input_format="A single line containing the encoded string (lowercase letters, digits and square brackets, no spaces).",
    output_format="Print the decoded string.",
    constraints=(
        "1 <= length of the encoded string <= 10^4\n"
        "The encoding is always valid; digits only appear as repeat counts k, with 1 <= k <= 500.\n"
        "The decoded string has length between 1 and 10^5."
    ),
    solve=_decode_string,
    tests=_tests_decode(),
)


# ---------------------------------------------------------------- M5
def _simplify_paths(inp):
    lines = inp.split("\n")
    t = int(lines[0])
    out = []
    for line in lines[1:1 + t]:
        st = []
        for part in line.strip().split('/'):
            if part == '' or part == '.':
                continue
            if part == '..':
                if st:
                    st.pop()
            else:
                st.append(part)
        out.append('/' + '/'.join(st))
    return "\n".join(out)


def _gen_path(rng, comps):
    words = ['.', '..', '...', 'a', 'b', 'home', 'usr', 'bin', 'x1', '_tmp', 'docs', '', '', '..', '.']
    s = '/' + '/'.join(rng.choice(words) for _ in range(comps))
    if rng.random() < 0.3:
        s += '/'
    return s


def _tests_simplify():
    rng = random.Random(1616)
    tests = [
        "4\n/home/\n/../\n/home//foo/\n/a/./b/../../c/",
        "2\n/.../a/../b/c/../d/./\n/a//b////c/d//././/..",
        "3\n/\n/..\n/./././",
    ]
    tests.append("10\n" + "\n".join(_gen_path(rng, rng.randint(1, 12)) for _ in range(10)))
    tests.append("50\n" + "\n".join(_gen_path(rng, rng.randint(1, 60)) for _ in range(50)))
    tests.append("20\n" + "\n".join(_gen_path(rng, 800) for _ in range(20)))
    tests.append("1\n" + "/" + "/".join("d%d" % i for i in range(1, 501)) + "/" + "/".join([".."] * 499))
    return tests


_add(
    title="Simplify Unix Path",
    difficulty="MEDIUM",
    tags="Stack,String",
    description=(
        "Given absolute Unix-style file paths, convert each one to its simplified canonical form. "
        "In a path, \".\" means the current directory, \"..\" means the parent directory (going up from the root stays at the root), "
        "and several consecutive slashes act as one. Any other name, including \"...\", is a normal directory name. "
        "The canonical path starts with a single slash, separates directory names by single slashes, has no trailing slash "
        "(unless it is the root \"/\") and contains no \".\" or \"..\" parts. "
        "For example \"/a/./b/../../c/\" simplifies to \"/c\"."
    ),
    input_format=(
        "The first line contains an integer T, the number of paths.\n"
        "Each of the next T lines contains one absolute path (it starts with '/'). Paths contain only English letters, digits, "
        "'.', '_' and '/', and no spaces."
    ),
    output_format="For each path, print its canonical form on its own line.",
    constraints=(
        "1 <= T <= 100\n"
        "1 <= length of each path <= 5000"
    ),
    solve=_simplify_paths,
    tests=_tests_simplify(),
)


# ---------------------------------------------------------------- M6
def _merge_intervals(inp):
    v = _ints(inp)
    n = v[0]
    iv = sorted((v[1 + 2 * i], v[2 + 2 * i]) for i in range(n))
    res = []
    for l, r in iv:
        if res and l <= res[-1][1]:
            if r > res[-1][1]:
                res[-1][1] = r
        else:
            res.append([l, r])
    return "\n".join("%d %d" % (l, r) for l, r in res)


def _gen_intervals(rng, n, maxc, maxlen, half_open=False):
    lines = []
    for _ in range(n):
        l = rng.randint(0, maxc)
        r = l + rng.randint(1 if half_open else 0, maxlen)
        lines.append("%d %d" % (l, r))
    return "%d\n%s" % (n, "\n".join(lines))


def _tests_merge_intervals():
    rng = random.Random(1717)
    return [
        "4\n1 3\n2 6\n8 10\n15 18",
        "3\n5 7\n1 5\n9 9",
        "1\n0 0",
        "4\n1 2\n3 4\n5 6\n7 8",
        "3\n1 10\n2 3\n4 5",
        _gen_intervals(rng, 15, 50, 6),
        _gen_intervals(rng, 2000, 10 ** 9 - 10 ** 6, 10 ** 6),
        _gen_intervals(rng, 12000, 10 ** 6, 200),
    ]


_add(
    title="Merge Intervals",
    difficulty="MEDIUM",
    tags="Intervals,Sorting,Greedy",
    description=(
        "You are given a list of closed intervals [l, r] in no particular order. Merge all overlapping intervals and print the result. "
        "Two intervals overlap if they share at least one point, so [1, 3] and [3, 5] merge into [1, 5], while [1, 2] and [3, 4] stay separate. "
        "For example [1,3], [2,6], [8,10], [15,18] becomes [1,6], [8,10], [15,18]."
    ),
    input_format=(
        "The first line contains an integer n, the number of intervals.\n"
        "Each of the next n lines contains two integers l and r."
    ),
    output_format=(
        "Print the merged intervals in increasing order of their start, one per line, as \"l r\"."
    ),
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= l <= r <= 10^9"
    ),
    solve=_merge_intervals,
    tests=_tests_merge_intervals(),
)


# ---------------------------------------------------------------- M7
def _meeting_rooms(inp):
    v = _ints(inp)
    n = v[0]
    ev = []
    for i in range(n):
        s, e = v[1 + 2 * i], v[2 + 2 * i]
        ev.append((s, 1))
        ev.append((e, -1))
    ev.sort()  # at equal times, -1 (end) sorts before +1 (start)
    cur = best = 0
    for _, d in ev:
        cur += d
        best = max(best, cur)
    return str(best)


def _tests_meeting_rooms():
    rng = random.Random(1818)
    return [
        "3\n0 30\n5 10\n15 20",
        "3\n1 5\n5 10\n10 15",
        "1\n7 8",
        "4\n1 10\n1 10\n1 10\n1 10",
        _gen_intervals(rng, 12, 30, 8, True),
        _gen_intervals(rng, 2000, 10 ** 9 - 10 ** 7, 10 ** 7, True),
        _gen_intervals(rng, 12000, 10 ** 5, 3000, True),
    ]


_add(
    title="Minimum Meeting Rooms",
    difficulty="MEDIUM",
    tags="Intervals,Greedy,Sorting",
    description=(
        "Each meeting occupies the half-open time interval [start, end): it begins at start and is over at end, "
        "so a meeting ending at time t and another starting at time t can use the same room. "
        "Find the minimum number of rooms needed so that all meetings can take place. "
        "For example, meetings [0,30), [5,10), [15,20) need 2 rooms."
    ),
    input_format=(
        "The first line contains an integer n, the number of meetings.\n"
        "Each of the next n lines contains two integers start and end."
    ),
    output_format="Print the minimum number of rooms.",
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= start < end <= 10^9"
    ),
    solve=_meeting_rooms,
    tests=_tests_meeting_rooms(),
)


# ---------------------------------------------------------------- M8
def _non_overlapping(inp):
    v = _ints(inp)
    n = v[0]
    iv = sorted(((v[1 + 2 * i], v[2 + 2 * i]) for i in range(n)), key=lambda x: x[1])
    kept = 0
    last = -1
    for s, e in iv:
        if s >= last:
            kept += 1
            last = e
    return str(n - kept)


def _tests_non_overlapping():
    rng = random.Random(1919)
    return [
        "4\n1 2\n2 3\n3 4\n1 3",
        "3\n1 2\n1 2\n1 2",
        "2\n1 2\n2 3",
        "1\n0 5",
        "5\n1 100\n11 22\n1 11\n2 12\n22 30",
        _gen_intervals(rng, 12, 20, 6, True),
        _gen_intervals(rng, 2000, 10 ** 9 - 10 ** 7, 10 ** 7, True),
        _gen_intervals(rng, 12000, 10 ** 5, 100, True),
    ]


_add(
    title="Non-overlapping Intervals",
    difficulty="MEDIUM",
    tags="Intervals,Greedy,Sorting",
    description=(
        "You are given n half-open intervals [start, end). Find the minimum number of intervals you need to remove so that "
        "the remaining intervals do not overlap. Intervals that only touch, like [1,2) and [2,3), do not overlap. "
        "For example, from [1,2), [2,3), [3,4), [1,3) it is enough to remove [1,3). "
        "Hint: greedily keep the interval that ends earliest."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "Each of the next n lines contains two integers start and end."
    ),
    output_format="Print the minimum number of intervals to remove.",
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= start < end <= 10^9"
    ),
    solve=_non_overlapping,
    tests=_tests_non_overlapping(),
)


# ---------------------------------------------------------------- M9
def _jump_game2(inp):
    v = _ints(inp)
    n = v[0]
    a = v[1:1 + n]
    if n == 1:
        return "0"
    jumps = cur_end = far = 0
    for i in range(n - 1):
        far = max(far, i + a[i])
        if i == cur_end:
            if far <= i:
                return "-1"
            jumps += 1
            cur_end = far
            if cur_end >= n - 1:
                return str(jumps)
    return str(jumps)


def _tests_jump2():
    rng = random.Random(2020)

    def mk(n, hi):
        return "%d\n%s" % (n, _join(rng.randint(0, hi) for _ in range(n)))

    big = [rng.randint(1, 3) for _ in range(50000)]
    big2 = [2000] * 38000
    big3 = [rng.randint(0, 9) for _ in range(50000)]
    big3[30000:30010] = [0] * 10
    return [
        "5\n2 3 1 1 4",
        "5\n3 2 1 0 4",
        "1\n0",
        "2\n0 5",
        "6\n1 1 1 1 1 1",
        mk(15, 3),
        "50000\n" + _join(big),
        "38000\n" + _join(big2),
        "50000\n" + _join(big3),
    ]


_add(
    title="Jump Game II",
    difficulty="MEDIUM",
    tags="Greedy,Array",
    description=(
        "You start at index 0 of an array a. From index i you may jump forward to any index from i+1 up to i + a[i]. "
        "Find the minimum number of jumps needed to reach the last index, or report -1 if it cannot be reached. "
        "For example with [2, 3, 1, 1, 4] the answer is 2 (jump 0 -> 1 -> 4), and with [3, 2, 1, 0, 4] you always get stuck at index 3. "
        "Think of it as a breadth-first search over ranges that can be done greedily in O(n)."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n integers a[0..n-1]."
    ),
    output_format="Print the minimum number of jumps, or -1 if the last index is unreachable.",
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= a[i] <= 10^5"
    ),
    solve=_jump_game2,
    tests=_tests_jump2(),
)


# ---------------------------------------------------------------- M10
def _gas_station(inp):
    v = _ints(inp)
    n = v[0]
    gas = v[1:1 + n]
    cost = v[1 + n:1 + 2 * n]
    if sum(gas) < sum(cost):
        return "-1"
    start = tank = 0
    for i in range(n):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    return str(start)


def _tests_gas():
    rng = random.Random(2121)

    def mk(n, hi, bias=0):
        g = [rng.randint(0, hi) for _ in range(n)]
        c = [max(0, rng.randint(0, hi) - bias) for _ in range(n)]
        return "%d\n%s\n%s" % (n, _join(g), _join(c))

    return [
        "5\n1 2 3 4 5\n3 4 5 1 2",
        "3\n2 3 4\n3 4 3",
        "1\n0\n0",
        "1\n3\n4",
        "4\n2 2 2 2\n2 2 2 2",
        mk(10, 10, 1),
        mk(20000, 10000, 2),
        mk(20000, 10000, 0),
    ]


_add(
    title="Gas Station Circuit",
    difficulty="MEDIUM",
    tags="Greedy,Array",
    description=(
        "There are n gas stations on a circular road, numbered 0 to n-1. Station i gives you gas[i] units of fuel, and driving from "
        "station i to station (i+1) mod n costs cost[i] units. You start with an empty tank at some station, fill up there, and want to "
        "drive around the whole circle once, back to where you started, without the tank ever going negative. "
        "Print the smallest starting index that works, or -1 if no starting station works. "
        "For example with gas = [1,2,3,4,5] and cost = [3,4,5,1,2] you must start at station 3."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n integers gas[0..n-1].\n"
        "The third line contains n integers cost[0..n-1]."
    ),
    output_format="Print the smallest valid starting index, or -1.",
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= gas[i], cost[i] <= 10^4"
    ),
    solve=_gas_station,
    tests=_tests_gas(),
)


# ---------------------------------------------------------------- M11
def _gen_parens(inp):
    n = int(inp.split()[0])
    res = []
    buf = []

    def rec(op, cl):
        if len(buf) == 2 * n:
            res.append(''.join(buf))
            return
        if op < n:
            buf.append('(')
            rec(op + 1, cl)
            buf.pop()
        if cl < op:
            buf.append(')')
            rec(op, cl + 1)
            buf.pop()

    rec(0, 0)
    return "\n".join(res)


_add(
    title="Generate Parentheses",
    difficulty="MEDIUM",
    tags="Backtracking,Recursion,String",
    description=(
        "Given n, print every string of n pairs of parentheses that is well-formed (balanced). "
        "Print them in lexicographic order, where '(' comes before ')'. "
        "For n = 2 the answer is (()) followed by ()(). "
        "Build the strings with backtracking: you may add '(' while fewer than n are open, and ')' while it would not close more than were opened."
    ),
    input_format="A single integer n.",
    output_format="Print all well-formed strings of n pairs of parentheses, one per line, in lexicographic order.",
    constraints="1 <= n <= 8",
    solve=_gen_parens,
    tests=["3", "1", "2", "4", "5", "7", "8"],
)


# ---------------------------------------------------------------- M12
def _combination_sum(inp):
    v = _ints(inp)
    n, target = v[0], v[1]
    c = sorted(v[2:2 + n])
    res = []
    path = []

    def dfs(start, rem):
        if rem == 0:
            res.append(_join(path))
            return
        for i in range(start, n):
            if c[i] > rem:
                break
            path.append(c[i])
            dfs(i, rem - c[i])
            path.pop()

    dfs(0, target)
    return "\n".join([str(len(res))] + res)


def _tests_combo():
    rng = random.Random(2222)
    tests = [
        "4 7\n2 3 6 7",
        "3 8\n2 3 5",
        "1 1\n2",
        "1 40\n2",
        "2 7\n4 6",
    ]
    added = 0
    while added < 3:
        n = rng.randint(3, 10)
        cands = rng.sample(range(2, 51), n)
        t = rng.randint(10, 50)
        out = _combination_sum("%d %d\n%s" % (n, t, _join(cands)))
        cnt = int(out.split("\n")[0])
        if (added == 0 and 1 <= cnt <= 30) or (added > 0 and 100 <= cnt <= 1000):
            tests.append("%d %d\n%s" % (n, t, _join(cands)))
            added += 1
    return tests


_add(
    title="Combination Sum",
    difficulty="MEDIUM",
    tags="Backtracking,Recursion",
    description=(
        "Given n distinct positive integers (candidates) and a target, find all combinations of candidates whose sum equals the target. "
        "The same candidate may be used any number of times; two combinations are different if some number is used a different number of times. "
        "Write each combination with its numbers in non-decreasing order, and list the combinations in lexicographic order "
        "(compare number by number). For candidates [2, 3, 6, 7] and target 7 the combinations are \"2 2 3\" and \"7\"."
    ),
    input_format=(
        "The first line contains two integers n and target.\n"
        "The second line contains n distinct integers, the candidates (in any order)."
    ),
    output_format=(
        "On the first line print K, the number of combinations. Then print the K combinations, one per line, "
        "numbers separated by single spaces, in the order described above. If K is 0, print only 0."
    ),
    constraints=(
        "1 <= n <= 10\n"
        "2 <= candidate <= 50\n"
        "1 <= target <= 50\n"
        "The number of combinations is at most 1000."
    ),
    solve=_combination_sum,
    tests=_tests_combo(),
)


# ---------------------------------------------------------------- M13
def _task_scheduler(inp):
    lines = inp.split()
    tasks, n = lines[0], int(lines[1])
    cnt = [0] * 26
    for ch in tasks:
        cnt[ord(ch) - 65] += 1
    mx = max(cnt)
    nmx = cnt.count(mx)
    return str(max(len(tasks), (mx - 1) * (n + 1) + nmx))


def _tests_tasks():
    rng = random.Random(2323)

    def mk(length, letters, n, skew=False):
        pool = [chr(65 + i) for i in range(letters)]
        if skew:
            w = [2 ** (letters - i) for i in range(letters)]
            s = ''.join(rng.choices(pool, weights=w, k=length))
        else:
            s = ''.join(rng.choice(pool) for _ in range(length))
        return "%s\n%d" % (s, n)

    return [
        "AAABBB\n2",
        "AAAAAABCDEFG\n2",
        "AAABBB\n0",
        "A\n100",
        "ABCDE\n4",
        mk(20, 4, 3),
        mk(100000, 26, 50),
        mk(100000, 10, 100, True),
        mk(150000, 3, 1),
    ]


_add(
    title="Task Scheduler",
    difficulty="MEDIUM",
    tags="Greedy,Counting",
    description=(
        "A CPU must run a list of tasks, each labelled with an uppercase letter; every task takes one time unit. "
        "In each time unit the CPU either runs one task or stays idle. Two tasks with the same label must be separated by at least n "
        "time units (there must be at least n other units - tasks or idle - between them). Tasks may be run in any order. "
        "Find the minimum number of time units needed to finish all tasks. "
        "For example, tasks AAABBB with n = 2 need 8 units: A B idle A B idle A B."
    ),
    input_format=(
        "The first line contains a string of uppercase letters, the tasks.\n"
        "The second line contains the integer n."
    ),
    output_format="Print the minimum number of time units.",
    constraints=(
        "1 <= number of tasks <= 1.5 * 10^5\n"
        "0 <= n <= 100"
    ),
    solve=_task_scheduler,
    tests=_tests_tasks(),
)


# =====================================================================
# HARD
# =====================================================================

# ---------------------------------------------------------------- H1
def _histogram(inp):
    v = _ints(inp)
    n = v[0]
    h = v[1:1 + n] + [0]
    st = []
    best = 0
    for i, x in enumerate(h):
        start = i
        while st and st[-1][1] >= x:
            j, hj = st.pop()
            area = hj * (i - j)
            if area > best:
                best = area
            start = j
        st.append((start, x))
    return str(best)


def _tests_histogram():
    rng = random.Random(2424)

    def mk(n, lo, hi):
        return "%d\n%s" % (n, _join(rng.randint(lo, hi) for _ in range(n)))

    return [
        "6\n2 1 5 6 2 3",
        "2\n2 4",
        "1\n0",
        "5\n3 3 3 3 3",
        mk(15, 0, 10),
        mk(16000, 900000000, 1000000000),
        "30000\n" + _join(range(1, 30001)),
        mk(50000, 0, 99),
    ]


_add(
    title="Largest Rectangle in Histogram",
    difficulty="HARD",
    tags="Stack,Monotonic Stack",
    description=(
        "A histogram consists of n bars of width 1 standing side by side; bar i has height h[i]. "
        "Find the area of the largest axis-aligned rectangle that fits completely inside the histogram. "
        "For heights [2, 1, 5, 6, 2, 3] the answer is 10 (the bars of heights 5 and 6 give a 2 x 5 rectangle). "
        "Checking every pair of bars is too slow; a monotonic stack finds the answer in O(n). "
        "The answer can exceed the 32-bit range, so use 64-bit integers."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n integers h[0..n-1]."
    ),
    output_format="Print the maximum rectangle area.",
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= h[i] <= 10^9"
    ),
    solve=_histogram,
    tests=_tests_histogram(),
)


# ---------------------------------------------------------------- H2
def _calculator(inp):
    s = inp.strip("\n")
    nums, ops = [], []
    prec = {'+': 1, '-': 1, '*': 2, '/': 2}

    def apply():
        op = ops.pop()
        b = nums.pop()
        a = nums.pop()
        nums.append(_arith(a, b, op))

    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == ' ':
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and s[j].isdigit():
                j += 1
            nums.append(int(s[i:j]))
            i = j
            continue
        if c == '(':
            ops.append(c)
        elif c == ')':
            while ops[-1] != '(':
                apply()
            ops.pop()
        else:
            while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[c]:
                apply()
            ops.append(c)
        i += 1
    while ops:
        apply()
    return str(nums[-1])


def _sp(rng, op, p):
    return (' ' if rng.random() < p else '') + op + (' ' if rng.random() < p else '')


def _calc_expr(rng, depth, nterms, sp):
    k = rng.randint(1, nterms)
    parts = []
    val = 0
    for t in range(k):
        ts, tv = _calc_term(rng, depth, nterms, sp)
        if t == 0:
            parts.append(ts)
            val = tv
        else:
            op = rng.choice('+-')
            parts.append(_sp(rng, op, sp))
            parts.append(ts)
            val = val + tv if op == '+' else val - tv
    return ''.join(parts), val


def _calc_term(rng, depth, nterms, sp):
    s, v = _calc_factor(rng, depth, nterms, sp)
    parts = [s]
    for _ in range(rng.randint(0, 2)):
        fs, fv = _calc_factor(rng, depth, nterms, sp)
        c = []
        if abs(v * fv) <= 10 ** 12:
            c.append('*')
        if fv != 0:
            c.append('/')
        if not c:
            break
        op = rng.choice(c)
        parts.append(_sp(rng, op, sp))
        parts.append(fs)
        v = v * fv if op == '*' else _tdiv(v, fv)
    return ''.join(parts), v


def _calc_factor(rng, depth, nterms, sp):
    if depth > 0 and rng.random() < 0.3:
        s, v = _calc_expr(rng, depth - 1, nterms, sp)
        return '(' + s + ')', v
    x = rng.randint(0, 1000) if rng.random() < 0.9 else rng.randint(0, 10 ** 9)
    return str(x), x


def _gen_calc(rng, top_terms, depth, nterms, sp):
    parts = []
    for t in range(top_terms):
        ts, _ = _calc_term(rng, depth, nterms, sp)
        if t:
            parts.append(_sp(rng, rng.choice('+-'), sp))
        parts.append(ts)
    return ''.join(parts)


def _tests_calc():
    rng = random.Random(2525)
    return [
        "3+2*2",
        "(1+(4+5+2)-3)+(6+8)",
        "42",
        "14 - 3 / 2",
        "7-10/3*3",
        "(0-7)/2 + 2*(5-8)/2",
        "1000000000*1000000000/7",
        _gen_calc(rng, 4, 2, 3, 0.3),
        _gen_calc(rng, 60, 4, 4, 0.2),
        _gen_calc(rng, 300, 6, 4, 0.1),
    ]


_add(
    title="Basic Calculator",
    difficulty="HARD",
    tags="Stack,Math,String,Recursion",
    description=(
        "Evaluate an arithmetic expression given as a string. It contains non-negative integers, the binary operators + - * /, "
        "parentheses and spaces. The usual rules apply: parentheses first, then * and / before + and -, and operators of the same "
        "precedence are evaluated from left to right. Division is integer division truncating toward zero (so (0-7)/2 = -3). "
        "For example \"3+2*2\" is 7 and \"(1+(4+5+2)-3)+(6+8)\" is 23. "
        "There are no unary operators: a minus sign always has a left operand."
    ),
    input_format="A single line containing the expression.",
    output_format="Print the value of the expression.",
    constraints=(
        "1 <= length of the expression <= 10^5\n"
        "Every number in the expression is between 0 and 10^9.\n"
        "Parentheses are nested at most 50 levels deep.\n"
        "The expression is valid, there is never a division by zero, and the value of every sub-expression and every intermediate "
        "result fits in a signed 64-bit integer."
    ),
    solve=_calculator,
    tests=_tests_calc(),
)


# ---------------------------------------------------------------- H3
def _nqueens(inp):
    n = int(inp.split()[0])
    full = (1 << n) - 1

    def rec(cols, d1, d2):
        if cols == full:
            return 1
        total = 0
        avail = full & ~(cols | d1 | d2)
        while avail:
            b = avail & -avail
            avail ^= b
            total += rec(cols | b, ((d1 | b) << 1) & full, (d2 | b) >> 1)
        return total

    return str(rec(0, 0, 0))


_add(
    title="N-Queens Count",
    difficulty="HARD",
    tags="Backtracking,Recursion,Bit Manipulation",
    description=(
        "Place n queens on an n x n chessboard so that no two queens attack each other: no two share a row, a column or a diagonal. "
        "Count the number of distinct arrangements. "
        "For n = 4 there are exactly 2 arrangements. "
        "Backtrack row by row; tracking used columns and diagonals with bitmasks makes the search fast."
    ),
    input_format="A single integer n.",
    output_format="Print the number of ways to place the n queens.",
    constraints="1 <= n <= 12",
    solve=_nqueens,
    tests=["4", "8", "1", "2", "3", "6", "9", "11", "12"],
)


# ---------------------------------------------------------------- H4
def _sudoku_search(g, limit):
    g = g[:]
    R = [0] * 9
    C = [0] * 9
    B = [0] * 9
    for i in range(81):
        v = g[i]
        if v:
            b = 1 << v
            r, c = divmod(i, 9)
            k = (r // 3) * 3 + c // 3
            if R[r] & b or C[c] & b or B[k] & b:
                return []
            R[r] |= b
            C[c] |= b
            B[k] |= b
    empt = [i for i in range(81) if not g[i]]
    sols = []

    def dfs(cnt):
        if cnt == len(empt):
            sols.append(g[:])
            return len(sols) >= limit
        best, bm, bc = -1, 0, 10
        for i in empt:
            if g[i]:
                continue
            r, c = divmod(i, 9)
            k = (r // 3) * 3 + c // 3
            m = ~(R[r] | C[c] | B[k]) & 0x3FE
            pc = bin(m).count('1')
            if pc < bc:
                best, bm, bc = i, m, pc
                if pc <= 1:
                    break
        if bc == 0:
            return False
        r, c = divmod(best, 9)
        k = (r // 3) * 3 + c // 3
        while bm:
            b = bm & -bm
            bm ^= b
            g[best] = b.bit_length() - 1
            R[r] |= b
            C[c] |= b
            B[k] |= b
            if dfs(cnt + 1):
                return True
            R[r] ^= b
            C[c] ^= b
            B[k] ^= b
            g[best] = 0
        return False

    dfs(0)
    return sols


def _sudoku(inp):
    rows = inp.split()[:9]
    g = [0 if ch == '.' else int(ch) for row in rows for ch in row[:9]]
    sol = _sudoku_search(g, 1)[0]
    return "\n".join(''.join(str(sol[r * 9 + c]) for c in range(9)) for r in range(9))


def _gen_sudoku(rng, min_clues):
    base = [((r * 3 + r // 3 + c) % 9) + 1 for r in range(9) for c in range(9)]
    digits = list(range(1, 10))
    rng.shuffle(digits)
    bands = [0, 1, 2]
    rng.shuffle(bands)
    rows = [b * 3 + r for b in bands for r in rng.sample(range(3), 3)]
    stacks = [0, 1, 2]
    rng.shuffle(stacks)
    cols = [s * 3 + c for s in stacks for c in rng.sample(range(3), 3)]
    full = [digits[base[rows[r] * 9 + cols[c]] - 1] for r in range(9) for c in range(9)]
    puzzle = full[:]
    order = list(range(81))
    rng.shuffle(order)
    clues = 81
    for i in order:
        if clues <= min_clues:
            break
        keep = puzzle[i]
        puzzle[i] = 0
        if len(_sudoku_search(puzzle, 2)) != 1:
            puzzle[i] = keep
        else:
            clues -= 1
    return "\n".join(''.join(str(puzzle[r * 9 + c]) if puzzle[r * 9 + c] else '.' for c in range(9)) for r in range(9))


def _tests_sudoku():
    rng = random.Random(2626)
    tests = [
        "53..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79",
        _gen_sudoku(rng, 45),
        _gen_sudoku(rng, 35),
        _gen_sudoku(rng, 30),
        _gen_sudoku(rng, 0),
        _gen_sudoku(rng, 0),
        _gen_sudoku(rng, 0),
        # a well-known hard puzzle (17 clues family style)
        "8........\n..36.....\n.7..9.2..\n.5...7...\n....457..\n...1...3.\n..1....68\n..85...1.\n.9....4..",
    ]
    return tests


_add(
    title="Sudoku Solver",
    difficulty="HARD",
    tags="Backtracking,Recursion,Bit Manipulation",
    description=(
        "Solve a 9 x 9 Sudoku puzzle. Fill every empty cell with a digit 1-9 so that each row, each column and each of the nine "
        "3 x 3 boxes contains every digit exactly once. "
        "Every puzzle given has exactly one solution. "
        "Use backtracking; choosing the empty cell with the fewest possible digits first makes even hard puzzles fast."
    ),
    input_format=(
        "Nine lines, each containing 9 characters. A character is a digit 1-9 for a given cell or '.' for an empty cell."
    ),
    output_format="Print the solved grid as nine lines of 9 digits each.",
    constraints="The puzzle is valid and has exactly one solution.",
    solve=_sudoku,
    tests=_tests_sudoku(),
)


# ---------------------------------------------------------------- H5
def _lru(inp):
    lines = inp.split("\n")
    cap, q = map(int, lines[0].split())
    cache = OrderedDict()
    out = []
    for line in lines[1:1 + q]:
        p = line.split()
        k = int(p[1])
        if p[0] == "get":
            if k in cache:
                cache.move_to_end(k)
                out.append(str(cache[k]))
            else:
                out.append("-1")
        else:
            v = int(p[2])
            if k in cache:
                cache.move_to_end(k)
            cache[k] = v
            if len(cache) > cap:
                cache.popitem(last=False)
    return "\n".join(out)


def _gen_lru(rng, cap, q, keys, getp=0.5):
    ops = []
    for _ in range(q):
        k = rng.randint(1, keys)
        if rng.random() < getp:
            ops.append("get %d" % k)
        else:
            ops.append("put %d %d" % (k, rng.randint(0, 10 ** 4)))
    ops.append("get %d" % rng.randint(1, keys))
    return "%d %d\n%s" % (cap, len(ops), "\n".join(ops))


def _tests_lru():
    rng = random.Random(2727)
    return [
        "2 9\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nput 4 4\nget 1\nget 3\nget 4",
        "2 7\nput 1 10\nput 2 20\nput 1 15\nput 3 30\nget 2\nget 1\nget 3",
        "1 5\nget 1\nput 1 5\nput 2 6\nget 1\nget 2",
        _gen_lru(rng, 3, 30, 6),
        _gen_lru(rng, 50, 3000, 100),
        _gen_lru(rng, 8000, 15000, 12000, 0.45),
        _gen_lru(rng, 100000, 14000, 9000, 0.4),
    ]


_add(
    title="LRU Cache Simulation",
    difficulty="HARD",
    tags="Design,Linked List,Hash Table,Simulation",
    description=(
        "Simulate a Least Recently Used (LRU) cache with a fixed capacity. "
        "get k returns the value stored for key k (or -1 if absent) and marks k as most recently used. "
        "put k v stores value v for key k (overwriting any old value) and marks k as most recently used; if this makes the cache "
        "hold more than capacity keys, the least recently used key is evicted. "
        "Both operations should run in O(1) on average - a hash map combined with a doubly linked list is the classic approach."
    ),
    input_format=(
        "The first line contains two integers: the capacity C and the number of operations Q.\n"
        "Each of the next Q lines is either \"get k\" or \"put k v\"."
    ),
    output_format="For every get operation, print the returned value on its own line.",
    constraints=(
        "1 <= C <= 10^5\n"
        "1 <= Q <= 2 * 10^5\n"
        "1 <= k <= 10^9, 0 <= v <= 10^9\n"
        "There is at least one get operation."
    ),
    solve=_lru,
    tests=_tests_lru(),
)


# ---------------------------------------------------------------- H6
_MOD = 10 ** 9 + 7


def _subarray_mins(inp):
    v = _ints(inp)
    n = v[0]
    a = v[1:1 + n]
    left = [0] * n   # distance to previous strictly smaller
    right = [0] * n  # distance to next smaller-or-equal
    st = []
    for i in range(n):
        while st and a[st[-1]] >= a[i]:
            st.pop()
        left[i] = i - (st[-1] if st else -1)
        st.append(i)
    st = []
    for i in range(n - 1, -1, -1):
        while st and a[st[-1]] > a[i]:
            st.pop()
        right[i] = (st[-1] if st else n) - i
        st.append(i)
    total = 0
    for i in range(n):
        total += a[i] * left[i] * right[i]
    return str(total % _MOD)


def _tests_submins():
    rng = random.Random(2828)

    def mk(n, lo, hi):
        return "%d\n%s" % (n, _join(rng.randint(lo, hi) for _ in range(n)))

    return [
        "4\n3 1 2 4",
        "5\n11 81 94 43 3",
        "1\n1000000000",
        "4\n2 2 2 2",
        mk(12, 1, 6),
        mk(16000, 1, 10 ** 9),
        "30000\n" + _join(range(1, 30001)),
        mk(50000, 1, 99),
    ]


_add(
    title="Sum of Subarray Minimums",
    difficulty="HARD",
    tags="Stack,Monotonic Stack,Math",
    description=(
        "Given an array a, consider every contiguous non-empty subarray and take its minimum element. "
        "Print the sum of all these minimums modulo 1000000007. "
        "For [3, 1, 2, 4] the minimums of the 10 subarrays are 3,1,1,1,1,1,1,2,2,4, which sum to 17. "
        "Counting, for each element, how many subarrays it is the minimum of (using monotonic stacks, with a tie-breaking rule "
        "for equal values) gives an O(n) solution. Intermediate products exceed 32 bits, so use 64-bit arithmetic."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n integers a[0..n-1]."
    ),
    output_format="Print the sum of the minimums of all subarrays, modulo 1000000007.",
    constraints=(
        "1 <= n <= 10^5\n"
        "1 <= a[i] <= 10^9"
    ),
    solve=_subarray_mins,
    tests=_tests_submins(),
)


# ---------------------------------------------------------------- H7
def _candy(inp):
    v = _ints(inp)
    n = v[0]
    r = v[1:1 + n]
    c = [1] * n
    for i in range(1, n):
        if r[i] > r[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if r[i] > r[i + 1] and c[i] <= c[i + 1]:
            c[i] = c[i + 1] + 1
    return str(sum(c))


def _tests_candy():
    rng = random.Random(2929)

    def mk(n, lo, hi):
        return "%d\n%s" % (n, _join(rng.randint(lo, hi) for _ in range(n)))

    return [
        "3\n1 0 2",
        "3\n1 2 2",
        "1\n5",
        "5\n1 3 4 5 2",
        "6\n5 4 3 2 1 0",
        mk(14, 0, 4),
        mk(16000, 0, 10 ** 9),
        "30000\n" + _join(range(30000, 0, -1)),
        mk(50000, 0, 99),
    ]


_add(
    title="Candy Distribution",
    difficulty="HARD",
    tags="Greedy,Array",
    description=(
        "n children stand in a line, each with a rating. You must give candies so that every child gets at least one candy, and every "
        "child with a strictly higher rating than an adjacent neighbour gets strictly more candies than that neighbour. "
        "Find the minimum total number of candies. "
        "For ratings [1, 0, 2] the answer is 5 (2, 1, 2), and for [1, 2, 2] it is 4 (1, 2, 1). "
        "The total can exceed the 32-bit range, so use 64-bit integers."
    ),
    input_format=(
        "The first line contains an integer n.\n"
        "The second line contains n integers, the ratings from left to right."
    ),
    output_format="Print the minimum total number of candies.",
    constraints=(
        "1 <= n <= 10^5\n"
        "0 <= rating <= 10^9"
    ),
    solve=_candy,
    tests=_tests_candy(),
)


# ---------------------------------------------------------------- H8
def _freq_stack(inp):
    lines = inp.split("\n")
    q = int(lines[0])
    freq = defaultdict(int)
    group = defaultdict(list)
    maxf = 0
    out = []
    for line in lines[1:1 + q]:
        p = line.split()
        if p[0] == "push":
            x = int(p[1])
            freq[x] += 1
            f = freq[x]
            if f > maxf:
                maxf = f
            group[f].append(x)
        else:
            if maxf == 0:
                out.append("EMPTY")
                continue
            x = group[maxf].pop()
            freq[x] -= 1
            if not group[maxf]:
                maxf -= 1
            out.append(str(x))
    return "\n".join(out)


def _gen_freq(rng, q, vals, pushp):
    ops = []
    for _ in range(q):
        if rng.random() < pushp:
            ops.append("push %d" % rng.randint(1, vals))
        else:
            ops.append("pop")
    ops.append("pop")
    return "%d\n%s" % (len(ops), "\n".join(ops))


def _tests_freq():
    rng = random.Random(3030)
    big = ["push %d" % rng.randint(1, 50) for _ in range(12000)] + ["pop"] * 12500
    return [
        "10\npush 5\npush 7\npush 5\npush 7\npush 4\npush 5\npop\npop\npop\npop",
        "6\npop\npush 3\npush 8\npop\npop\npop",
        "4\npush -1\npush -1\npop\npop",
        _gen_freq(rng, 30, 4, 0.6),
        _gen_freq(rng, 3000, 20, 0.55),
        _gen_freq(rng, 25000, 300, 0.6),
        "%d\n%s" % (len(big), "\n".join(big)),
    ]


_add(
    title="Maximum Frequency Stack",
    difficulty="HARD",
    tags="Stack,Design,Hash Table,Simulation",
    description=(
        "Simulate a frequency stack. push x pushes the integer x. pop removes and reports the most frequent element currently in the stack; "
        "if several elements are tied for the highest frequency, the one closest to the top (the most recently pushed among them) is removed. "
        "A pop on an empty stack reports EMPTY. "
        "For example after pushing 5, 7, 5, 7, 4, 5, four pops return 5, 7, 5, 4. "
        "Aim for O(1) per operation by keeping one stack per frequency level."
    ),
    input_format=(
        "The first line contains an integer Q, the number of operations.\n"
        "Each of the next Q lines is either \"push x\" or \"pop\"."
    ),
    output_format="For every pop, print the removed element (or EMPTY) on its own line.",
    constraints=(
        "1 <= Q <= 2 * 10^5\n"
        "-10^9 <= x <= 10^9\n"
        "There is at least one pop operation."
    ),
    solve=_freq_stack,
    tests=_tests_freq(),
)
