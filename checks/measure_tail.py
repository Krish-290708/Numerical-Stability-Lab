import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from mpmath import mp, mpf, ncdf
from normal_lab import normal_cdf

mp.dps = 60

print(f"{'x':>5}{'Phi(x) true':>16}{'relative error':>18}{'digits lost':>13}")
for x in [-1, -3, -5, -6, -7, -8, -10]:
    true = ncdf(mpf(x))
    value = normal_cdf(x, 400)
    error = float(abs((mpf(value) - true) / true))
    lost = max(0.0, 16 + math.log10(error))
    print(f"{x:>5}{float(true):>16.3e}{error:>18.1e}{lost:>13.1f}")