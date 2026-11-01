# check_stage5.py - checks for Stage 5 (stable statistics)
import math
import random
from stats_lab import (variance_naive, variance_welford, historical_volatility,
                       logsumexp_naive, logsumexp_stable)

# ---------------------------------------------------------------
# PART 1: variance of 4 numbers that sit far from zero
# ---------------------------------------------------------------
print("PART 1: variance of [offset+4, offset+7, offset+13, offset+16]  (true answer 30)")
print(f"{'offset':>10}{'naive':>20}{'welford':>20}")
for offset in [0, 1e3, 1e6, 1e8, 1e9, 1e10]:
    data = [offset + 4, offset + 7, offset + 13, offset + 16]
    print(f"{offset:>10.0e}{variance_naive(data):>20.6f}{variance_welford(data):>20.6f}")

# ---------------------------------------------------------------
# PART 2: historical volatility from simulated prices
# ---------------------------------------------------------------
print("\nPART 2: historical volatility from 1 year of simulated daily prices")
random.seed(42)                        # same 'random' numbers every run
true_sigma = 0.20
daily_sigma = true_sigma / math.sqrt(252)
prices = [100.0]
for day in range(252):
    # each day: multiply by e^(random move)
    prices.append(prices[-1] * math.exp(random.gauss(0, daily_sigma)))
print(f"  true volatility used to make the prices   {true_sigma:.4f}")
print(f"  estimated from the prices                 {historical_volatility(prices):.4f}")

# ---------------------------------------------------------------
# PART 3: log-sum-exp
# ---------------------------------------------------------------
print("\nPART 3: log(e^a + e^b + ...)")
tests = [
    ("[1, 2, 3]", [1, 2, 3]),
    ("[1000, 1000]", [1000, 1000]),
    ("[-1000, -1000]", [-1000, -1000]),
    ("[1000, 0]", [1000, 0]),
]
print(f"{'values':<18}{'naive':>22}{'stable':>22}")
for name, values in tests:
    try:
        naive = f"{logsumexp_naive(values):.10f}"
    except (OverflowError, ValueError):
        naive = "ERROR"
    stable = logsumexp_stable(values)
    print(f"{name:<18}{naive:>22}{stable:>22.10f}")