import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# graph3.py
# Checks a prediction: how many digits does cancellation destroy?
#   predicted loss = log10(largest term / |true answer|)
#   measured loss  = 16 - (correct digits the plain series actually gave)
# Needs exp_lab.py in the same folder.

import math
import matplotlib.pyplot as plt
from mpmath import mp, mpf, exp as mp_exp
from exp_lab import exp_series, relative_error

mp.dps = 50          # same 50-digit precision as exp_lab

N_TERMS = 200        # plenty of terms, so truncation error is not the problem

# x from -25 to 5 (negative = cancellation, positive = no problem)
x_values = list(range(-25, 6))

predicted = []       # what the formula says we should lose
measured = []        # what we really lost

for x in x_values:
    # --- run the plain series ---
    total, largest_term = exp_series(x, N_TERMS)

    # --- the true answer, to 50 digits, as a normal float ---
    true_value = float(mp_exp(mpf(x)))

    # --- prediction: digits lost = log10(largest term / true answer) ---
    # max(..., 0) because we can't lose a negative number of digits
    pred = max(0.0, math.log10(largest_term / true_value))
    predicted.append(pred)

    # --- measurement ---
    error = relative_error(total, x)
    if error == 0:
        correct_digits = 16.0
    else:
        # -log10(error) = number of correct digits; keep it between 0 and 16
        correct_digits = max(0.0, min(16.0, -math.log10(error)))
    measured.append(16.0 - correct_digits)

# ---------------------------------------------------------------
# Plot: predicted (line) vs measured (dots)
# ---------------------------------------------------------------
plt.plot(x_values, predicted, label="predicted: log10(largest term / answer)")
plt.plot(x_values, measured, "o", label="measured (16 - correct digits)")

# A computer only keeps about 16 digits, so you can't lose more than 16
plt.axhline(16, color="gray", linestyle=":", label="all 16 digits gone")

plt.xlabel("x")
plt.ylabel("digits lost")
plt.title("Digits lost to cancellation: prediction vs reality")
plt.legend()
plt.grid(True)

plt.savefig("images/graph3.png", dpi=110)   # save BEFORE show
plt.show()