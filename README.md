# bigo-time — Auto Time Complexity Estimator

[![PyPI version](https://img.shields.io/pypi/v/bigo-time)](https://pypi.org/project/bigo-time/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Zero dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](#)

> **One function call. Instant Big-O estimate.** No static analysis, no AST tricks — pure empirical measurement.
---

## Interactive playground

Open **[demo.html](./demo.html)** in your browser for a live visual playground — no Python needed.

- 6 categories: sorting, searching, DP, strings, graph, tricky
- Runtime growth curve animates point-by-point as analysis runs
- View source code, architecture diagram, and per-size stats
- **Custom fn tab** — paste your own function for an instant browser estimate

```bash
open demo.html       # macOS
xdg-open demo.html   # Linux
start demo.html      # Windows
```

---

```python
from bigo_time import analyze

analyze(my_function)
```

```
────────────────────────────────────────────────────
  bigo analysis  ·  my_function()
────────────────────────────────────────────────────
  🟡  Estimated complexity : O(n log n)  (Linearithmic)
     R² fit score         : 0.9994  [high confidence]
     Data points used     : 14

           n      avg time   inner loops
  ──────────  ────────────  ────────────
          10    0.0014 ms        10,000
          16    0.0023 ms        10,000
          ...
      32,768    1.4821 ms             1
────────────────────────────────────────────────────
```

---

## How it works

Instead of analysing source code (which is hard and often wrong), `bigo-time`:

1. **Generates inputs** of geometrically-increasing sizes (`n ≈ 10 → 50 000`)
2. **Measures runtime** for each size — intelligently averaging out noise
3. **Fits known curves** (`O(1)`, `O(log n)`, `O(n)`, `O(n log n)`, `O(n²)`, `O(n³)`, `O(2ⁿ)`) via least-squares
4. **Returns the best fit** with an R² confidence score

### Problems solved

| Problem | Solution |
|---|---|
| CPU noise & variance | Average 7 independent runs; trim min/max outliers |
| Small-n bias | 15 log-spaced sizes up to ~50 000 |
| Functions too fast to time | Auto-repeat in inner loop; divide elapsed by count |
| Exponential blowup (`2ⁿ`) | Per-run and total wall-clock budget; early stop |

---

## Installation

```bash
pip install bigo-time
```

No dependencies — pure Python stdlib.

---

## Usage

### Basic

```python
from bigo_time import analyze

def my_sort(lst):
    return sorted(lst)

result = analyze(my_sort)
```

### Custom input generator

```python
# Default: list of n ints. Override for your data shape:
analyze(my_sort, input_generator=lambda n: list(range(n, 0, -1)))

# Dict-based function
def count_values(d: dict):
    return len(set(d.values()))

analyze(count_values, input_generator=lambda n: {i: i % 100 for i in range(n)})
```

### Custom sizes

```python
# Probe specific sizes
analyze(my_sort, sizes=[100, 500, 1000, 5000, 10000])
```

### Programmatic access

```python
result = analyze(my_sort, print_result=False)

print(result.complexity.notation)   # "O(n log n)"
print(result.complexity.name)       # "Linearithmic"
print(result.r_squared)             # 0.9994
print(result.confidence)            # "high"
print(result.input_sizes)           # [10, 16, 25, ...]
print(result.runtimes)              # [1.4e-6, 2.3e-6, ...]
```

### Verbose mode

```python
analyze(my_sort, verbose=True)
# → n=      10  inner=10,000  avg=  0.0014 ms  stdev=0.0001 ms
# → n=      16  inner=10,000  avg=  0.0023 ms  stdev=0.0002 ms
# ...
```

---

## API reference

### `analyze(func, *, ...)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `func` | `Callable` | — | Function to analyse |
| `input_generator` | `Callable[[int], Any]` | auto-detected | `f(n)` → input of size n |
| `sizes` | `List[int]` | log-spaced 10→50k | Input sizes to probe |
| `repeat` | `int` | `7` | Outer timing repeats per size |
| `time_budget` | `float` | `3.0` | Per-run abort threshold (seconds) |
| `total_budget` | `float` | `30.0` | Total wall-clock limit (seconds) |
| `verbose` | `bool` | `False` | Print live timing lines |
| `print_result` | `bool` | `True` | Print summary table |

Returns `AnalysisResult`.

### `AnalysisResult`

| Attribute | Type | Description |
|---|---|---|
| `.func_name` | `str` | Name of analysed function |
| `.complexity` | `ComplexityClass` | Best-fit complexity class |
| `.complexity.notation` | `str` | e.g. `"O(n log n)"` |
| `.complexity.name` | `str` | e.g. `"Linearithmic"` |
| `.r_squared` | `float` | Goodness-of-fit (0–1) |
| `.confidence` | `str` | `"high"` / `"medium"` / `"low"` |
| `.input_sizes` | `List[int]` | n values measured |
| `.runtimes` | `List[float]` | Per-call averages (seconds) |

---

## Caveats

- Empirical estimation is **probabilistic**, not exact. Noise, JIT caching, and branch prediction can affect results.
- `O(1)` and `O(log n)` are hard to distinguish — both run very fast.  
- Results reflect **average-case** behaviour on the default input shape. Adversarial inputs may show different complexity.
- For `O(2ⁿ)` functions the early-stop kicks in — you'll get a partial result but the trend is unmistakable.

---

## License

MIT
