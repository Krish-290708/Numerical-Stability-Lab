import csv         # for writing the spreadsheet file
import math        # for log10
import timeit      # the stopwatch from before

from exp_lab import (exp_series, exp_reciprocal, exp_range_reduction,
                     exp_horner, exp_kahan, exp_horner_reciprocal, relative_error)


def plain_series(x, n):
    return exp_series(x, n)[0]      # exp_series gives two values; keep only the total


# The methods to compare.
methods = {
    "plain series": plain_series,
    "reciprocal": exp_reciprocal,
    "range reduction": exp_range_reduction,
    "horner": exp_horner,
    "kahan": exp_kahan,
    "horner + reciprocal": exp_horner_reciprocal,
}

x_values = range(-20, 21)           # -20, -19, ..., 20
N_TERMS = 100
NUMBER = 1000                       # calls per timing measurement
REPEAT = 7                          # timing measurements per method


def run_all_methods(x):
    """Run every method for this x. Returns one tuple per method:
    (name, result, error, digits, time_us)."""
    rows = []
    for name, method in methods.items():
        result = method(x, N_TERMS)                       # the method's answer
        error = relative_error(result, x)                 # how wrong it is (fraction)
        # How many of the 16 digits are correct: -log10(error), kept between 0 and 16.
        # (An error of exactly 0 would break log10, so call that 16.)
        digits = 16.0 if error == 0 else max(0.0, min(16.0, -math.log10(error)))
        # Fastest of REPEAT measurements, converted to microseconds for ONE call.
        fastest = min(timeit.repeat(lambda: method(x, N_TERMS), number=NUMBER, repeat=REPEAT))
        time_us = fastest / NUMBER * 1_000_000
        rows.append((name, result, error, digits, time_us))
    return rows


# ---------- PART 1: run everything and save it to a CSV file ----------
with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["x", "method", "terms", "result", "relative_error", "correct_digits", "time_us"])
    for x in x_values:
        for name, result, error, digits, time_us in run_all_methods(x):
            writer.writerow([x, name, N_TERMS, result, error, round(digits, 1), round(time_us, 2)])

print("Saved", len(x_values) * len(methods), "rows to results.csv")

# ---------- PART 2: interactive. Type any x, see how every method does ----------
while True:
    text = input("\nEnter any x to compare all methods (or press Enter to quit): ")
    if text == "":
        break
    try:
        x = float(text)
    except ValueError:
        print("Please type a number, like -20 or 3.5")
        continue

    rows = run_all_methods(x)
    rows.sort(key=lambda row: row[3], reverse=True)       # most correct digits first

    print(f"\nRanking for e^{x:g} with {N_TERMS} terms (best first):")
    print(f"{'method':<20}{'digits':>8}{'error':>12}{'time (us)':>12}")
    for name, result, error, digits, time_us in rows:
        print(f"{name:<20}{digits:>8.1f}{error:>12.2e}{time_us:>12.2f}")