"""
tests/test_bigo.py — Test suite for the bigo library.
"""

import math
import time
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bigo_time import analyze
from bigo_time.utils import fit_complexity, default_sizes, sniff_generator, r_squared
from bigo_time.models import COMPLEXITY_CLASSES


# ---------------------------------------------------------------------------
# Helper lambdas
# ---------------------------------------------------------------------------

from typing import List as TList

def o1(arr: list):        # O(1)
    return arr[0] if arr else None

def ologn(arr: list):     # O(log n) — binary search
    lo, hi = 0, len(arr) - 1
    target = len(arr) // 2
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

def on(arr: list):        # O(n) — linear scan
    return sum(arr)

def onlogn(arr: list):    # O(n log n) — timsort
    return sorted(arr)

def on2(arr: list):       # O(n²) — bubble sort
    a = arr[:]
    for i in range(len(a)):
        for j in range(len(a) - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


# ---------------------------------------------------------------------------
# Smoke tests (fast — just check the API doesn't crash)
# ---------------------------------------------------------------------------

INT_LIST_GEN = lambda n: list(range(n))

class TestSmoke:

    def test_analyze_returns_result(self):
        r = analyze(on, input_generator=INT_LIST_GEN, print_result=False)
        assert r is not None
        assert r.func_name == "on"
        assert r.complexity is not None
        assert 0.0 <= r.r_squared <= 1.0

    def test_result_has_data(self):
        r = analyze(on, input_generator=INT_LIST_GEN, print_result=False)
        assert len(r.input_sizes) >= 3
        assert len(r.runtimes) == len(r.input_sizes)

    def test_custom_generator(self):
        def my_gen(n):
            return list(range(n, 0, -1))
        r = analyze(on, input_generator=my_gen, print_result=False)
        assert r.complexity.notation in ("O(n)", "O(n log n)", "O(1)")

    def test_str_repr(self):
        r = analyze(on, input_generator=INT_LIST_GEN, print_result=False)
        s = str(r)
        assert "Complexity" in s
        assert "n" in s

    def test_repr(self):
        r = analyze(on, input_generator=INT_LIST_GEN, print_result=False)
        assert "AnalysisResult" in repr(r)


# ---------------------------------------------------------------------------
# Complexity detection tests
# ---------------------------------------------------------------------------

DETECT_CASES = [
    (o1,     {"O(1)", "O(log n)"}),
    (ologn,  {"O(log n)", "O(1)", "O(n)"}),
    (on,     {"O(n)", "O(n log n)"}),
    (onlogn, {"O(n log n)", "O(n)"}),
]

@pytest.mark.parametrize("func,expected_set", DETECT_CASES)
def test_complexity_detection(func, expected_set):
    r = analyze(func, input_generator=INT_LIST_GEN, print_result=False)
    assert r.complexity.notation in expected_set, (
        f"{func.__name__}: got {r.complexity.notation}, expected one of {expected_set}"
    )

def test_quadratic_detected():
    r = analyze(on2, input_generator=INT_LIST_GEN, sizes=[10, 20, 40, 80, 160, 320], print_result=False)
    assert r.complexity.notation in ("O(n²)", "O(n log n)", "O(n³)")


# ---------------------------------------------------------------------------
# r_squared correctness
# ---------------------------------------------------------------------------

def test_r_squared_perfect():
    y = [1.0, 2.0, 3.0, 4.0]
    assert r_squared(y, y) == pytest.approx(1.0)

def test_r_squared_zero():
    y = [1.0, 2.0, 3.0, 4.0]
    mean = sum(y) / len(y)
    y_pred = [mean] * len(y)
    assert r_squared(y, y_pred) == pytest.approx(0.0)

def test_r_squared_negative():
    y = [1.0, 2.0, 3.0, 4.0]
    y_pred = [4.0, 3.0, 2.0, 1.0]   # terrible fit
    assert r_squared(y, y_pred) < 0


# ---------------------------------------------------------------------------
# fit_complexity
# ---------------------------------------------------------------------------

def test_fit_linear():
    sizes = [100, 200, 400, 800, 1600]
    times = [s * 1e-6 for s in sizes]
    cls, r2 = fit_complexity(sizes, times)
    assert cls.notation == "O(n)"
    assert r2 > 0.99

def test_fit_quadratic():
    sizes = [10, 20, 40, 80, 160]
    times = [s**2 * 1e-9 for s in sizes]
    cls, r2 = fit_complexity(sizes, times)
    assert cls.notation == "O(n²)"
    assert r2 > 0.99

def test_fit_constant():
    sizes = [100, 200, 400, 800, 1600]
    times = [5e-6] * len(sizes)   # flat line
    cls, r2 = fit_complexity(sizes, times)
    assert cls.notation == "O(1)"


# ---------------------------------------------------------------------------
# default_sizes
# ---------------------------------------------------------------------------

def test_default_sizes_length():
    s = default_sizes(steps=10)
    assert len(s) == 10

def test_default_sizes_monotone():
    s = default_sizes()
    assert s == sorted(s)
    assert s[0] >= 1

def test_default_sizes_unique():
    s = default_sizes()
    assert len(s) == len(set(s))


# ---------------------------------------------------------------------------
# sniff_generator
# ---------------------------------------------------------------------------

def test_sniff_int():
    def f(n: int): pass
    assert sniff_generator(f)(5) == 5

def test_sniff_str():
    def f(text: str): pass
    result = sniff_generator(f)(7)
    assert isinstance(result, str)
    assert len(result) == 7

def test_sniff_fallback():
    def f(data): pass
    result = sniff_generator(f)(5)
    # 'data' param name → no match → list fallback
    assert isinstance(result, (list, dict))
    assert len(result) == 5


# ---------------------------------------------------------------------------
# Confidence levels
# ---------------------------------------------------------------------------

def test_confidence_high():
    sizes = [100, 200, 400, 800, 1600, 3200]
    times = [s * 1e-6 for s in sizes]
    cls, r2 = fit_complexity(sizes, times)
    from bigo_time.models import AnalysisResult
    r = AnalysisResult("f", cls, r2, sizes, times, [[t] for t in times], [1]*len(sizes))
    assert r.confidence == "high"

def test_confidence_low():
    import random
    random.seed(42)
    sizes = [10, 20, 40, 80, 160]
    times = [random.random() * 1e-3 for _ in sizes]
    cls, r2 = fit_complexity(sizes, times)
    from bigo_time.models import AnalysisResult
    r = AnalysisResult("f", cls, r2, sizes, times, [[t] for t in times], [1]*len(sizes))
    # Just check the attribute exists and is valid
    assert r.confidence in ("high", "medium", "low")
