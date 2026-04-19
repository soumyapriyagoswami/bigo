"""
Utility helpers for bigo: default generators, curve fitting, R² scoring.
"""

from __future__ import annotations
import math
import inspect
from typing import Callable, List, Tuple, Any

from .models import ComplexityClass, COMPLEXITY_CLASSES


# ---------------------------------------------------------------------------
# Default input generators
# ---------------------------------------------------------------------------

def _list_generator(n: int):
    """Default: a list of n integers."""
    return list(range(n))


def _int_generator(n: int):
    """Integer n itself."""
    return n


def _string_generator(n: int):
    """A string of length n."""
    return "a" * n


def _dict_generator(n: int):
    """A dict with n key-value pairs."""
    return {i: i for i in range(n)}


def _tuple_generator(n: int):
    """A tuple of n integers."""
    return tuple(range(n))


def _matrix_generator(n: int):
    """A 2D list (n × n) — useful for O(n²) functions."""
    return [[0] * n for _ in range(n)]


def sniff_generator(func: Callable) -> Callable[[int], Any]:
    """
    Inspect the first parameter annotation / name to pick a sensible default
    generator.  Falls back to _list_generator for unknown cases.
    """
    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if not params:
            return _int_generator   # zero-arg — just pass n (ignored)

        first = params[0]
        ann = first.annotation
        name = first.name.lower()

        # Annotation-based
        if ann is inspect.Parameter.empty:
            pass
        elif ann in (int, float):
            return _int_generator
        elif ann is str:
            return _string_generator
        elif ann is dict:
            return _dict_generator
        elif ann is tuple:
            return _tuple_generator

        # Name heuristics
        if any(k in name for k in ("str", "text", "word")):
            return _string_generator
        if any(k in name for k in ("dict", "map", "table")):
            return _dict_generator
        if any(k in name for k in ("matrix", "grid", "board")):
            return _matrix_generator
        if name in ("n", "k", "num", "count", "size"):
            return _int_generator

    except (ValueError, TypeError):
        pass

    return _list_generator


# ---------------------------------------------------------------------------
# Logarithm sizes — well-spaced to expose growth
# ---------------------------------------------------------------------------

def default_sizes(min_n: int = 10, steps: int = 15) -> List[int]:
    """
    Return `steps` geometrically-spaced sizes starting at min_n,
    each roughly 1.6× the previous (good range: ~10 → ~50 000).
    """
    ratio = 1.6
    sizes = []
    n = float(min_n)
    for _ in range(steps):
        sizes.append(max(1, int(round(n))))
        n *= ratio
    return sorted(set(sizes))


# ---------------------------------------------------------------------------
# Least-squares curve fitting (no scipy needed)
# ---------------------------------------------------------------------------

def fit_complexity(
    sizes: List[int],
    times: List[float],
) -> Tuple[ComplexityClass, float]:
    """
    For each known complexity class, fit a single scale factor a via
    least-squares ( a = Σ(y·f) / Σ(f²) ) and compute R².
    Return the class with the highest R².
    """
    y = times
    n_vals = sizes

    best_cls = COMPLEXITY_CLASSES[2]  # O(n) as fallback
    best_r2 = -math.inf

    for cls in COMPLEXITY_CLASSES:
        f = [cls.fn(n) for n in n_vals]
        sum_ff = sum(fi * fi for fi in f)
        if sum_ff < 1e-30:
            continue
        a = sum(yi * fi for yi, fi in zip(y, f)) / sum_ff
        if a <= 0:
            continue
        y_pred = [a * fi for fi in f]
        r2 = r_squared(y, y_pred)
        if r2 > best_r2:
            best_r2 = r2
            best_cls = cls

    return best_cls, max(best_r2, 0.0)


def r_squared(y_actual: List[float], y_predicted: List[float]) -> float:
    mean_y = sum(y_actual) / len(y_actual)
    ss_tot = sum((yi - mean_y) ** 2 for yi in y_actual)
    ss_res = sum((yi - yp) ** 2 for yi, yp in zip(y_actual, y_predicted))
    if ss_tot < 1e-30:
        return 1.0
    return 1.0 - ss_res / ss_tot


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

COMPLEXITY_EMOJI = {
    "O(1)":       "🟢",
    "O(log n)":   "🟢",
    "O(n)":       "🟡",
    "O(n log n)": "🟡",
    "O(n²)":      "🔴",
    "O(n³)":      "🔴",
    "O(n⁴)":      "💀",
    "O(2ⁿ)":      "💀",
}

def emoji_for(notation: str) -> str:
    return COMPLEXITY_EMOJI.get(notation, "❓")
