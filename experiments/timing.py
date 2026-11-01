import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import statistics      # gives us the median (the middle value of a list)
import timeit          # Python's built-in stopwatch for short pieces of code

from exp_lab import exp_series, exp_reciprocal, exp_range_reduction, exp_horner, exp_kahan

# The five methods, each with a label for printing.
methods = {
    "plain series": exp_series,
    "reciprocal": exp_reciprocal,
    "range reduction": exp_range_reduction,
    "horner": exp_horner,
    "kahan": exp_kahan,
}

x, n = 10, 100     # the input used for every method (same for all = fair comparison)
NUMBER = 1000      # how many times to run the method inside ONE measurement
REPEAT = 15        # how many measurements to take for each method

print("Time for ONE call, in microseconds (millionths of a second)")
print(f"{'method':<18}{'median':>10}{'fastest':>10}{'slowest':>10}")

for name, method in methods.items():
    # Run the method NUMBER times, and do that REPEAT times.
    # This gives a list of REPEAT totals, one per measurement.
    # (lambda: method(x, n) is a tiny function that makes one call; timeit needs it.)
    totals = timeit.repeat(lambda: method(x, n), number=NUMBER, repeat=REPEAT)

    # Each total covers NUMBER calls. Divide to get one call, then
    # multiply by 1,000,000 to turn seconds into microseconds.
    per_call = [t / NUMBER * 1_000_000 for t in totals]

    # Middle value = typical speed. Smallest and largest show how steady it is.
    median = statistics.median(per_call)
    fastest = min(per_call)
    slowest = max(per_call)

    # <18 and >10 line the columns up; .2f shows 2 decimal places.
    print(f"{name:<18}{median:>10.2f}{fastest:>10.2f}{slowest:>10.2f}")