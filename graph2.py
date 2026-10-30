# graph2.py
# Draws: relative error vs number of terms, for several values of x.
# Needs exp_lab.py in the same folder (it uses your functions).

import matplotlib.pyplot as plt
from exp_lab import exp_series, exp_horner_reciprocal, relative_error

# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------
# x = 10  -> healthy case (all terms positive, no cancellation)
# x = -10 -> mild cancellation
# x = -20 -> severe cancellation
x_values = [10, -10, -20]

# Numbers of terms to try: 1, 2, 3, ... 100
ns = list(range(1, 101))

# ---------------------------------------------------------------
# Step 1: plain series, one line per x
# ---------------------------------------------------------------
for x in x_values:
    errors = []                       # fresh empty list for each x

    for n in ns:
        # exp_series returns TWO things (total, largest_term); we only want total
        result = exp_series(x, n)[0]

        # How wrong is it compared with the 50-digit true value?
        error = relative_error(result, x)

        # The log axis cannot show 0, so raise tiny/zero errors to 1e-17
        errors.append(max(error, 1e-17))

    # Draw this x's line: number of terms on the horizontal axis
    plt.plot(ns, errors, label=f"plain series, x = {x}")

# ---------------------------------------------------------------
# Step 2: the fixed method for x = -20, as a dashed comparison line
# ---------------------------------------------------------------
# Same loop written as a list comprehension (one line instead of five)
fixed_errors = [
    max(relative_error(exp_horner_reciprocal(-20, n), -20), 1e-17)
    for n in ns
]
plt.plot(ns, fixed_errors, linestyle="--", label="horner + reciprocal, x = -20")

# ---------------------------------------------------------------
# Step 3: make the graph readable
# ---------------------------------------------------------------
plt.yscale("log")                      # errors span 1e-16 up to 1e16
plt.xlabel("number of terms")
plt.ylabel("relative error (log scale)")
plt.title("Error vs number of terms")
plt.legend()
plt.grid(True)

# ---------------------------------------------------------------
# Step 4: save and show
# ---------------------------------------------------------------
# Save BEFORE show(): show() clears the figure, so a later save is blank.
plt.savefig("graph2.png", dpi=110)
plt.show()