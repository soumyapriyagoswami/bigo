"""
bigo-time  —  examples & extended test suite
=============================================

Run all examples:
    python examples.py

Run a specific section:
    python examples.py sorting
    python examples.py searching
    python examples.py graph
    python examples.py strings
    python examples.py dp
    python examples.py tricky
    python examples.py custom
"""

import sys
import math
import random
import hashlib
from collections import defaultdict, deque
from functools import lru_cache

from bigo_time import analyze

random.seed(42)


# ─────────────────────────────────────────────
# SECTION 1 — Sorting algorithms
# ─────────────────────────────────────────────

def section_sorting():
    print("\n" + "═"*52)
    print("  SECTION 1 · Sorting algorithms")
    print("═"*52)

    # O(n log n)
    def builtin_sort(arr):
        return sorted(arr)

    # O(n log n)
    def merge_sort(arr):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left  = merge_sort(arr[:mid])
        right = merge_sort(arr[mid:])
        result, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        return result + left[i:] + right[j:]

    # O(n²)
    def insertion_sort(arr):
        a = arr[:]
        for i in range(1, len(a)):
            key = a[i]
            j = i - 1
            while j >= 0 and a[j] > key:
                a[j+1] = a[j]
                j -= 1
            a[j+1] = key
        return a

    # O(n²)
    def selection_sort(arr):
        a = arr[:]
        for i in range(len(a)):
            min_idx = i
            for j in range(i+1, len(a)):
                if a[j] < a[min_idx]:
                    min_idx = j
            a[i], a[min_idx] = a[min_idx], a[i]
        return a

    gen = lambda n: [random.randint(0, n*10) for _ in range(n)]

    analyze(builtin_sort,   input_generator=gen)
    analyze(merge_sort,     input_generator=gen)
    analyze(insertion_sort, input_generator=gen, sizes=[50,100,200,400,800,1200])
    analyze(selection_sort, input_generator=gen, sizes=[50,100,200,400,800,1200])


# ─────────────────────────────────────────────
# SECTION 2 — Searching algorithms
# ─────────────────────────────────────────────

def section_searching():
    print("\n" + "═"*52)
    print("  SECTION 2 · Searching algorithms")
    print("═"*52)

    # O(n)
    def linear_search(arr):
        target = arr[-1]          # worst case — always last
        for i, v in enumerate(arr):
            if v == target:
                return i
        return -1

    # O(log n)
    def binary_search(arr):
        target = arr[len(arr) // 2]
        lo, hi = 0, len(arr) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if arr[mid] == target:   return mid
            elif arr[mid] < target:  lo = mid + 1
            else:                    hi = mid - 1
        return -1

    # O(n)
    def find_max(arr):
        return max(arr)

    # O(n)
    def find_two_sum(arr):
        """Find pair summing to a target — hash map approach."""
        target = arr[0] + arr[-1]
        seen = {}
        for i, v in enumerate(arr):
            if target - v in seen:
                return (seen[target-v], i)
            seen[v] = i
        return None

    sorted_gen = lambda n: list(range(n))
    rand_gen   = lambda n: [random.randint(0, n*10) for _ in range(n)]

    analyze(linear_search, input_generator=sorted_gen)
    analyze(binary_search, input_generator=sorted_gen)
    analyze(find_max,      input_generator=rand_gen)
    analyze(find_two_sum,  input_generator=rand_gen)


# ─────────────────────────────────────────────
# SECTION 3 — Graph algorithms
# ─────────────────────────────────────────────

def section_graph():
    print("\n" + "═"*52)
    print("  SECTION 3 · Graph algorithms")
    print("═"*52)

    def make_graph(n):
        """Adjacency list: random sparse graph with ~3n edges."""
        g = defaultdict(list)
        for u in range(n):
            for _ in range(3):
                v = random.randint(0, n-1)
                g[u].append(v)
        return (n, dict(g))

    # O(V + E)
    def bfs(graph_tuple):
        n, g = graph_tuple
        visited = set()
        queue   = deque([0])
        visited.add(0)
        while queue:
            node = queue.popleft()
            for nb in g.get(node, []):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        return len(visited)

    # O(V + E)
    def dfs(graph_tuple):
        n, g = graph_tuple
        visited = set()
        stack   = [0]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            stack.extend(g.get(node, []))
        return len(visited)

    # O(V + E)  — topological sort (DAG)
    def topo_sort(graph_tuple):
        n, g = graph_tuple
        visited, order = set(), []
        def dfs_rec(v):
            visited.add(v)
            for nb in g.get(v, []):
                if nb not in visited:
                    dfs_rec(nb)
            order.append(v)
        for v in range(n):
            if v not in visited:
                dfs_rec(v)
        return order[::-1]

    analyze(bfs,       input_generator=make_graph)
    analyze(dfs,       input_generator=make_graph)
    analyze(topo_sort, input_generator=make_graph, sizes=[50,100,200,400,800,1500])


# ─────────────────────────────────────────────
# SECTION 4 — String algorithms
# ─────────────────────────────────────────────

def section_strings():
    print("\n" + "═"*52)
    print("  SECTION 4 · String algorithms")
    print("═"*52)

    str_gen = lambda n: ''.join(random.choices('abcdefgh', k=n))

    # O(n)
    def count_chars(s):
        freq = {}
        for c in s:
            freq[c] = freq.get(c, 0) + 1
        return freq

    # O(n)
    def is_palindrome(s):
        return s == s[::-1]

    # O(n)
    def longest_unique_substr(s):
        """Sliding window — O(n)."""
        start, max_len = 0, 0
        seen = {}
        for i, c in enumerate(s):
            if c in seen and seen[c] >= start:
                start = seen[c] + 1
            seen[c] = i
            max_len = max(max_len, i - start + 1)
        return max_len

    # O(n²)
    def naive_substr_count(s):
        """Count distinct substrings naively — O(n²) due to set insertions."""
        subs = set()
        for i in range(len(s)):
            for j in range(i+1, min(i+50, len(s))+1):   # cap j to avoid n³
                subs.add(s[i:j])
        return len(subs)

    # O(n)
    def sha256_hash(s):
        return hashlib.sha256(s.encode()).hexdigest()

    analyze(count_chars,         input_generator=str_gen)
    analyze(is_palindrome,       input_generator=str_gen)
    analyze(longest_unique_substr, input_generator=str_gen)
    analyze(naive_substr_count,  input_generator=str_gen, sizes=[50,100,200,400,800,1200])
    analyze(sha256_hash,         input_generator=str_gen)


# ─────────────────────────────────────────────
# SECTION 5 — Dynamic programming
# ─────────────────────────────────────────────

def section_dp():
    print("\n" + "═"*52)
    print("  SECTION 5 · Dynamic programming")
    print("═"*52)

    # O(n)
    def fibonacci_dp(n):
        if n <= 1: return n
        a, b = 0, 1
        for _ in range(n-1):
            a, b = b, a+b
        return b

    # O(n)
    def max_subarray(arr):
        """Kadane's algorithm."""
        max_sum = cur = arr[0]
        for v in arr[1:]:
            cur = max(v, cur + v)
            max_sum = max(max_sum, cur)
        return max_sum

    # O(n²)
    def longest_common_subseq(pair):
        a, b = pair
        m, n = len(a), len(b)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(1, m+1):
            for j in range(1, n+1):
                if a[i-1] == b[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[m][n]

    # O(n²)
    def longest_increasing_subseq(arr):
        if not arr: return 0
        dp = [1]*len(arr)
        for i in range(1, len(arr)):
            for j in range(i):
                if arr[j] < arr[i]:
                    dp[i] = max(dp[i], dp[j]+1)
        return max(dp)

    int_gen  = lambda n: n
    arr_gen  = lambda n: [random.randint(-100, 100) for _ in range(n)]
    pair_gen = lambda n: (
        [random.choice('ABCDE') for _ in range(n)],
        [random.choice('ABCDE') for _ in range(n)]
    )

    analyze(fibonacci_dp,            input_generator=int_gen)
    analyze(max_subarray,            input_generator=arr_gen)
    analyze(longest_common_subseq,   input_generator=pair_gen, sizes=[10,20,40,80,160,300])
    analyze(longest_increasing_subseq, input_generator=arr_gen, sizes=[50,100,200,400,800])


# ─────────────────────────────────────────────
# SECTION 6 — Tricky / surprising complexities
# ─────────────────────────────────────────────

def section_tricky():
    print("\n" + "═"*52)
    print("  SECTION 6 · Tricky / surprising complexities")
    print("═"*52)

    # Looks like O(n²) but is actually O(n) amortised
    def dynamic_array_append(n):
        """Python list append is O(1) amortised."""
        lst = []
        for i in range(n):
            lst.append(i)
        return lst

    # Looks O(1) but is O(n) — string concatenation in loop
    def string_concat_loop(n):
        """+ concatenation builds a new string each time → O(n²) total work."""
        s = ""
        for i in range(n):
            s += "x"
        return s

    # O(n) — join is always linear
    def string_join(n):
        return "".join(["x"] * n)

    # O(n log n) — set from list (hash + amortised)
    def list_to_set(arr):
        return set(arr)

    # O(n) — dict comprehension
    def list_to_dict(arr):
        return {v: i for i, v in enumerate(arr)}

    # O(n) — in operator on set
    def membership_set(pair):
        s, queries = pair
        return [q in s for q in queries]

    # O(n) — in operator on list  (actually O(n·q) but q=1 here)
    def membership_list(pair):
        lst, queries = pair
        return [q in lst for q in queries]

    int_gen  = lambda n: n
    arr_gen  = lambda n: [random.randint(0, n) for _ in range(n)]
    pair_gen = lambda n: (set(range(n)), [random.randint(0,n) for _ in range(n)])
    pair_list_gen = lambda n: (list(range(n)), [random.randint(0,n) for _ in range(n)])

    analyze(dynamic_array_append, input_generator=int_gen)
    analyze(string_concat_loop,   input_generator=int_gen,  sizes=[100,300,600,1000,2000,4000])
    analyze(string_join,          input_generator=int_gen)
    analyze(list_to_set,          input_generator=arr_gen)
    analyze(list_to_dict,         input_generator=arr_gen)
    analyze(membership_set,       input_generator=pair_gen)
    analyze(membership_list,      input_generator=pair_list_gen)


# ─────────────────────────────────────────────
# SECTION 7 — Custom input generators
# ─────────────────────────────────────────────

def section_custom():
    print("\n" + "═"*52)
    print("  SECTION 7 · Custom input generators")
    print("═"*52)

    # Matrix trace — O(n)
    def matrix_trace(matrix):
        return sum(matrix[i][i] for i in range(len(matrix)))

    # Naive matrix multiply — O(n³)
    def matrix_multiply(matrix):
        n   = len(matrix)
        res = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    res[i][j] += matrix[i][k] * matrix[k][j]
        return res

    # Flatten nested list — O(n)
    def flatten(nested):
        out = []
        for row in nested:
            out.extend(row)
        return out

    # Frequency map of a dict's values — O(n)
    def value_freq(d):
        freq = defaultdict(int)
        for v in d.values():
            freq[v] += 1
        return dict(freq)

    square_matrix = lambda n: [[random.randint(0,9) for _ in range(n)] for _ in range(n)]
    nested_list   = lambda n: [[random.randint(0,9) for _ in range(10)] for _ in range(n)]
    dict_gen      = lambda n: {i: random.randint(0,20) for i in range(n)}

    analyze(matrix_trace,    input_generator=square_matrix)
    analyze(matrix_multiply, input_generator=square_matrix, sizes=[5,10,15,20,30,40,55,70])
    analyze(flatten,         input_generator=nested_list)
    analyze(value_freq,      input_generator=dict_gen)


# ─────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────

SECTIONS = {
    "sorting":   section_sorting,
    "searching": section_searching,
    "graph":     section_graph,
    "strings":   section_strings,
    "dp":        section_dp,
    "tricky":    section_tricky,
    "custom":    section_custom,
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        for key in args:
            if key in SECTIONS:
                SECTIONS[key]()
            else:
                print(f"Unknown section '{key}'. Choose from: {', '.join(SECTIONS)}")
    else:
        for fn in SECTIONS.values():
            fn()
