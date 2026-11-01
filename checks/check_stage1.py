import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# check_stage1.py - compares normal_cdf with a 50-digit reference
from mpmath import mp, mpf, ncdf
from normal_lab import normal_cdf

mp.dps = 50

x_values = [0.5, 1, 1.96, 3, -1, -3]
n_values = [5, 10, 20, 40]

print(f"{'x':>6}{'terms':>7}{'Phi(x)':>18}{'relative error':>18}")
for x in x_values:
    true = ncdf(mpf(x))                  # mpmath's normal CDF, 50 digits
    for n in n_values:
        value = normal_cdf(x, n)
        error = float(abs((mpf(value) - true) / true))
        print(f"{x:>6}{n:>7}{value:>18.12f}{error:>18.1e}")
    print()