# graph4.py
# Draws: how long each method takes (microseconds per call).
# Reads the time_us column of results.csv, which run_experiments.py wrote.

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Step 1: load the data
# ---------------------------------------------------------------
df = pd.read_csv("results.csv")

# ---------------------------------------------------------------
# Step 2: one speed number per method
# ---------------------------------------------------------------
# Each method was timed at 41 values of x (-20 ... 20), and each timing is a
# bit noisy. The MEDIAN across all x ignores the occasional slow outlier.
# groupby("method") makes one group per method; sort_values puts fastest first.
times = df.groupby("method")["time_us"].median().sort_values()

# ---------------------------------------------------------------
# Step 3: draw a bar chart
# ---------------------------------------------------------------
plt.figure(figsize=(8, 4.5))              # a bit wider so the names fit
bars = plt.bar(times.index, times.values)

# Write the number on top of each bar so nobody has to guess
for bar, value in zip(bars, times.values):
    plt.text(bar.get_x() + bar.get_width() / 2,   # centre of the bar
             value,                               # top of the bar
             f"{value:.1f}",                      # e.g. 4.9
             ha="center", va="bottom")

plt.ylabel("time per call (microseconds)")
plt.title("Speed of each method (100 terms, median over x = -20 ... 20)")
plt.xticks(rotation=20, ha="right")       # tilt the names so they don't overlap
plt.grid(True, axis="y")                  # horizontal grid lines only
plt.tight_layout()                        # stop the labels getting cut off

plt.savefig("graph4.png", dpi=110)        # save BEFORE show
plt.show()