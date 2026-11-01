# Numerical Stability Lab

**When correct math gives wrong answers, and how to fix it.**

The Maclaurin series for e^x is exact for every x. But computed in Python
with 100 terms, it returns **6.15e-09 for x = -20, when the true value is
2.06e-09**, almost 200% wrong. This project explains why, predicts the damage
with a formula, and fixes it. Every result is checked against a 50-digit
reference computed with mpmath.

![error vs x](images/graph1.png)

## Key findings
- **Cause:** cancellation. For x = -20 the series adds terms as large as 4.3e7
  to get an answer of 2e-9, which destroys all 16 digits a computer keeps.
- **More terms do not help.** The error flattens at a level set by the size of
  the largest term, not by how many terms you add.
- **The damage is predictable:** digits lost is about
  log10(largest term / |answer|), and the measured loss matches it.
- **What fixes it:** methods that avoid huge alternating terms (reciprocal
  trick, range reduction). Methods that only rearrange or protect the
  additions (Horner, Kahan) do not.
- **Best method:** Horner + reciprocal. Accurate for every x from -20 to 20,
  and about 1.8x faster than the plain series.

## What is inside
- Six methods for computing e^x, compared on accuracy and speed
- A diagnosis rule that tells truncation error from cancellation error
- An interactive explorer: type any x and number of terms, get the answer,
  the error and the diagnosis
- A results table (`results.csv`) with 246 measurements
- Four graphs and 12 automated tests

## Run it
```
pip install mpmath pandas matplotlib pytest
python lab.py               # interactive explorer
python run_experiments.py   # runs all methods, writes results.csv
python graph1.py            # error vs x
python graph2.py            # error vs number of terms
python graph3.py            # digits lost, predicted vs measured
python graph4.py            # speed
python -m pytest            # 46 tests
python pricer.py            # Interactive option calculator
python graphs_phase2.py
```

## Read more
The full write-up with all four graphs is in [report.md](report.md).

## Files
| File | Purpose |
|---|---|
| exp_lab.py | the six methods and the error function |
| lab.py | interactive explorer |
| test_exp_lab.py | automated tests |
| run_experiments.py | experiment runner, writes results.csv |
| timing.py | speed comparison |
| graph1.py to graph4.py | the figures |
|normal_lab.py|
|Black_Scholes_lab.py|
|iv_lab.py|
|stats_lab.py|
|pricer.py|
|graphs_phase2.py|
|test_phase2.py|

## Skills demonstrated
Taylor series and convergence (ratio test), floating-point error analysis,
benchmarking against a high-precision reference, automated testing with
pytest, and data analysis and visualisation with pandas and matplotlib.

## Next
A second phase applies the same ideas to quantitative finance: a normal
CDF built from series, a Black-Scholes option pricer, and implied volatility.

## Phase 2: option pricing and statistics
Phase 2 applies the same numerical thinking to quantitative finance. Everything
is built from scratch and checked against a 60-digit reference.
- Normal CDF from a series, with a continued-fraction fix for the left tail
- Black-Scholes pricer for calls and puts
- Implied volatility solver: Newton's method with a bisection fallback
- Stable statistics: Welford variance, historical volatility, log-sum-exp
- An interactive option calculator (`python pricer.py`)
- 34 more automated tests (46 in total)

Full write-up: [report2.md](report2.md)