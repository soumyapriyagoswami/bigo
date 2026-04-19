"""
analyzer.py — Public API for bigo.

    from bigo import analyze
    result = analyze(my_func)
    print(result)
"""

from __future__ import annotations

import sys
from typing import Callable, List, Optional, Any

from .models import AnalysisResult
from .runner import measure, OUTER_REPEATS, TIME_BUDGET_SECONDS, TOTAL_BUDGET_SECONDS
from .utils import (
    fit_complexity,
    sniff_generator,
    default_sizes,
    emoji_for,
)


def analyze(
    func: Callable,
    *,
    input_generator: Optional[Callable[[int], Any]] = None,
    sizes: Optional[List[int]] = None,
    repeat: int = OUTER_REPEATS,
    time_budget: float = TIME_BUDGET_SECONDS,
    total_budget: float = TOTAL_BUDGET_SECONDS,
    verbose: bool = False,
    print_result: bool = True,
) -> AnalysisResult:
    """
    Empirically estimate the time complexity of *func*.

    Parameters
    ----------
    func             : The callable to analyse.
    input_generator  : ``f(n) -> arg`` to build inputs of size n.
                       Auto-detected from type annotations / param names if omitted.
    sizes            : List of n values to test.  Defaults to 15 log-spaced sizes.
    repeat           : Number of independent timing runs per size (default 7).
    time_budget      : Per-run abort threshold in seconds (default 3 s).
    total_budget     : Total wall-clock limit in seconds (default 30 s).
    verbose          : Print live timing lines.
    print_result     : Pretty-print the summary table (default True).

    Returns
    -------
    AnalysisResult
    """
    # --- Input generator ---------------------------------------------------
    gen = input_generator or sniff_generator(func)

    # --- Sizes -------------------------------------------------------------
    ns = sizes or default_sizes()

    # --- Measure -----------------------------------------------------------
    if verbose:
        print(f"\n[bigo] Analysing '{func.__name__}' …")

    used_sizes, avg_times, raw_times, inner_loops = measure(
        func=func,
        sizes=ns,
        generator=gen,
        outer_repeats=repeat,
        time_budget=time_budget,
        total_budget=total_budget,
        verbose=verbose,
    )

    if len(used_sizes) < 3:
        raise RuntimeError(
            f"[bigo] Only {len(used_sizes)} usable data points — cannot fit a curve. "
            "Try a slower function or reduce 'time_budget'."
        )

    # --- Fit ---------------------------------------------------------------
    complexity_cls, r2 = fit_complexity(used_sizes, avg_times)

    result = AnalysisResult(
        func_name    = func.__name__,
        complexity   = complexity_cls,
        r_squared    = r2,
        input_sizes  = used_sizes,
        runtimes     = avg_times,
        raw_runtimes = raw_times,
        repeats_used = inner_loops,
    )

    # --- Print -------------------------------------------------------------
    if print_result:
        _pretty_print(result)

    return result


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def _pretty_print(r: AnalysisResult) -> None:
    em = emoji_for(r.complexity.notation)
    sep = "─" * 52
    print(f"\n{sep}")
    print(f"  bigo analysis  ·  {r.func_name}()")
    print(sep)
    print(f"  {em}  Estimated complexity : {r.complexity.notation}  ({r.complexity.name})")
    print(f"     R² fit score         : {r.r_squared:.4f}  [{r.confidence} confidence]")
    print(f"     Data points used     : {len(r.input_sizes)}")
    print(f"\n  {'n':>10}  {'avg time':>12}  {'inner loops':>12}")
    print(f"  {'─'*10}  {'─'*12}  {'─'*12}")
    for n, t, loops in zip(r.input_sizes, r.runtimes, r.repeats_used):
        ms = t * 1000
        unit = f"{ms:.4f} ms"
        print(f"  {n:>10,}  {unit:>12}  {loops:>12,}")
    print(f"{sep}\n")
