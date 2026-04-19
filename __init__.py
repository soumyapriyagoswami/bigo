"""
bigo — Auto Time Complexity Estimator
======================================

Empirically estimates Big-O time complexity by measuring runtime growth
across input sizes and fitting known complexity curves.

Quick start
-----------
    from bigo import analyze

    def my_sort(lst):
        return sorted(lst)

    result = analyze(my_sort)
    # → O(n log n)

    # Custom generator
    analyze(my_sort, input_generator=lambda n: list(range(n, 0, -1)))

    # Suppress auto-print and inspect programmatically
    result = analyze(my_sort, print_result=False)
    print(result.complexity.notation)   # "O(n log n)"
    print(result.r_squared)             # 0.9997
"""

from .analyzer import analyze
from .models import AnalysisResult, ComplexityClass, COMPLEXITY_CLASSES
from .utils import sniff_generator, default_sizes, fit_complexity
from .runner import measure

__all__ = [
    "analyze",
    "AnalysisResult",
    "ComplexityClass",
    "COMPLEXITY_CLASSES",
    "sniff_generator",
    "default_sizes",
    "fit_complexity",
    "measure",
]

__version__ = "0.1.2"
__author__  = "Soumyapriya Goswami"
