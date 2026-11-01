# iv_lab.py
# "IV" = implied volatility. This file runs Black-Scholes BACKWARDS:
# given a market price, find the volatility (sigma) that produces it.
#
# Two ways to search for sigma:
#   bisection  slow (43 steps) but always works
#   newton     fast (about 5 steps) but can fail when the price curve is flat
# implied_vol() tries Newton first and falls back to bisection.
#
# Needs: exp_lab.py, normal_lab.py, bs_lab.py in the same folder.

import math
from exp_lab import exp_horner_reciprocal
from normal_lab import normal_pdf
from Black_Scholes_lab import d1_d2, call_price, put_price, EXP_TERMS


# 1. HELPERS

def model_price(kind, S, K, T, r, sigma):
    """Black-Scholes price of a 'call' or a 'put'."""
    if kind == "call":
        return call_price(S, K, T, r, sigma)
    return put_price(S, K, T, r, sigma)


def price_bounds(kind, S, K, T, r):
    """Cheapest and dearest price an option can possibly have.

    Call: between max(S - K*e^(-rT), 0) and S
    Put:  between max(K*e^(-rT) - S, 0) and K*e^(-rT)
    A market price outside this range has NO implied volatility.
    """
    disc = exp_horner_reciprocal(-r * T, EXP_TERMS)      # e^(-rT)
    if kind == "call":
        return max(S - K * disc, 0.0), S
    return max(K * disc - S, 0.0), K * disc


def vega(S, K, T, r, sigma):
    """How much the price changes per unit of sigma (the slope).

    vega = S * pdf(d1) * sqrt(T)
    Newton's method divides by this, so a tiny vega is dangerous.
    """
    d1, d2 = d1_d2(S, K, T, r, sigma)
    return S * normal_pdf(d1) * math.sqrt(T)


# 2. BISECTION  (slow, safe)

def implied_vol_bisection(kind, market, S, K, T, r,
                          low=0.001, high=5.0, tol=1e-12):
    """Return (sigma, steps).

    The true sigma is somewhere between low and high. Look at the middle:
    if the price there is below the market price, sigma is too small, so
    move 'low' up; otherwise move 'high' down. Each step halves the gap.
    """
    steps = 0
    while high - low > tol:
        mid = (low + high) / 2
        steps = steps + 1

        try:
            too_low = model_price(kind, S, K, T, r, mid) < market
        except ValueError:
            # The pricer refuses extremely tiny sigma (d1, d2 out of range).
            # There the price is essentially its minimum, so it is below market.
            too_low = True

        if too_low:
            low = mid        # sigma is too small: search the upper half
        else:
            high = mid       # sigma is too big: search the lower half

    return (low + high) / 2, steps


# 3. NEWTON'S METHOD  (fast, fragile)

def implied_vol_newton(kind, market, S, K, T, r,
                       guess=0.2, tol=1e-12, max_steps=50):
    """Return (sigma, steps), or (None, steps) if Newton gives up.

    Each step: sigma_new = sigma - (price(sigma) - market) / vega
    It follows the slope of the price curve straight to the answer.
    """
    sigma = guess

    for step in range(1, max_steps + 1):
        try:
            diff = model_price(kind, S, K, T, r, sigma) - market   # how far off
            v = vega(S, K, T, r, sigma)                            # the slope
        except ValueError:
            return None, step            # sigma went somewhere the pricer rejects

        if v < 1e-12:
            return None, step            # curve is flat: step would be enormous

        change = diff / v
        sigma = sigma - change           # the Newton step

        if sigma <= 0:
            return None, step            # jumped to a negative volatility

        if abs(change) < tol:
            return sigma, step           # converged

    return None, max_steps               # did not converge in time


# 4. THE COMBINED SOLVER

def implied_vol(kind, market, S, K, T, r):
    """Return (sigma, steps, method). Newton first, bisection as the backup."""
    # No volatility can produce a price outside these bounds.
    lo, hi = price_bounds(kind, S, K, T, r)
    if not (lo < market < hi):
        raise ValueError("no implied vol: price outside no-arbitrage bounds")

    # Fast attempt
    sigma, steps = implied_vol_newton(kind, market, S, K, T, r)
    if sigma is not None:
        return sigma, steps, "newton"

    # Newton failed: use the method that cannot fail
    sigma, steps = implied_vol_bisection(kind, market, S, K, T, r)
    return sigma, steps, "bisection"