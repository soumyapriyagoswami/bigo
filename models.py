"""
Complexity models and result types for bigo.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import math


# ---------------------------------------------------------------------------
# Complexity class registry
# ---------------------------------------------------------------------------

class ComplexityClass:
    """Describes a Big-O complexity class with a fitting function."""

    def __init__(self, name: str, notation: str, fn, rank: int):
        self.name = name          # human-readable: "Linear"
        self.notation = notation  # "O(n)"
        self.fn = fn              # f(n) -> predicted value (for curve-fitting)
        self.rank = rank          # lower = better / simpler

    def __repr__(self):
        return f"ComplexityClass({self.notation})"


def _safe_log(n):
    return math.log(n) if n > 1 else 1e-9

def _safe_nlogn(n):
    return n * math.log(n) if n > 1 else n * 1e-9


COMPLEXITY_CLASSES: List[ComplexityClass] = [
    ComplexityClass("Constant",        "O(1)",       lambda n: 1,              0),
    ComplexityClass("Logarithmic",     "O(log n)",   _safe_log,               1),
    ComplexityClass("Linear",          "O(n)",       lambda n: n,              2),
    ComplexityClass("Linearithmic",    "O(n log n)", _safe_nlogn,             3),
    ComplexityClass("Quadratic",       "O(n²)",      lambda n: n ** 2,         4),
    ComplexityClass("Cubic",           "O(n³)",      lambda n: n ** 3,         5),
    ComplexityClass("Polynomial(n^4)", "O(n⁴)",      lambda n: n ** 4,         6),
    ComplexityClass("Exponential",     "O(2ⁿ)",      lambda n: 2 ** min(n, 60),7),
]


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class AnalysisResult:
    """Holds the result of a `bigo.analyze()` call."""

    func_name: str
    complexity: ComplexityClass
    r_squared: float
    input_sizes: List[int]
    runtimes: List[float]          # seconds, averaged over repeats
    raw_runtimes: List[List[float]] # per-repeat measurements
    repeats_used: List[int]        # how many inner-loops per size
    confidence: str = field(init=False)

    def __post_init__(self):
        if self.r_squared >= 0.99:
            self.confidence = "high"
        elif self.r_squared >= 0.95:
            self.confidence = "medium"
        else:
            self.confidence = "low"

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        lines = [
            "",
            f"  Function  : {self.func_name}",
            f"  Complexity: {self.complexity.notation}  ({self.complexity.name})",
            f"  R²        : {self.r_squared:.4f}  [{self.confidence} confidence]",
            "",
            f"  {'n':>10}  {'time (ms)':>12}  {'repeats':>8}",
            f"  {'-'*10}  {'-'*12}  {'-'*8}",
        ]
        for n, t, r in zip(self.input_sizes, self.runtimes, self.repeats_used):
            lines.append(f"  {n:>10,}  {t*1000:>12.4f}  {r:>8,}")
        lines.append("")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"AnalysisResult(func={self.func_name!r}, "
            f"complexity={self.complexity.notation!r}, "
            f"r2={self.r_squared:.4f})"
        )
