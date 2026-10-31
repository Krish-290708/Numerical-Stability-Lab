# Black-Scholes prices for European call and put options.
# Built on your own pieces:
#   exp_horner_reciprocal  (exp_lab.py, Phase 1)  for e^(-r*T)
#   normal_cdf_stable      (normal_lab.py, Stage 2) for Phi
# Only ln and the square root come from Python's math module.

import math
from exp_lab import exp_horner_reciprocal
from normal_lab import normal_cdf_stable

# Terms for e^(-r*T). r*T is small in practice, so 400 is far more than enough.
EXP_TERMS = 400


# 1. INPUT CHECK

def check_inputs(S, K, T, sigma):
    """Stop early, with a clear message, if an input makes no sense."""
    if S <= 0 or K <= 0:
        raise ValueError("S and K must be positive")
    if T <= 0:
        raise ValueError("T (years to expiry) must be positive")
    if sigma <= 0:
        raise ValueError("sigma (volatility) must be positive")


# 2. d1 AND d2

def d1_d2(S, K, T, r, sigma):
    """The two numbers Black-Scholes feeds into Phi.

    d1 = ( ln(S/K) + (r + sigma^2/2) * T ) / ( sigma * sqrt(T) )
    d2 = d1 - sigma * sqrt(T)
    """
    check_inputs(S, K, T, sigma)

    top = math.log(S / K) + (r + sigma * sigma / 2) * T
    bottom = sigma * math.sqrt(T)

    d1 = top / bottom
    d2 = d1 - bottom          # bottom is sigma * sqrt(T)
    return d1, d2             # two values returned together (a tuple)


# 3. CALL PRICE

def call_price(S, K, T, r, sigma):
    """Price of a call: the right to BUY the stock at K on expiry.

    Call = S * Phi(d1) - K * e^(-rT) * Phi(d2)
    """
    d1, d2 = d1_d2(S, K, T, r, sigma)               # unpack the tuple
    discount = exp_horner_reciprocal(-r * T, EXP_TERMS)    # e^(-rT)

    return S * normal_cdf_stable(d1) - K * discount * normal_cdf_stable(d2)


# 4. PUT PRICE

def put_price(S, K, T, r, sigma):
    """Price of a put: the right to SELL the stock at K on expiry.

    Put = K * e^(-rT) * Phi(-d2) - S * Phi(-d1)
    (the mirror image of the call formula)
    """
    d1, d2 = d1_d2(S, K, T, r, sigma)
    discount = exp_horner_reciprocal(-r * T, EXP_TERMS)    # e^(-rT)

    return K * discount * normal_cdf_stable(-d2) - S * normal_cdf_stable(-d1)