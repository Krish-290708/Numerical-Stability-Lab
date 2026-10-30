'''
Numerical Stability Lab - Phase 1
Compute e^x using different methods, compare each one against a
very precise reference, and find where they break.
'''

from mpmath import mp, mpf, exp as mp_exp #mpmath is a library for numerical computations with arbitrary precision
mp.dps = 50  # set precision to 50 decimal places
from matplotlib import pyplot as plt

from exp_lab import exp_series, exp_reciprocal, exp_horner, exp_range_reduction

x=float(input("Enter a value for x: "))
n=int(input("Enter the number of terms to use in the Taylor series: "))

print("=" * 50)
print("   NUMERICAL STABILITY LAB")
print("=" * 50)

total, largest_term = exp_series(x,n)
print(f"The largest absolute term in the Taylor series is: {largest_term}")

true = mp_exp(mpf(x))  #this line calculates the true value of e^x using the mpmath library's exp function, which computes the exponential of a given number with arbitrary precision. The result is stored in the variable true, which will be used later to compare against the Taylor series approximation.
error = float(abs((mpf(total) - true)/true))  # #mpf utisizes mpmath's 50 decimal places instead of the computer's 16 decimal places which gets the calc more accurate. Dividing by the true value gives us the relative error instead of the absolute error.

print("\n" + "-" * 50)
print("PLAIN TAYLOR SERIES")
print("-" * 50)

print(f"Taylor series approximation of e^{x} with {n} terms: {total}")
print(f"True value of e^{x}: {true}")
print(f"Relative error: {error}")

print("\n" + "-" * 50)
print("DIAGNOSIS")
print("-" * 50)

TOLERANCE = 1e-12            # error below this counts as "accurate"

if error <= TOLERANCE:                     
    print("Plain series is accurate.")
else:
    print("Plain series FAILED.")
    print(f"Largest term / answer = {largest_term/abs(total):.2e}")
    cancelling = total == 0 or largest_term/abs(total) > 10000       

    if cancelling:
        print("Reason: cancellation. Trying the reciprocal trick.")

        print("\n" + "-" * 50)
        print("RECIPROCAL TRICK")
        print("-" * 50)

        recip = exp_reciprocal(x, n)
        recip_error = float(abs((mpf(recip) - true) / true))
        print(f"Reciprocal trick: {recip}   (relative error {recip_error:.2e})")
        if recip_error < TOLERANCE:
            print("Fixed.")
        else:
            print("Still inaccurate: too few terms. Try a larger n.")
    else:
        print("Reason: you stopped too early. Use more terms.")
    

#Find error for each term in the Taylor series and explain find where the error stops improving and starts to diverge from the true value. This is important because it helps us understand the limitations of the Taylor series approximation and when it becomes unreliable.
error_list = []  #this line initializes an empty list called error_list, which will be used to store the absolute errors for each term in the Taylor series approximation of e^x. The purpose of this list is to track how the error changes as more terms are added to the approximation, allowing us to analyze the convergence behavior and identify when the approximation starts to diverge from the true value.
for k in range(1, n + 1):
    term = 1.0
    total = 1.0
    for j in range(1, k + 1):
        term *= x / j
        total += term
    error = float(abs((mpf(total) - true)/true)) #mpf utisizes mpmath's 50 decimal places instead of the computer's 16 decimal places which gets the calc more accurate. Dividing by the true value gives us the relative error instead of the absolute error.
    error_list.append(mpf(error))

print("\n" + "-" * 50)
print("ERROR AS TERMS ARE ADDED")
print("-" * 50)

print("\n Error list for each term in the Taylor series: ")
print(*error_list, sep="\n")

best = error_list.index(min(error_list)) + 1             # min(error_list) finds the smallest error anywhere in the list. .index(...) finds that error’s position in the list. + 1 is needed because lists start counting at 0, while term numbers start at 1. The first entry is the error after 1 term.
print(f"\nSmallest error: {min(error_list)}, reached at term {best}")

clean = []
for e in error_list:
    clean.append(max(e, 1e-17))  #the log of 0 is undefined. so if any error in the list is 0 then it shall be placed just 1e-16 

plt.semilogy(range(1, n + 1), clean)
plt.xlabel('Number of Terms in Taylor Series') 
plt.ylabel('Relative Error (log scale)')
plt.title(f'Error in Taylor Series Approximation of e^{x}')
plt.show()











