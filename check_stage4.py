# check_stage4.py - round trip: sigma -> price -> implied sigma
from iv_lab import (model_price, vega, implied_vol_bisection,
                    implied_vol_newton, implied_vol)

S, r = 100, 0.05

# (kind, K, T, true sigma)
cases = [
    ("call", 100, 1.0, 0.25),    # at the money: the easy case
    ("call", 110, 0.5, 0.30),    # slightly out of the money
    ("put",   90, 0.25, 0.40),   # out of the money put
    ("call", 100, 2.0, 0.80),    # high volatility
    ("put",  150, 0.1, 0.40),    # far in the money, short expiry
    ("call",  60, 0.5, 0.40),    # far in the money call
    ("call",  60, 0.5, 0.10),    # price barely depends on sigma
]

print(f"{'case':<24}{'true':>6}{'vega':>10}{'newton':>12}{'steps':>6}"
      f"{'bisection':>12}{'steps':>6}{'combined':>11}{'error':>10}")
for kind, K, T, true_sigma in cases:
    price = model_price(kind, S, K, T, r, true_sigma)
    v = vega(S, K, T, r, true_sigma)

    n_sigma, n_steps = implied_vol_newton(kind, price, S, K, T, r)
    b_sigma, b_steps = implied_vol_bisection(kind, price, S, K, T, r)
    c_sigma, c_steps, method = implied_vol(kind, price, S, K, T, r)

    name = f"{kind} K={K} T={T}"
    n_text = f"{n_sigma:.8f}" if n_sigma is not None else "FAILED"
    print(f"{name:<24}{true_sigma:>6.2f}{v:>10.1e}{n_text:>12}{n_steps:>6}"
          f"{b_sigma:>12.8f}{b_steps:>6}{method:>11}{abs(c_sigma - true_sigma):>10.1e}")

from iv_lab import implied_vol
print(implied_vol("call", 10.4506, 100, 100, 1, 0.05))