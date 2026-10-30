# graph1.py
# Draws: relative error vs x for every method, using the data in results.csv

import pandas as pd              # reads the CSV into a table
import matplotlib.pyplot as plt  # draws the graph


# Step 1: load the data

# results.csv must be in the same folder as this file.
# Columns: x, method, terms, result, relative_error, correct_digits, time_us
df = pd.read_csv("results.csv")

# Step 2: draw one line per method

# df["method"].unique() gives each method name once:
# "plain series", "reciprocal", "range reduction", ...
for name in df["method"].unique():

    # Keep only the rows that belong to this method
    # (read it as: "rows where the method column equals name")
    rows = df[df["method"] == name]

    # A log axis cannot show 0, and some methods get an error of exactly 0.
    # clip(lower=1e-17) raises any value below 1e-17 up to 1e-17,
    # so those points sit at the bottom of the graph instead of vanishing.
    errors = rows["relative_error"].clip(lower=1e-17)

    # Draw this method's line: x on the horizontal axis, error on the vertical.
    # marker="o" puts a dot on every data point, label=name feeds the legend.
    plt.plot(rows["x"], errors, marker="o", markersize=4, label=name)


# Step 3: make the graph readable

plt.yscale("log")                 # errors range from 1e-16 to 1, so use a log scale
plt.xlabel("x")                   # what the horizontal axis means
plt.ylabel("relative error (log scale)")
plt.title("Error of each method for e^x (100 terms)")
plt.legend()                      # box that says which colour is which method
plt.grid(True)                    # light grid lines to help read values


# Step 4: save and show

# Save BEFORE show(): show() clears the figure, so a save after it is blank.
plt.savefig("graph1.png", dpi=110)
plt.show()