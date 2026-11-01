#   1) normal CDF: error vs x
#   2) option prices: error vs strike
#   3) implied volatility: where Newton works and where it fails
#   4) variance: error vs offset

import math
import matplotlib.pyplot as plt
from mpmath import mp, mpf, ncdf, log, sqrt, exp

from normal_lab import normal_cdf, normal_cdf_stable
from Black_Scholes_lab import call_price, put_price
from iv_lab import model_price, implied_vol_newton
from stats_lab import variance_naive, variance_welford

mp.dps = 60            # the 60-digit "true answer" used as the reference
FLOOR = 1e-17          # a log axis cannot show 0, so tiny errors are lifted to this


def rel_error(value, true):
    """Relative error of a float against a high-precision true value."""
    return float(abs((mpf(value) - true) / true))


# GRAPH 1: normal CDF, error vs x

def graph1():
    xs = [i / 4 for i in range(-40, 33)]            # -10 ... 8 in steps of 0.25
    series_err, stable_err = [], []
    for x in xs:
        true = ncdf(mpf(x))
        series_err.append(max(rel_error(normal_cdf(x, 400), true), FLOOR))
        stable_err.append(max(rel_error(normal_cdf_stable(x), true), FLOOR))

    plt.figure(figsize=(8, 4.8))
    plt.plot(xs, series_err, marker="o", markersize=3, label="series only (Stage 1)")
    plt.plot(xs, stable_err, marker="o", markersize=3, linestyle="--",
             label="series + continued fraction (Stage 2)")
    plt.yscale("log")
    plt.xlabel("x")
    plt.ylabel("relative error (log scale)")
    plt.title("Normal CDF: the series loses all its digits in the left tail")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("p2_graph1.png", dpi=110)
    plt.close()


# GRAPH 2: option price error vs strike

def reference_prices(S, K, T, r, sigma):
    """Call and put to 60 digits."""
    S, K, T, r, sigma = map(mpf, (S, K, T, r, sigma))
    d1 = (log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    call = S * ncdf(d1) - K * exp(-r * T) * ncdf(d2)
    put = K * exp(-r * T) * ncdf(-d2) - S * ncdf(-d1)
    return call, put


def graph2():
    S, T, r, sigma = 100, 0.25, 0.05, 0.2
    strikes = list(range(50, 301, 5))
    call_err, put_err = [], []
    for K in strikes:
        ref_call, ref_put = reference_prices(S, K, T, r, sigma)
        call_err.append(max(rel_error(call_price(S, K, T, r, sigma), ref_call), FLOOR))
        put_err.append(max(rel_error(put_price(S, K, T, r, sigma), ref_put), FLOOR))

    plt.figure(figsize=(8, 4.8))
    plt.plot(strikes, call_err, marker="o", markersize=3, label="call price error")
    plt.plot(strikes, put_err, marker="o", markersize=3, linestyle="--", label="put price error")
    plt.yscale("log")
    plt.xlabel("strike price K  (stock price S = 100)")
    plt.ylabel("relative error (log scale)")
    plt.title("Option price accuracy: far out-of-the-money options lose digits")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("p2_graph2.png", dpi=110)
    plt.close()


# GRAPH 3: implied volatility, where Newton works

def graph3():
    S, T, r = 100, 0.5, 0.05
    strikes = list(range(60, 201, 5))
    sigmas = [0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.5]

    ok_k, ok_s, fail_k, fail_s = [], [], [], []
    for K in strikes:
        for sigma in sigmas:
            try:
                price = model_price("call", S, K, T, r, sigma)
            except ValueError:
                continue                       # pricer refuses these inputs
            if price < 1e-8:
                continue                       # price too tiny to be meaningful
            found, steps = implied_vol_newton("call", price, S, K, T, r)
            if found is not None and abs(found - sigma) < 1e-6:
                ok_k.append(K)
                ok_s.append(sigma)
            else:
                fail_k.append(K)
                fail_s.append(sigma)

    plt.figure(figsize=(8, 4.8))
    plt.scatter(ok_k, ok_s, s=28, label=f"Newton works ({len(ok_k)})")
    plt.scatter(fail_k, fail_s, s=40, marker="x", color="red",
                label=f"Newton fails, bisection needed ({len(fail_k)})")
    plt.xlabel("strike price K  (stock price S = 100)")
    plt.ylabel("true volatility")
    plt.title("Implied volatility: Newton from a guess of 0.2 (T = 0.5)")
    # legend below the plot, so it does not hide any points
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("p2_graph3.png", dpi=110)
    plt.close()


# GRAPH 4: variance error vs offset

def graph4():
    exponents = [e / 2 for e in range(0, 25)]          # offsets 1e0 ... 1e12
    offsets = [10 ** e for e in exponents]
    naive_err, welford_err = [], []
    for offset in offsets:
        data = [offset + 4, offset + 7, offset + 13, offset + 16]   # true variance = 30
        naive_err.append(max(abs(variance_naive(data) - 30) / 30, FLOOR))
        welford_err.append(max(abs(variance_welford(data) - 30) / 30, FLOOR))

    plt.figure(figsize=(8, 4.8))
    plt.plot(offsets, naive_err, marker="o", markersize=3, label="textbook formula")
    plt.plot(offsets, welford_err, marker="o", markersize=3, linestyle="--", label="Welford")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("offset added to every number (log scale)")
    plt.ylabel("relative error of the variance (log scale)")
    plt.title("Variance: the textbook formula breaks as numbers get large")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("p2_graph4.png", dpi=110)
    plt.close()


# RUN ALL

print("drawing graph 1 ...")
graph1()
print("drawing graph 2 ...")
graph2()
print("drawing graph 3 ...")
graph3()
print("drawing graph 4 ...")
graph4()
print("done: p2_graph1.png ... p2_graph4.png")