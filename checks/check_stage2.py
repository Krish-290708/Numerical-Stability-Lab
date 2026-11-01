import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mpmath import mp, mpf, ncdf
from normal_lab import normal_cdf, normal_cdf_stable

mp.dps = 60
print(f"{'x':>6}{'series error':>16}{'stable error':>16}{'true Phi(x)':>16}")
for x in [-1, -2, -3, -5, -6, -7, -8, -10, -15, -20, 0, 3, 8]:
    true = ncdf(mpf(x))
    e1 = float(abs((mpf(normal_cdf(x, 400)) - true) / true))
    e2 = float(abs((mpf(normal_cdf_stable(x)) - true) / true))
    print(f"{x:>6}{e1:>16.1e}{e2:>16.1e}{float(true):>16.3e}")