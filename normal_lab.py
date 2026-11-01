# The standard normal distribution:
#   normal_pdf          height of the bell curve
#   normal_cdf          Phi(x) from a series (accurate near zero)
#   upper_tail          tail probability from a continued fraction (accurate far out)
#   normal_cdf_stable   picks the right method for each x
# Needs exp_lab.py in the same folder.

import math
from exp_lab import exp_horner_reciprocal

# SETTINGS

# Terms used for e^(-x*x/2). For x = -20 the power is -200, and e^200 needs
# hundreds of terms before the series settles, so 400 is safe up to |x| = 20.
PDF_TERMS = 400


# 1. THE BELL CURVE (pdf)

def normal_pdf(x):
    """Height of the standard bell curve at x."""
    value = exp_horner_reciprocal(-x * x / 2, PDF_TERMS)   # e^(-x*x/2)
    return value / math.sqrt(2 * math.pi)


# 2. Phi(x) FROM A SERIES  (Stage 1)

def normal_cdf(x, n):
    """Phi(x) using n terms of the series.

    Phi(x) = 0.5 + pdf(x) * ( x + x^3/3 + x^5/(3*5) + x^7/(3*5*7) + ... )
    Each term is the previous term times x*x / (2k+1).
    Accurate for x from about -1.5 up; loses digits for very negative x.
    """
    term = x          # first term of the bracket
    total = x         # running total of the bracket

    for k in range(1, n + 1):
        term = term * x * x / (2 * k + 1)   # build next term from the last one
        total = total + term

    return 0.5 + normal_pdf(x) * total


# 3. THE TAIL FROM A CONTINUED FRACTION  (Stage 2)

def upper_tail(x, depth):
    """P(Z > x) for POSITIVE x. By symmetry this equals Phi(-x).

    Q(x) = pdf(x) / ( x + 1/( x + 2/( x + 3/( x + ... ))) )
    Evaluated from the bottom up. Only adds and divides positive numbers,
    so nothing cancels. Needs depth ~ 200 to be accurate for x >= 1.5.
    """
    f = x                                # innermost piece
    for k in range(depth, 0, -1):        # k = depth, depth-1, ..., 1
        f = x + k / f                    # wrap one more layer around it
    return normal_pdf(x) / f


# 4. THE FINAL, STABLE Phi(x)  (Stage 2)

def normal_cdf_stable(x):
    """Phi(x), accurate to about 1e-16 for x between -20 and 8.3 (and beyond)."""
    # Far on the right, Phi is 1 minus something below 1e-16: a float cannot
    # tell it apart from 1.0, so 1.0 is already the best possible answer.
    if x > 8.3:
        return 1.0

    # Far on the left, e^(-x*x/2) needs more terms than PDF_TERMS gives.
    # An honest error is better than a plausible wrong number.
    if x < -20:
        raise ValueError("x below -20 is outside the supported range")

    # Near zero and on the right: the series has no cancellation problem.
    if x >= -1.5:
        return normal_cdf(x, 400)

    # In the negative tail: compute the tail directly (no subtraction).
    return upper_tail(-x, 200)
    
   

