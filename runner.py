"""
runner.py — Smart measurement engine for bigo.

Solves:
  1. Noise & Variance       → average over `outer_repeats` independent runs
  2. Small Input Bias       → auto-scale sizes until runtime is significant
  3. Fast Functions Problem → auto-repeat inside a tight loop, divide after
  4. Exponential Blowup     → early-stop when time budget is exceeded
"""

from __future__ import annotations

import time
import gc
import statistics
from typing import Callable, List, Tuple, Any, Optional

# Tunables (module-level so advanced users can override before calling analyze)
MIN_MEASURABLE_SECONDS = 5e-4   # 0.5 ms — below this we loop more
MAX_INNER_LOOPS        = 10_000 # cap inner auto-repeat
OUTER_REPEATS          = 7      # independent timing runs per (n, inner)
TIME_BUDGET_SECONDS    = 3.0    # abort a size if a single run takes this long
TOTAL_BUDGET_SECONDS   = 30.0   # total wall-clock limit for the whole sweep


def _time_one(func: Callable, arg: Any, inner: int) -> float:
    """
    Time `inner` back-to-back calls of func(arg).
    Disables GC during the measurement for lower variance.
    Returns *per-call* elapsed seconds.
    """
    gc.disable()
    try:
        t0 = time.perf_counter()
        for _ in range(inner):
            func(arg)
        t1 = time.perf_counter()
    finally:
        gc.enable()
    return (t1 - t0) / inner


def _calibrate_inner(func: Callable, arg: Any) -> int:
    """
    Find the smallest inner-loop count such that the total measurement
    is >= MIN_MEASURABLE_SECONDS.  Caps at MAX_INNER_LOOPS.
    """
    inner = 1
    while inner <= MAX_INNER_LOOPS:
        elapsed = _time_one(func, arg, inner) * inner  # total, not per-call
        if elapsed >= MIN_MEASURABLE_SECONDS:
            return inner
        inner = min(inner * 4, MAX_INNER_LOOPS)
    return MAX_INNER_LOOPS


def measure(
    func: Callable,
    sizes: List[int],
    generator: Callable[[int], Any],
    outer_repeats: int = OUTER_REPEATS,
    time_budget: float = TIME_BUDGET_SECONDS,
    total_budget: float = TOTAL_BUDGET_SECONDS,
    verbose: bool = False,
) -> Tuple[List[int], List[float], List[List[float]], List[int]]:
    """
    Measure `func` at each size in `sizes`.

    Returns
    -------
    used_sizes   : input sizes actually measured (early-stop may shorten list)
    avg_times    : averaged per-call runtime in seconds
    raw_times    : raw[i] = list of outer_repeats per-call measurements for sizes[i]
    inner_loops  : inner repeat counts used per size
    """
    used_sizes: List[int] = []
    avg_times:  List[float] = []
    raw_times:  List[List[float]] = []
    inner_loops: List[int] = []

    wall_start = time.perf_counter()

    for n in sizes:
        # Wall-clock budget check
        if time.perf_counter() - wall_start > total_budget:
            if verbose:
                print(f"  [bigo] Total budget {total_budget}s reached, stopping at n={n}")
            break

        arg = generator(n)
        inner = _calibrate_inner(func, arg)

        runs: List[float] = []
        blew_up = False

        for _ in range(outer_repeats):
            t = _time_one(func, arg, inner)
            runs.append(t)
            if t > time_budget:
                blew_up = True
                break

        if blew_up:
            if verbose:
                print(f"  [bigo] Exponential blowup at n={n} ({runs[-1]*1000:.1f} ms), stopping.")
            break

        # Trim outliers: drop highest and lowest if we have >=5 runs
        trimmed = _trim(runs)
        avg = statistics.mean(trimmed)

        if verbose:
            print(f"  n={n:>8,}  inner={inner:>6,}  avg={avg*1000:8.4f} ms"
                  f"  stdev={statistics.stdev(trimmed)*1000:.4f} ms" if len(trimmed) > 1 else
                  f"  n={n:>8,}  inner={inner:>6,}  avg={avg*1000:8.4f} ms")

        used_sizes.append(n)
        avg_times.append(avg)
        raw_times.append(runs)
        inner_loops.append(inner)

    return used_sizes, avg_times, raw_times, inner_loops


def _trim(runs: List[float]) -> List[float]:
    """Drop min and max for >= 5 samples to reduce outlier impact."""
    if len(runs) >= 5:
        s = sorted(runs)
        return s[1:-1]
    return runs
