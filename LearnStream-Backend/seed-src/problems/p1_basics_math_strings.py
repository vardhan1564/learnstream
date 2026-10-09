"""
LearnStream problem pack 1: basics, math, number theory and strings.
33 problems: 14 EASY, 12 MEDIUM, 7 HARD.
"""
import random
from collections import Counter

MOD = 10**9 + 7


def _lines(inp):
    return inp.split("\n")


def _rng(seed):
    return random.Random(seed)


def _rand_word(r, n, alpha="abcdefghijklmnopqrstuvwxyz"):
    return "".join(r.choice(alpha) for _ in range(n))


# ---------------------------------------------------------------- shared math

def _is_prime(n):
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _factorize(n):
    """Trial division; fine for n <= 1e12."""
    f = []
    if n % 2 == 0:
        e = 0
        while n % 2 == 0:
            n //= 2
            e += 1
        f.append((2, e))
    i = 3
    while i * i <= n:
        if n % i == 0:
            e = 0
            while n % i == 0:
                n //= i
                e += 1
            f.append((i, e))
        i += 2
    if n > 1:
        f.append((n, 1))
    return f


def _simple_sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0] = 0
    if n >= 1:
        s[1] = 0
    i = 2
    while i * i <= n:
        if s[i]:
            s[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
        i += 1
    return s


DIG36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _to_base(n, b):
    if n == 0:
        return "0"
    out = []
    while n:
        n, d = divmod(n, b)
        out.append(DIG36[d])
    return "".join(reversed(out))


# =============================================================== EASY

# E1 Even or Odd
def solve_even_odd(inp):
    t = inp.split()
    n = int(t[0])
    return "\n".join("EVEN" if int(x) % 2 == 0 else "ODD" for x in t[1:1 + n])


def _tests_even_odd():
    r = _rng(101)
    big = [r.randint(-10**18, 10**18) for _ in range(9000)]
    return [
        "5\n4 7 0 -3 10",
        "3\n-8 15 1",
        "1\n0",
        "1\n-1",
        "4\n1000000000000000000 -1000000000000000000 999999999999999999 -999999999999999999",
        "6\n2 2 2 3 3 3",
        f"{len(big)}\n" + " ".join(map(str, big)),
    ]


# E2 Digit Sum of a Huge Number
def solve_digit_sum(inp):
    s = inp.split()[0]
    return str(sum(int(c) for c in s if c.isdigit()))


def _tests_digit_sum():
    r = _rng(102)
    big = str(r.randint(1, 9)) + "".join(r.choice("0123456789") for _ in range(99999))
    return [
        "12345",
        "-9081726354",
        "0",
        "7",
        "-1",
        "99999999999999999999999999999999999999999999999999",
        "1000000000000000000000000000000000000",
        big,
    ]


# E3 Factorial of a Large Number
def solve_factorial(inp):
    n = int(inp.split()[0])
    f = 1
    for i in range(2, n + 1):
        f *= i
    return str(f)


def _tests_factorial():
    return ["5", "25", "0", "1", "20", "21", "100", "1000"]


# E4 GCD and LCM
def solve_gcd_lcm(inp):
    from math import gcd
    t = inp.split()
    q = int(t[0])
    out = []
    for i in range(q):
        a, b = int(t[1 + 2 * i]), int(t[2 + 2 * i])
        g = gcd(a, b)
        out.append(f"{g} {a // g * b}")
    return "\n".join(out)


def _tests_gcd_lcm():
    r = _rng(104)
    big = [(r.randint(1, 10**9), r.randint(1, 10**9)) for _ in range(5000)]
    big += [(r.randint(1, 30000) * 6000, r.randint(1, 30000) * 6000) for _ in range(1000)]
    return [
        "3\n12 18\n7 5\n100 25",
        "2\n1 1\n48 180",
        "1\n1 1000000000",
        "2\n1000000000 999999999\n1000000000 1000000000",
        "3\n13 13\n17 34\n999999937 999999929",
        "4\n2 3\n4 6\n8 12\n16 24",
        f"{len(big)}\n" + "\n".join(f"{a} {b}" for a, b in big),
    ]


# E5 Prime Check
def solve_prime_check(inp):
    t = inp.split()
    q = int(t[0])
    return "\n".join("YES" if _is_prime(int(x)) else "NO" for x in t[1:1 + q])


def _tests_prime_check():
    r = _rng(105)
    big = [r.randint(1, 10**9) for _ in range(60)] + [999999937, 999999929, 1000000000,
                                                       999999893, 2147483647 % 10**9,
                                                       31607 * 31627, 99991 * 9973]
    return [
        "5\n2\n9\n17\n1\n97",
        "4\n4\n29\n100\n7919",
        "1\n1",
        "1\n2",
        "6\n3\n25\n49\n121\n169\n289",
        "5\n561\n1105\n1729\n2465\n2821",
        f"{len(big)}\n" + "\n".join(map(str, big)),
    ]


# E6 Armstrong Numbers in a Range
def solve_armstrong(inp):
    a, b = map(int, inp.split()[:2])
    res = []
    for x in range(a, b + 1):
        s = str(x)
        k = len(s)
        if sum(int(c) ** k for c in s) == x:
            res.append(x)
    return " ".join(map(str, res)) if res else "-1"


def _tests_armstrong():
    return ["100 500", "1 20", "10 99", "1 1", "153 153", "154 369",
            "1000 10000", "1 1000000"]


# E7 Leap Year Checker
def solve_leap(inp):
    t = inp.split()
    q = int(t[0])
    out = []
    for x in t[1:1 + q]:
        y = int(x)
        out.append("YES" if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0 else "NO")
    return "\n".join(out)


def _tests_leap():
    r = _rng(107)
    big = [r.randint(1, 10**9) for _ in range(3000)] + [r.randint(1, 10**7) * 100 for _ in range(1000)]
    return [
        "4\n2024\n1900\n2000\n2023",
        "3\n1600\n1700\n1996",
        "1\n1",
        "1\n4",
        "5\n100\n200\n300\n400\n500",
        "3\n1000000000\n999999996\n999999900",
        f"{len(big)}\n" + "\n".join(map(str, big)),
    ]


# E8 Count the Vowels
def solve_vowels(inp):
    line = _lines(inp)[0]
    return str(sum(1 for c in line if c in "aeiouAEIOU"))


def _tests_vowels():
    r = _rng(108)
    alpha = "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ,.!?0123456789"
    big = "x" + "".join(r.choice(alpha) for _ in range(99998)) + "y"
    return [
        "Hello World",
        "Programming is FUN, isn't it?",
        "rhythm",
        "a",
        "AEIOU aeiou",
        "Th3 qu1ck br0wn f0x!",
        "Queueing up EUOUAE",
        big,
    ]


# E9 Anagram Check
def solve_anagram(inp):
    t = inp.split()
    return "YES" if Counter(t[0]) == Counter(t[1]) else "NO"


def _tests_anagram():
    r = _rng(109)
    a = _rand_word(r, 100000)
    b = list(a)
    r.shuffle(b)
    b = "".join(b)
    c = list(b)
    i = c.index("a") if "a" in c else 0
    c[i] = "b" if c[i] != "b" else "c"
    return [
        "listen\nsilent",
        "hello\nworld",
        "a\na",
        "a\nb",
        "abc\nabcd",
        "aabbcc\nabcabc",
        "aab\nabb",
        a + "\n" + b,
        a + "\n" + "".join(c),
    ]


# E10 Capitalize Each Word
def solve_capitalize(inp):
    words = _lines(inp)[0].split()
    return " ".join(w[0].upper() + w[1:].lower() for w in words)


def _tests_capitalize():
    r = _rng(110)
    alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    big = " ".join(_rand_word(r, r.randint(1, 10), alpha) for _ in range(15000))
    return [
        "hello world from learnstream",
        "tHIS iS a TeSt",
        "a",
        "Z",
        "ALREADY CAPITALIZED WORDS",
        "x y z",
        "mcDonald o connor",
        big,
    ]


# E11 Roman to Integer
ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
         (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def _int_to_roman(n):
    out = []
    for v, s in ROMAN:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


def solve_roman_to_int(inp):
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    t = inp.split()
    q = int(t[0])
    out = []
    for s in t[1:1 + q]:
        total = 0
        for i, c in enumerate(s):
            v = val[c]
            if i + 1 < len(s) and val[s[i + 1]] > v:
                total -= v
            else:
                total += v
        out.append(str(total))
    return "\n".join(out)


def _tests_roman_to_int():
    r = _rng(111)
    big = [r.randint(1, 3999) for _ in range(5000)]
    return [
        "3\nIII\nLVIII\nMCMXCIV",
        "2\nIX\nXL",
        "1\nI",
        "1\nMMMCMXCIX",
        "6\nIV\nXC\nCD\nCM\nXLIX\nCDXLIV",
        "4\nMMXXIV\nDCCC\nLXXXVIII\nMMMDCCCLXXXVIII",
        f"{len(big)}\n" + "\n".join(_int_to_roman(x) for x in big),
    ]


# E12 Integer to Roman
def solve_int_to_roman(inp):
    t = inp.split()
    q = int(t[0])
    return "\n".join(_int_to_roman(int(x)) for x in t[1:1 + q])


def _tests_int_to_roman():
    r = _rng(112)
    big = [r.randint(1, 3999) for _ in range(5000)]
    return [
        "3\n3\n58\n1994",
        "3\n4\n9\n40",
        "1\n1",
        "1\n3999",
        "6\n14\n44\n90\n400\n900\n944",
        "4\n2024\n3888\n1000\n500",
        f"{len(big)}\n" + "\n".join(map(str, big)),
    ]


# E13 Decimal to Any Base
def solve_to_base(inp):
    t = inp.split()
    q = int(t[0])
    out = []
    for i in range(q):
        n, b = int(t[1 + 2 * i]), int(t[2 + 2 * i])
        out.append(_to_base(n, b))
    return "\n".join(out)


def _tests_to_base():
    r = _rng(113)
    big = [(r.randint(0, 10**18), r.randint(2, 36)) for _ in range(5000)]
    return [
        "3\n10 2\n255 16\n35 36",
        "2\n100 8\n7 7",
        "1\n0 2",
        "1\n1 36",
        "3\n1000000000000000000 2\n1000000000000000000 36\n1000000000000000000 10",
        "4\n36 36\n1295 36\n15 16\n16 16",
        f"{len(big)}\n" + "\n".join(f"{a} {b}" for a, b in big),
    ]


# E14 Run-Length Compression
def solve_rle(inp):
    s = inp.split()[0]
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i))
        i = j
    return "".join(out)


def _tests_rle():
    r = _rng(114)
    big = "".join(r.choice("ab") * r.randint(1, 30) for _ in range(6000))[:100000]
    return [
        "aaabbc",
        "abcd",
        "z",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "aabbaa",
        "abababab",
        "q" * 100000,
        big,
    ]


# =============================================================== MEDIUM

# M1 Count Primes up to N
def solve_count_primes(inp):
    n = int(inp.split()[0])
    return str(sum(_simple_sieve(n)))


def _tests_count_primes():
    return ["10", "30", "1", "2", "100", "1000000", "4999999", "5000000"]


# M2 Modular Exponentiation
def solve_powmod(inp):
    t = inp.split()
    q = int(t[0])
    out = []
    for i in range(q):
        a, b, m = int(t[1 + 3 * i]), int(t[2 + 3 * i]), int(t[3 + 3 * i])
        out.append(str(pow(a, b, m)))
    return "\n".join(out)


def _tests_powmod():
    r = _rng(202)
    big = [(r.randint(0, 10**18), r.randint(0, 10**18), r.randint(1, 10**9)) for _ in range(3000)]
    return [
        "3\n2 10 1000\n3 4 5\n5 0 7",
        "2\n7 13 11\n10 18 1000000007",
        "1\n0 0 1",
        "3\n0 0 5\n0 5 5\n5 5 1",
        "2\n1000000000000000000 1000000000000000000 1000000000\n999999999999999999 999999999999999999 999999937",
        "3\n2 1000000000000000000 1000000007\n123456789 987654321 998244353\n1 1000000000000000000 2",
        f"{len(big)}\n" + "\n".join(f"{a} {b} {m}" for a, b, m in big),
    ]


# M3 Modular Inverse
def solve_modinv(inp):
    from math import gcd
    t = inp.split()
    q = int(t[0])
    out = []
    for i in range(q):
        a, m = int(t[1 + 2 * i]), int(t[2 + 2 * i])
        out.append(str(pow(a, -1, m)) if gcd(a, m) == 1 else "-1")
    return "\n".join(out)


def _tests_modinv():
    r = _rng(203)
    big = [(r.randint(0, 10**9), r.randint(2, 10**9)) for _ in range(5000)]
    return [
        "3\n3 7\n10 17\n4 8",
        "2\n2 1000000007\n6 9",
        "1\n1 2",
        "2\n0 5\n5 5",
        "3\n1000000000 999999999\n999999999 1000000000\n123456789 1000000000",
        "4\n7 7\n14 21\n1 1000000000\n999999999 2",
        f"{len(big)}\n" + "\n".join(f"{a} {m}" for a, m in big),
    ]


# M4 Longest Common Prefix
def solve_lcp(inp):
    t = inp.split()
    n = int(t[0])
    ws = t[1:1 + n]
    p = ws[0]
    for w in ws[1:]:
        k = 0
        while k < len(p) and k < len(w) and p[k] == w[k]:
            k += 1
        p = p[:k]
    return p if p else "-1"


def _tests_lcp():
    r = _rng(204)
    pre = _rand_word(r, 300)
    big = [pre + _rand_word(r, r.randint(0, 700)) for _ in range(100)]
    big[r.randrange(100)] = pre
    big2 = ["a" * 1000 for _ in range(100)]
    return [
        "3\nflower\nflow\nflight",
        "3\ndog\nracecar\ncar",
        "1\nsingle",
        "2\na\na",
        "2\nab\nb",
        "4\ninterview\ninternet\ninterval\ninternal",
        "3\nabc\nabc\nab",
        f"{len(big)}\n" + "\n".join(big),
        f"{len(big2)}\n" + "\n".join(big2),
    ]


# M5 String Rotation Check
def solve_rotation(inp):
    t = inp.split()
    s, u = t[0], t[1]
    if len(s) != len(u):
        return "-1"
    i = (s + s).find(u)
    return str(i if 0 <= i < len(s) else -1)


def _tests_rotation():
    r = _rng(205)
    s = _rand_word(r, 100000, "ab")
    k = 61234
    hard = "a" * 99999 + "b"
    return [
        "waterbottle\nerbottlewat",
        "abcd\nacbd",
        "a\na",
        "a\nb",
        "abc\nabcd",
        "abab\nbaba",
        "aaaa\naaaa",
        s + "\n" + s[k:] + s[:k],
        hard + "\n" + "a" * 50000 + "b" + "a" * 49999,
        hard + "\n" + "a" * 50000 + "c" + "a" * 49999,
    ]


# M6 Word Frequency
def solve_word_freq(inp):
    c = Counter(inp.split())
    items = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    return "\n".join(f"{w} {k}" for w, k in items)


def _tests_word_freq():
    r = _rng(206)
    vocab = [_rand_word(r, r.randint(1, 6)) for _ in range(300)]
    lines = []
    for _ in range(2000):
        lines.append(" ".join(r.choice(vocab[: r.randint(1, 300)]) for _ in range(15)))
    return [
        "the cat and the dog and the bird",
        "to be or not\nto be",
        "hello",
        "b a c",
        "zz zz zz a a a m",
        "x\n\ny\n   x   y\nz",
        "\n".join(lines),
    ]


# M7 Sum of Divisor Counts
def solve_divcount_sum(inp):
    n = int(inp.split()[0])
    total = 0
    i = 1
    while i <= n:
        q = n // i
        j = n // q
        total += q * (j - i + 1)
        i = j + 1
    return str(total)


def _tests_divcount_sum():
    return ["4", "10", "1", "2", "1000", "123456789", "999999999989", "1000000000000"]


# M8 Euler's Totient
def solve_totient(inp):
    t = inp.split()
    q = int(t[0])
    out = []
    for x in t[1:1 + q]:
        n = int(x)
        res = n
        for p, _ in _factorize(n):
            res = res // p * (p - 1)
        out.append(str(res))
    return "\n".join(out)


def _tests_totient():
    r = _rng(208)
    big = [999999999989, 1000000000000, 999999000001, 963761198400, 999966000289,
           r.randint(1, 10**12), r.randint(1, 10**12), 2**39, 3**25, 999999999959]
    return [
        "3\n9\n10\n13",
        "2\n1\n36",
        "1\n1",
        "1\n2",
        "4\n97\n100\n1024\n1000000007",
        "5\n6\n30\n210\n2310\n30030",
        f"{len(big)}\n" + "\n".join(map(str, big)),
    ]


# M9 Multiply Large Numbers
def solve_bigmul(inp):
    t = inp.split()
    return str(int(t[0]) * int(t[1]))


def _tests_bigmul():
    r = _rng(209)

    def num(d, neg=False):
        s = str(r.randint(1, 9)) + "".join(r.choice("0123456789") for _ in range(d - 1))
        return ("-" if neg else "") + s
    return [
        "123\n456",
        "-25\n4",
        "0\n-987654321",
        "1\n1",
        "-1\n-1",
        "99999999999999999999\n99999999999999999999",
        num(1000) + "\n" + num(1000, True),
        num(1000, True) + "\n" + num(1000, True),
        "-" + "9" * 1000 + "\n" + "9" * 1000,
    ]


# M10 nCr Modulo a Prime
def solve_ncr(inp):
    t = inp.split()
    q = int(t[0])
    qs = [(int(t[1 + 2 * i]), int(t[2 + 2 * i])) for i in range(q)]
    mx = max(n for n, _ in qs)
    fact = [1] * (mx + 1)
    for i in range(1, mx + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (mx + 1)
    inv[mx] = pow(fact[mx], MOD - 2, MOD)
    for i in range(mx, 0, -1):
        inv[i - 1] = inv[i] * i % MOD
    out = []
    for n, k in qs:
        out.append(str(fact[n] * inv[k] % MOD * inv[n - k] % MOD) if k <= n else "0")
    return "\n".join(out)


def _tests_ncr():
    r = _rng(210)
    big = []
    for _ in range(10000):
        n = r.randint(0, 10**6)
        big.append((n, r.randint(0, n) if r.random() < 0.95 else n + r.randint(1, 10)))
    return [
        "3\n5 2\n10 3\n6 0",
        "2\n4 4\n3 5",
        "1\n0 0",
        "2\n1 0\n1 1",
        "3\n1000000 500000\n1000000 1\n1000000 999999",
        "3\n100 50\n60 30\n20 10",
        f"{len(big)}\n" + "\n".join(f"{n} {k}" for n, k in big),
    ]


# M11 Pattern Occurrence Count
def solve_pattern(inp):
    t = inp.split()
    text, pat = t[0], t[1]
    m = len(pat)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k and pat[i] != pat[k]:
            k = pi[k - 1]
        if pat[i] == pat[k]:
            k += 1
        pi[i] = k
    cnt, first, k = 0, -1, 0
    for i, c in enumerate(text):
        while k and c != pat[k]:
            k = pi[k - 1]
        if c == pat[k]:
            k += 1
        if k == m:
            cnt += 1
            if first < 0:
                first = i - m + 2
            k = pi[k - 1]
    return f"{cnt} {first}"


def _tests_pattern():
    r = _rng(211)
    rand = _rand_word(r, 100000, "ab")
    return [
        "abababa\naba",
        "hello\nworld",
        "a\na",
        "a\naa",
        "aaaaa\naa",
        "mississippi\nissi",
        rand + "\n" + "abbab",
        "a" * 100000 + "\n" + "a" * 49999 + "b",
        "a" * 100000 + "\n" + "a" * 50000,
    ]


# M12 Base Conversion
def solve_base_conv(inp):
    t = inp.split()
    a, b, s = int(t[0]), int(t[1]), t[2]
    return _to_base(int(s, a), b)


def _tests_base_conv():
    r = _rng(212)

    def num(base, d):
        return DIG36[r.randint(1, base - 1)] + "".join(DIG36[r.randrange(base)] for _ in range(d - 1))
    return [
        "2 10 101101",
        "16 2 1F",
        "10 2 0",
        "36 10 ZZ",
        "10 36 1295",
        "7 7 654321",
        "2 36 " + "1" * 100,
        "36 2 " + num(36, 100),
        "13 29 " + num(13, 100),
    ]


# =============================================================== HARD

# H1 Fibonacci for Huge N
def _fib_pair(n):
    if n == 0:
        return 0, 1
    a, b = _fib_pair(n >> 1)
    c = a * ((2 * b - a) % MOD) % MOD
    d = (a * a + b * b) % MOD
    return (d, (c + d) % MOD) if n & 1 else (c, d)


def solve_fib_huge(inp):
    t = inp.split()
    q = int(t[0])
    return "\n".join(str(_fib_pair(int(x))[0]) for x in t[1:1 + q])


def _tests_fib_huge():
    r = _rng(301)
    big = [r.randint(0, 10**18) for _ in range(1000)]
    return [
        "4\n0\n1\n10\n50",
        "2\n2\n100",
        "1\n0",
        "1\n1000000000000000000",
        "5\n90\n91\n92\n93\n94",
        "3\n1000000006\n2000000016\n123456789012345678",
        f"{len(big)}\n" + "\n".join(map(str, big)),
    ]


# H2 Longest Palindromic Substring
def solve_lps(inp):
    s = inp.split()[0]
    t = "^#" + "#".join(s) + "#$"
    n = len(t)
    p = [0] * n
    c = rgt = 0
    for i in range(1, n - 1):
        if i < rgt:
            p[i] = min(rgt - i, p[2 * c - i])
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1
        if i + p[i] > rgt:
            c, rgt = i, i + p[i]
    best_len, best_start = 0, 0
    for i in range(1, n - 1):
        ln = p[i]
        st = (i - ln) // 2
        if ln > best_len or (ln == best_len and st < best_start):
            best_len, best_start = ln, st
    return s[best_start:best_start + best_len]


def _tests_lps():
    r = _rng(302)
    rand = _rand_word(r, 200000, "ab")
    half = _rand_word(r, 30000)
    planted = _rand_word(r, 70000) + half + half[::-1] + _rand_word(r, 70000)
    return [
        "babad",
        "cbbd",
        "a",
        "abcde",
        "aaaa",
        "forgeeksskeegfor",
        "a" * 200000,
        rand,
        planted,
        ("ab" * 100000),
    ]


# H3 Prefix Occurrence Sum (Z-function)
def solve_prefix_occ(inp):
    s = inp.split()[0]
    n = len(s)
    z = [0] * n
    z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return str(sum(z))


def _tests_prefix_occ():
    r = _rng(303)
    rand = _rand_word(r, 200000, "ab")
    per = ("abaab" * 40000)
    return [
        "abab",
        "aaa",
        "a",
        "ab",
        "abacaba",
        "zzzzzzzzzz",
        "a" * 200000,
        rand,
        per,
    ]


# H4 nCr Modulo a Small Prime (Lucas)
def solve_lucas(inp):
    t = inp.split()
    p, q = int(t[0]), int(t[1])
    fact = [1] * p
    for i in range(1, p):
        fact[i] = fact[i - 1] * i % p
    out = []
    for i in range(q):
        n, k = int(t[2 + 2 * i]), int(t[3 + 2 * i])
        if k > n:
            out.append("0")
            continue
        res = 1
        while n or k:
            a, b = n % p, k % p
            if b > a:
                res = 0
                break
            res = res * fact[a] % p * pow(fact[b] * fact[a - b] % p, p - 2, p) % p
            n //= p
            k //= p
        out.append(str(res))
    return "\n".join(out)


def _tests_lucas():
    r = _rng(304)
    big1 = [(r.randint(0, 10**18), 0) for _ in range(5000)]
    big1 = [(n, r.randint(0, n)) for n, _ in big1]
    big2 = []
    for _ in range(5000):
        n = r.randint(0, 10**18)
        big2.append((n, r.randint(0, n) if r.random() < 0.9 else n + r.randint(1, 100)))
    return [
        "7 3\n10 3\n5 2\n7 7",
        "5 3\n6 2\n100 50\n3 5",
        "2 1\n0 0",
        "2 4\n1 1\n3 1\n4 2\n1000000000000000000 500000000000000000",
        "13 3\n12 6\n13 1\n169 13",
        "999983 3\n1000000000000000000 999983\n999982 1\n123456789 98765",
        f"999983 {len(big1)}\n" + "\n".join(f"{n} {k}" for n, k in big1),
        f"3 {len(big2)}\n" + "\n".join(f"{n} {k}" for n, k in big2),
    ]


# H5 GCD Sum
def solve_gcd_sum(inp):
    t = inp.split()
    q = int(t[0])
    out = []
    for x in t[1:1 + q]:
        n = int(x)
        res = 1
        for p, e in _factorize(n):
            res *= (e + 1) * p ** e - e * p ** (e - 1)
        out.append(str(res))
    return "\n".join(out)


def _tests_gcd_sum():
    r = _rng(305)
    big = [999999999989, 1000000000000, 963761198400, 999999000001, 999966000289,
           r.randint(1, 10**12), r.randint(1, 10**12), 2**39, 735134400, 999999999959]
    return [
        "3\n6\n1\n12",
        "2\n7\n10",
        "1\n1",
        "1\n2",
        "4\n16\n81\n100\n720720",
        "3\n1000000007\n1000000\n999999",
        f"{len(big)}\n" + "\n".join(map(str, big)),
    ]


# H6 Primes in a Range (segmented sieve)
_BASE = None


def solve_range_primes(inp):
    global _BASE
    t = inp.split()
    q = int(t[0])
    if _BASE is None:
        s = _simple_sieve(10**6)
        _BASE = [i for i in range(len(s)) if s[i]]
    out = []
    for i in range(q):
        lo, hi = int(t[1 + 2 * i]), int(t[2 + 2 * i])
        seg = bytearray([1]) * (hi - lo + 1)
        for p in _BASE:
            if p * p > hi:
                break
            st = max(p * p, (lo + p - 1) // p * p)
            if st > hi:
                continue
            seg[st - lo::p] = bytearray(len(range(st, hi + 1, p)))
        if lo <= 1:
            for v in range(lo, min(hi, 1) + 1):
                seg[v - lo] = 0
        out.append(str(sum(seg)))
    return "\n".join(out)


def _tests_range_primes():
    r = _rng(306)
    big = []
    for _ in range(8):
        lo = r.randint(1, 10**12 - 10**6)
        big.append((lo, lo + 10**6))
    big.append((10**12 - 10**6, 10**12))
    big.append((1, 10**6 + 1))
    return [
        "2\n1 10\n10 30",
        "3\n2 2\n14 16\n97 101",
        "1\n1 1",
        "2\n1 2\n4 4",
        "2\n999999999989 999999999989\n999999999990 1000000000000",
        "3\n1 1000000\n1000000 2000000\n1000000007 1000000009",
        f"{len(big)}\n" + "\n".join(f"{a} {b}" for a, b in big),
    ]


# H7 Huge Power Modulo
def solve_huge_pow(inp):
    t = inp.split()
    a_s, b_s = t[0], t[1]
    am = 0
    for c in a_s:
        am = (am * 10 + ord(c) - 48) % MOD
    bm = 0
    bz = True
    for c in b_s:
        if c != "0":
            bz = False
        bm = (bm * 10 + ord(c) - 48) % (MOD - 1)
    if bz:
        return "1"
    if am == 0:
        return "0"
    return str(pow(am, bm, MOD))


def _tests_huge_pow():
    r = _rng(307)

    def num(d):
        return str(r.randint(1, 9)) + "".join(r.choice("0123456789") for _ in range(d - 1))
    return [
        "2\n10",
        "3\n1000000006",
        "0\n0",
        "0\n5",
        "1000000007\n0",
        "2000000014\n3",
        "5\n1000000006",
        "123456789123456789\n" + str(2 * (MOD - 1)),
        num(90000) + "\n" + num(90000),
        str(MOD) * 1000 + "\n" + num(50000),
    ]


# =============================================================== catalogue

PROBLEMS = [
    # ---------------- EASY
    dict(
        title="Even or Odd",
        difficulty="EASY",
        tags="Math,Basics",
        description=(
            "Given a list of integers, decide for each one whether it is even or odd.\n"
            "An integer is even if it is divisible by 2, otherwise it is odd. Be careful: "
            "negative numbers can be odd too, and in some languages -3 % 2 evaluates to -1, not 1."
        ),
        input_format="The first line contains an integer n.\nThe second line contains n space-separated integers.",
        output_format="Print n lines. Line i is EVEN if the i-th number is even and ODD otherwise.",
        constraints="1 <= n <= 100000\n-10^18 <= each number <= 10^18 (use 64-bit integers)",
        solve=solve_even_odd,
        tests=_tests_even_odd(),
    ),
    dict(
        title="Digit Sum of a Huge Number",
        difficulty="EASY",
        tags="Math,Strings",
        description=(
            "You are given an integer that may have up to 100000 digits, far too large for any built-in "
            "integer type. Print the sum of its decimal digits. A leading minus sign is not a digit and "
            "does not change the answer.\n"
            "Example: for -9081726354 the digit sum is 9+0+8+1+7+2+6+3+5+4 = 45."
        ),
        input_format="A single line containing the integer, optionally preceded by '-'. It has no leading zeros (except the number 0 itself).",
        output_format="Print a single integer: the sum of the digits.",
        constraints="1 <= number of digits <= 100000",
        solve=solve_digit_sum,
        tests=_tests_digit_sum(),
    ),
    dict(
        title="Factorial of a Large Number",
        difficulty="EASY",
        tags="Math,Big Integers",
        description=(
            "Compute n! = 1 * 2 * ... * n exactly, with every digit. By definition 0! = 1.\n"
            "Note that 21! already exceeds the range of a 64-bit integer, so you will need big-integer "
            "arithmetic (BigInteger in Java, Python ints, or digit arrays in C++)."
        ),
        input_format="A single integer n.",
        output_format="Print n! in decimal without leading zeros.",
        constraints="0 <= n <= 1000",
        solve=solve_factorial,
        tests=_tests_factorial(),
    ),
    dict(
        title="GCD and LCM",
        difficulty="EASY",
        tags="Math,Number Theory",
        description=(
            "For each pair of positive integers a and b, print their greatest common divisor and their "
            "least common multiple.\n"
            "Example: for 12 and 18 the GCD is 6 and the LCM is 36. Use the Euclidean algorithm, and compute "
            "the LCM as a / gcd(a, b) * b to avoid overflow."
        ),
        input_format="The first line contains an integer T, the number of pairs.\nEach of the next T lines contains two integers a and b.",
        output_format="For each pair print one line with two integers: gcd(a, b) and lcm(a, b), separated by a space.",
        constraints="1 <= T <= 10000\n1 <= a, b <= 10^9\nThe LCM can be as large as 10^18, so use 64-bit integers.",
        solve=solve_gcd_lcm,
        tests=_tests_gcd_lcm(),
    ),
    dict(
        title="Prime Check",
        difficulty="EASY",
        tags="Math,Number Theory,Primes",
        description=(
            "A prime number is an integer greater than 1 whose only positive divisors are 1 and itself. "
            "For each given number, decide whether it is prime.\n"
            "Hint: you only need to test divisors up to the square root of the number."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains one integer n.",
        output_format="For each n print YES if it is prime and NO otherwise, one answer per line.",
        constraints="1 <= T <= 100\n1 <= n <= 10^9",
        solve=solve_prime_check,
        tests=_tests_prime_check(),
    ),
    dict(
        title="Armstrong Numbers in a Range",
        difficulty="EASY",
        tags="Math,Basics",
        description=(
            "An Armstrong number is a number that equals the sum of its own digits, each raised to the power "
            "of the number of digits. For example, 153 is an Armstrong number because it has 3 digits and "
            "1^3 + 5^3 + 3^3 = 153. Every single-digit number is an Armstrong number.\n"
            "List all Armstrong numbers between a and b, inclusive."
        ),
        input_format="A single line with two integers a and b.",
        output_format="Print all Armstrong numbers x with a <= x <= b in increasing order, separated by single spaces. If there are none, print -1.",
        constraints="1 <= a <= b <= 1000000",
        solve=solve_armstrong,
        tests=_tests_armstrong(),
    ),
    dict(
        title="Leap Year Checker",
        difficulty="EASY",
        tags="Math,Basics",
        description=(
            "In the Gregorian calendar a year is a leap year if it is divisible by 4, except that years "
            "divisible by 100 are not leap years, unless they are also divisible by 400.\n"
            "So 2024 and 2000 are leap years, while 1900 and 2023 are not. Check each given year."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains one year y.",
        output_format="For each year print YES if it is a leap year and NO otherwise, one per line.",
        constraints="1 <= T <= 10000\n1 <= y <= 10^9",
        solve=solve_leap,
        tests=_tests_leap(),
    ),
    dict(
        title="Count the Vowels",
        difficulty="EASY",
        tags="Strings,Basics",
        description=(
            "Count how many vowels appear in a line of text. The vowels are a, e, i, o and u, in either "
            "lowercase or uppercase. The letter y is not a vowel here, and every other character "
            "(spaces, digits, punctuation) is ignored.\n"
            "Example: \"Hello World\" contains 3 vowels (e, o, o)."
        ),
        input_format="A single line of text. It may contain letters, digits, spaces and punctuation, and it does not start or end with a space.",
        output_format="Print a single integer: the number of vowels in the line.",
        constraints="1 <= length of the line <= 100000",
        solve=solve_vowels,
        tests=_tests_vowels(),
    ),
    dict(
        title="Anagram Check",
        difficulty="EASY",
        tags="Strings,Hashing,Counting",
        description=(
            "Two strings are anagrams if one can be rearranged to form the other, meaning they contain exactly "
            "the same letters with the same counts. For example, listen and silent are anagrams, but aab and abb "
            "are not. Decide whether the two given strings are anagrams."
        ),
        input_format="The first line contains the string s.\nThe second line contains the string t.\nBoth consist of lowercase English letters only.",
        output_format="Print YES if s and t are anagrams of each other, otherwise print NO.",
        constraints="1 <= |s|, |t| <= 100000",
        solve=solve_anagram,
        tests=_tests_anagram(),
    ),
    dict(
        title="Capitalize Each Word",
        difficulty="EASY",
        tags="Strings,Basics",
        description=(
            "Given a sentence, rewrite every word so that its first letter is uppercase and all of its "
            "remaining letters are lowercase.\n"
            "Example: \"tHIS iS a TeSt\" becomes \"This Is A Test\"."
        ),
        input_format="A single line containing words made of English letters (a-z, A-Z), separated by single spaces, with no leading or trailing spaces.",
        output_format="Print the transformed sentence, with words separated by single spaces.",
        constraints="1 <= number of words <= 20000\n1 <= length of each word <= 10\nTotal line length <= 200000",
        solve=solve_capitalize,
        tests=_tests_capitalize(),
    ),
    dict(
        title="Roman to Integer",
        difficulty="EASY",
        tags="Strings,Math",
        description=(
            "Roman numerals use the symbols I=1, V=5, X=10, L=50, C=100, D=500 and M=1000. Symbols are usually "
            "written from largest to smallest and added together, but when a smaller symbol appears directly "
            "before a larger one it is subtracted instead (IV=4, IX=9, XL=40, XC=90, CD=400, CM=900).\n"
            "Example: MCMXCIV = 1000 + 900 + 90 + 4 = 1994. Convert each numeral to its integer value."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains one Roman numeral in standard form.",
        output_format="For each numeral print its integer value on its own line.",
        constraints="1 <= T <= 5000\nEach numeral represents a value between 1 and 3999 and is written in the standard (minimal) form.",
        solve=solve_roman_to_int,
        tests=_tests_roman_to_int(),
    ),
    dict(
        title="Integer to Roman",
        difficulty="EASY",
        tags="Strings,Math,Greedy",
        description=(
            "Convert each integer to its standard Roman numeral. Use the symbols I=1, V=5, X=10, L=50, C=100, "
            "D=500, M=1000 and the subtractive pairs IV=4, IX=9, XL=40, XC=90, CD=400, CM=900. The standard form "
            "always uses the largest possible symbol first.\n"
            "Example: 1994 is written MCMXCIV and 58 is written LVIII."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains one integer n.",
        output_format="For each n print its Roman numeral (uppercase letters) on its own line.",
        constraints="1 <= T <= 5000\n1 <= n <= 3999",
        solve=solve_int_to_roman,
        tests=_tests_int_to_roman(),
    ),
    dict(
        title="Decimal to Any Base",
        difficulty="EASY",
        tags="Math,Base Conversion",
        description=(
            "Convert a non-negative decimal integer n into base b. Digits greater than 9 are written with "
            "uppercase letters: A=10, B=11, ..., Z=35.\n"
            "Example: 255 in base 16 is FF, 10 in base 2 is 1010, and 0 in any base is 0."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains two integers n and b.",
        output_format="For each query print n written in base b, without leading zeros, on its own line.",
        constraints="1 <= T <= 5000\n0 <= n <= 10^18 (use 64-bit integers)\n2 <= b <= 36",
        solve=solve_to_base,
        tests=_tests_to_base(),
    ),
    dict(
        title="Run-Length Compression",
        difficulty="EASY",
        tags="Strings,Basics",
        description=(
            "Compress a string by replacing each maximal run of equal consecutive characters with the "
            "character followed by the length of the run. Runs of length 1 are also written with a count.\n"
            "Example: aaabbc becomes a3b2c1, and aabbaa becomes a2b2a2."
        ),
        input_format="A single line containing a string s of lowercase English letters.",
        output_format="Print the compressed string.",
        constraints="1 <= |s| <= 100000",
        solve=solve_rle,
        tests=_tests_rle(),
    ),

    # ---------------- MEDIUM
    dict(
        title="Count Primes up to N",
        difficulty="MEDIUM",
        tags="Math,Number Theory,Primes,Sieve",
        description=(
            "Count how many prime numbers are less than or equal to N.\n"
            "Checking every number one by one is too slow for the largest inputs. Use the Sieve of "
            "Eratosthenes: start from 2, and for every number still marked as prime, cross out all of its "
            "multiples. Example: there are 4 primes up to 10 (2, 3, 5, 7)."
        ),
        input_format="A single integer N.",
        output_format="Print the number of primes p with 2 <= p <= N.",
        constraints="1 <= N <= 5000000",
        solve=solve_count_primes,
        tests=_tests_count_primes(),
    ),
    dict(
        title="Modular Exponentiation",
        difficulty="MEDIUM",
        tags="Math,Number Theory,Fast Exponentiation",
        description=(
            "Compute a^b mod m for several queries. The exponent can be as large as 10^18, so multiplying "
            "a by itself b times is far too slow: use binary (fast) exponentiation, which needs only about "
            "log2(b) multiplications. Treat 0^0 as 1.\n"
            "Example: 2^10 = 1024, so 2^10 mod 1000 = 24."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains three integers a, b and m.",
        output_format="For each query print a^b mod m (a value between 0 and m-1) on its own line.",
        constraints="1 <= T <= 3000\n0 <= a, b <= 10^18\n1 <= m <= 10^9\nReduce a modulo m first; products of two values below m fit in a 64-bit integer.",
        solve=solve_powmod,
        tests=_tests_powmod(),
    ),
    dict(
        title="Modular Inverse",
        difficulty="MEDIUM",
        tags="Math,Number Theory,Extended Euclid",
        description=(
            "The modular inverse of a modulo m is an integer x with 0 <= x < m such that (a * x) mod m = 1. "
            "It exists exactly when gcd(a, m) = 1, and then it is unique. The modulus m is not necessarily "
            "prime, so use the extended Euclidean algorithm.\n"
            "Example: the inverse of 3 modulo 7 is 5, because 3 * 5 = 15 = 2 * 7 + 1."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains two integers a and m.",
        output_format="For each query print the modular inverse x (0 <= x < m), or -1 if it does not exist, on its own line.",
        constraints="1 <= T <= 5000\n0 <= a <= 10^9\n2 <= m <= 10^9",
        solve=solve_modinv,
        tests=_tests_modinv(),
    ),
    dict(
        title="Longest Common Prefix",
        difficulty="MEDIUM",
        tags="Strings",
        description=(
            "Find the longest string that is a prefix of every one of the given words.\n"
            "Example: for flower, flow and flight the longest common prefix is fl. For dog, racecar and car "
            "there is no common prefix at all."
        ),
        input_format="The first line contains an integer n.\nEach of the next n lines contains one word of lowercase English letters.",
        output_format="Print the longest common prefix. If it is empty, print -1.",
        constraints="1 <= n <= 1000\n1 <= length of each word <= 1000\nTotal length of all words <= 100000",
        solve=solve_lcp,
        tests=_tests_lcp(),
    ),
    dict(
        title="String Rotation Check",
        difficulty="MEDIUM",
        tags="Strings,String Matching",
        description=(
            "Rotating a string s left by k moves its first k characters to the end; for example, rotating "
            "waterbottle left by 3 gives erbottlewat. Given s and t, find the smallest k (0 <= k < |s|) such "
            "that rotating s left by k gives t, or report that no such k exists.\n"
            "Hint: t is a rotation of s exactly when the lengths match and t occurs inside s + s. Trying every "
            "k with a full comparison is O(n^2) and too slow for the largest tests."
        ),
        input_format="The first line contains the string s.\nThe second line contains the string t.\nBoth consist of lowercase English letters.",
        output_format="Print the smallest valid k, or -1 if t is not a rotation of s.",
        constraints="1 <= |s|, |t| <= 100000",
        solve=solve_rotation,
        tests=_tests_rotation(),
    ),
    dict(
        title="Word Frequency",
        difficulty="MEDIUM",
        tags="Strings,Hashing,Sorting",
        description=(
            "Given a piece of text, count how many times each distinct word appears and print the words "
            "from most frequent to least frequent. Words with the same count are printed in alphabetical "
            "(lexicographic) order.\n"
            "Example: in \"the cat and the dog and the bird\", the appears 3 times and and appears 2 times."
        ),
        input_format="The input is text spread over one or more lines. Words consist of lowercase English letters and are separated by any amount of whitespace (spaces or newlines). There is at least one word.",
        output_format="For each distinct word print a line containing the word and its count separated by a space, ordered by count descending, then by word ascending.",
        constraints="1 <= total number of words <= 100000\n1 <= length of each word <= 20",
        solve=solve_word_freq,
        tests=_tests_word_freq(),
    ),
    dict(
        title="Sum of Divisor Counts",
        difficulty="MEDIUM",
        tags="Math,Number Theory",
        description=(
            "Let d(i) be the number of positive divisors of i. Compute D(N) = d(1) + d(2) + ... + d(N).\n"
            "Example: d(1..4) = 1, 2, 2, 3, so D(4) = 8. Hint: D(N) also equals the sum of floor(N / i) for "
            "i = 1..N, and floor(N / i) takes only about 2 * sqrt(N) distinct values, so you can group equal "
            "terms together. A loop over all i up to N is too slow."
        ),
        input_format="A single integer N.",
        output_format="Print D(N).",
        constraints="1 <= N <= 10^12\nThe answer exceeds the 32-bit range; use 64-bit integers.",
        solve=solve_divcount_sum,
        tests=_tests_divcount_sum(),
    ),
    dict(
        title="Euler's Totient",
        difficulty="MEDIUM",
        tags="Math,Number Theory,Prime Factorization",
        description=(
            "Euler's totient phi(n) counts the integers k with 1 <= k <= n and gcd(k, n) = 1. If n has distinct "
            "prime factors p1, ..., pr, then phi(n) = n * (1 - 1/p1) * ... * (1 - 1/pr).\n"
            "Example: phi(9) = 6 (1, 2, 4, 5, 7, 8) and phi(1) = 1. Compute phi(n) for each query."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains one integer n.",
        output_format="For each n print phi(n) on its own line.",
        constraints="1 <= T <= 10\n1 <= n <= 10^12 (use 64-bit integers)",
        solve=solve_totient,
        tests=_tests_totient(),
    ),
    dict(
        title="Multiply Large Numbers",
        difficulty="MEDIUM",
        tags="Math,Strings,Big Integers",
        description=(
            "Multiply two integers that can each have up to 1000 digits and print the exact product. Implement "
            "schoolbook multiplication on digit arrays, or use your language's big-integer support.\n"
            "Remember the sign rules: the product of two negatives is positive, and a zero product is printed "
            "as 0 (never -0)."
        ),
        input_format="The first line contains the integer a.\nThe second line contains the integer b.\nEach may start with '-' and has no leading zeros; zero is written as 0.",
        output_format="Print a * b without leading zeros.",
        constraints="1 <= number of digits of a, b <= 1000",
        solve=solve_bigmul,
        tests=_tests_bigmul(),
    ),
    dict(
        title="nCr Modulo a Prime",
        difficulty="MEDIUM",
        tags="Math,Combinatorics,Modular Arithmetic",
        description=(
            "Answer many queries of the binomial coefficient C(n, r) = n! / (r! * (n - r)!) modulo "
            "1000000007, which is prime. C(n, r) is 0 when r > n.\n"
            "Precompute factorials and inverse factorials (via Fermat's little theorem: x^(p-2) is the inverse "
            "of x modulo a prime p) so that each query is answered in O(1)."
        ),
        input_format="The first line contains an integer Q.\nEach of the next Q lines contains two integers n and r.",
        output_format="For each query print C(n, r) mod 1000000007 on its own line.",
        constraints="1 <= Q <= 10000\n0 <= n, r <= 1000010",
        solve=solve_ncr,
        tests=_tests_ncr(),
    ),
    dict(
        title="Pattern Occurrence Count",
        difficulty="MEDIUM",
        tags="Strings,String Matching,KMP",
        description=(
            "Count how many times a pattern occurs in a text, including overlapping occurrences, and report "
            "where the first one starts.\n"
            "Example: aba occurs in abababa 3 times, starting at positions 1, 3 and 5 (1-based). A naive check at "
            "every position can take O(|text| * |pattern|) time; use KMP or the Z-function to run in linear time."
        ),
        input_format="The first line contains the text.\nThe second line contains the pattern.\nBoth consist of lowercase English letters.",
        output_format="Print two integers separated by a space: the number of occurrences and the 1-based starting position of the first occurrence (or -1 if there are none).",
        constraints="1 <= |text|, |pattern| <= 100000",
        solve=solve_pattern,
        tests=_tests_pattern(),
    ),
    dict(
        title="Base Conversion",
        difficulty="MEDIUM",
        tags="Math,Strings,Base Conversion,Big Integers",
        description=(
            "A number is written in base a; rewrite it in base b. Digits use 0-9 followed by uppercase letters "
            "A-Z for values 10 to 35. The number can have up to 100 digits, so it may not fit in a 64-bit integer.\n"
            "Example: 101101 in base 2 is 45 in base 10, and 1F in base 16 is 11111 in base 2."
        ),
        input_format="A single line with two integers a and b followed by the number s written in base a.",
        output_format="Print s written in base b, using uppercase letters and without leading zeros.",
        constraints="2 <= a, b <= 36\n1 <= |s| <= 100\ns contains only valid digits for base a and has no leading zeros (except the number 0 itself).",
        solve=solve_base_conv,
        tests=_tests_base_conv(),
    ),

    # ---------------- HARD
    dict(
        title="Fibonacci for Huge N",
        difficulty="HARD",
        tags="Math,Matrix Exponentiation,Modular Arithmetic",
        description=(
            "The Fibonacci numbers are F(0) = 0, F(1) = 1 and F(n) = F(n-1) + F(n-2). Compute F(n) modulo "
            "1000000007 for n as large as 10^18.\n"
            "A loop up to n is impossible here. Use the identity [[1,1],[1,0]]^n = [[F(n+1),F(n)],[F(n),F(n-1)]] "
            "with fast matrix exponentiation, or the fast-doubling formulas, to get O(log n) per query."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains one integer n.",
        output_format="For each n print F(n) mod 1000000007 on its own line.",
        constraints="1 <= T <= 1000\n0 <= n <= 10^18 (use 64-bit integers)",
        solve=solve_fib_huge,
        tests=_tests_fib_huge(),
    ),
    dict(
        title="Longest Palindromic Substring",
        difficulty="HARD",
        tags="Strings,Manacher,Palindromes",
        description=(
            "Find the longest contiguous substring of s that reads the same forwards and backwards. If several "
            "substrings share the maximum length, print the one that starts earliest (leftmost).\n"
            "Example: for babad both bab and aba have length 3, and bab starts first. With |s| up to 200000, "
            "expanding around every center is O(n^2) in the worst case; Manacher's algorithm runs in O(n)."
        ),
        input_format="A single line containing the string s of lowercase English letters.",
        output_format="Print the leftmost longest palindromic substring.",
        constraints="1 <= |s| <= 200000",
        solve=solve_lps,
        tests=_tests_lps(),
    ),
    dict(
        title="Prefix Occurrence Sum",
        difficulty="HARD",
        tags="Strings,Z-Function,String Matching",
        description=(
            "For every length k from 1 to |s|, count how many times the prefix of s of length k occurs as a "
            "substring of s (occurrences may overlap), and print the total of all these counts.\n"
            "Example: for abab, the prefixes a, ab, aba, abab occur 2, 2, 1 and 1 times, so the answer is 6. "
            "Hint: this equals the sum of the Z-function of s, with Z[0] = |s|."
        ),
        input_format="A single line containing the string s of lowercase English letters.",
        output_format="Print the total as a single integer.",
        constraints="1 <= |s| <= 200000\nThe answer can exceed the 32-bit range; use 64-bit integers.",
        solve=solve_prefix_occ,
        tests=_tests_prefix_occ(),
    ),
    dict(
        title="nCr Modulo a Small Prime",
        difficulty="HARD",
        tags="Math,Combinatorics,Lucas Theorem,Modular Arithmetic",
        description=(
            "Compute C(n, r) modulo a prime p, where n and r can be as large as 10^18 but p is at most 10^6. "
            "Since n can exceed p, factorials modulo p become zero and the usual formula breaks down.\n"
            "Lucas' theorem helps: write n and r in base p; then C(n, r) mod p equals the product of "
            "C(n_i, r_i) mod p over their base-p digits. C(n, r) is 0 when r > n."
        ),
        input_format="The first line contains two integers p and Q.\nEach of the next Q lines contains two integers n and r.",
        output_format="For each query print C(n, r) mod p on its own line.",
        constraints="2 <= p <= 1000000, p is prime\n1 <= Q <= 5000\n0 <= n, r <= 10^18 + 100 (use 64-bit integers)",
        solve=solve_lucas,
        tests=_tests_lucas(),
    ),
    dict(
        title="GCD Sum",
        difficulty="HARD",
        tags="Math,Number Theory,Prime Factorization",
        description=(
            "For a positive integer n, compute G(n) = gcd(1, n) + gcd(2, n) + ... + gcd(n, n).\n"
            "Example: G(6) = 1 + 2 + 3 + 2 + 1 + 6 = 15. Iterating up to n is too slow for n = 10^12. Group the "
            "terms by their gcd value: G(n) is the sum of d * phi(n / d) over all divisors d of n, and it is "
            "multiplicative, so it can be computed from the prime factorization of n."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains one integer n.",
        output_format="For each n print G(n) on its own line.",
        constraints="1 <= T <= 10\n1 <= n <= 10^12\nThe answer fits in a signed 64-bit integer.",
        solve=solve_gcd_sum,
        tests=_tests_gcd_sum(),
    ),
    dict(
        title="Primes in a Range",
        difficulty="HARD",
        tags="Math,Number Theory,Primes,Segmented Sieve",
        description=(
            "Count the primes in the interval [L, R]. R can be as large as 10^12, so a sieve up to R does not "
            "fit in memory, but the interval itself is at most about a million numbers long.\n"
            "Use a segmented sieve: find all primes up to sqrt(R) with an ordinary sieve, then use them to "
            "cross out composites inside [L, R] only. Remember that 1 is not prime."
        ),
        input_format="The first line contains an integer T.\nEach of the next T lines contains two integers L and R.",
        output_format="For each query print the number of primes p with L <= p <= R on its own line.",
        constraints="1 <= T <= 10\n1 <= L <= R <= 10^12\nR - L <= 1000000",
        solve=solve_range_primes,
        tests=_tests_range_primes(),
    ),
    dict(
        title="Huge Power Modulo",
        difficulty="HARD",
        tags="Math,Number Theory,Modular Arithmetic,Fermat",
        description=(
            "Given two non-negative integers a and b, each with up to 100000 digits, compute a^b mod "
            "1000000007. Define 0^0 = 1.\n"
            "Reduce a modulo p = 1000000007 digit by digit. For the exponent, Fermat's little theorem says "
            "x^(p-1) = 1 (mod p) whenever x is not a multiple of p, so b can be reduced modulo p - 1. Be careful "
            "with the cases where a is a multiple of p or b is 0."
        ),
        input_format="The first line contains the integer a.\nThe second line contains the integer b.\nNeither has leading zeros (except the number 0 itself).",
        output_format="Print a^b mod 1000000007.",
        constraints="1 <= number of digits of a, b <= 100000",
        solve=solve_huge_pow,
        tests=_tests_huge_pow(),
    ),
]
