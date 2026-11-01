import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from mpmath import mp, mpf, ncdf, log, sqrt, exp
from Black_Scholes_lab import call_price, put_price

mp.dps = 60

def reference(S, K, T, r, sigma):
    """Call and put at 60 digits (mpmath), the 'true' answer."""
    S, K, T, r, sigma = map(mpf, (S, K, T, r, sigma))
    d1 = (log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    call = S * ncdf(d1) - K * exp(-r * T) * ncdf(d2)
    put = K * exp(-r * T) * ncdf(-d2) - S * ncdf(-d1)
    return call, put

cases = [
    (100, 100, 1,    0.05, 0.20),   # at the money (classic check case)
    (100,  90, 0.5,  0.03, 0.25),   # in the money
    (100, 110, 1,    0.05, 0.20),   # out of the money
    (100, 150, 0.5,  0.05, 0.20),   # far out of the money
    (100, 200, 0.25, 0.05, 0.20),   # very far out of the money
    (100, 300, 0.25, 0.05, 0.20),   # absurdly far out of the money
]

print(f"{'S':>5}{'K':>5}{'T':>6}{'call':>13}{'call err':>11}{'put':>13}{'put err':>11}{'parity gap':>12}")
for S, K, T, r, sigma in cases:
    c = call_price(S, K, T, r, sigma)
    p = put_price(S, K, T, r, sigma)
    ref_c, ref_p = reference(S, K, T, r, sigma)
    c_err = float(abs((mpf(c) - ref_c) / ref_c))
    p_err = float(abs((mpf(p) - ref_p) / ref_p))
    # put-call parity: call - put should equal S - K*e^(-rT)
    gap = abs((c - p) - (S - K * math.exp(-r * T)))
    print(f"{S:>5}{K:>5}{T:>6}{c:>13.6g}{c_err:>11.1e}{p:>13.6g}{p_err:>11.1e}{gap:>12.1e}")

from Black_Scholes_lab import call_price, put_price
print(call_price(100, 100, 1, 0.05, 0.2))   # 10.4506...
print(put_price(100, 100, 1, 0.05, 0.2))    # 5.5735...