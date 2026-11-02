# Numerical Stability Lab: interactive web app.
# Running it with:   streamlit run app.py
#
# Four tabs, one per theme of the project:
#   1. e^x lab           six ways to compute e^x, and where they fail   (Phase 1)
#   2. Normal CDF        the series vs the continued-fraction fix       (Phase 2)
#   3. Option pricer     Black-Scholes prices and implied volatility    (Phase 2)
#   4. Stable statistics variance and log-sum-exp                       (Phase 2)
#
# Needs the project's own files in the same folder:
#   exp_lab.py, normal_lab.py, Black_Scholes_lab.py, iv_lab.py, stats_lab.py

import math

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from mpmath import mp, mpf, ncdf

from exp_lab import (exp_series, exp_reciprocal, exp_range_reduction,
                     exp_horner, exp_kahan, exp_horner_reciprocal, relative_error)
from normal_lab import normal_cdf, normal_cdf_stable
from Black_Scholes_lab import d1_d2, call_price, put_price
from iv_lab import implied_vol, vega, model_price
from stats_lab import (variance_naive, variance_welford,
                       logsumexp_naive, logsumexp_stable)

mp.dps = 60          # the 60-digit "true answer" used as the reference
FLOOR = 1e-17        # a log axis cannot show 0, so tiny errors are lifted to this

st.set_page_config(page_title="Numerical Stability Lab", layout="wide")


# =====================================================================
# SMALL HELPERS
# =====================================================================
def correct_digits(error):
    """How many of the 16 digits are right, given a relative error."""
    if error == 0:
        return 16.0
    return max(0.0, min(16.0, -math.log10(error)))


def rel_error(value, true):
    """Relative error against a high-precision true value."""
    return float(abs((mpf(value) - true) / true))


# =====================================================================
# TAB 1: e^x LAB (Phase 1)
# =====================================================================
@st.cache_data
def error_curve(x, n_max):
    """Error after 1, 2, ... n_max terms, for two methods (cached: it is slow)."""
    ns = list(range(1, n_max + 1))
    plain = [max(relative_error(exp_series(x, n)[0], x), FLOOR) for n in ns]
    fixed = [max(relative_error(exp_horner_reciprocal(x, n), x), FLOOR) for n in ns]
    return ns, plain, fixed


def set_x(value):
    st.session_state["x"] = float(value)


def tab_exp():
    st.subheader("Six ways to compute e^x")
    st.write("The series for e^x is exact for every x. But a computer keeps only about "
             "16 digits, and for negative x the terms get huge and cancel. "
             "Pick an x and see which methods survive.")

    if "x" not in st.session_state:
        st.session_state["x"] = -20.0

    left, right = st.columns(2)
    with left:
        st.number_input("x  (we compute e^x)", min_value=-50.0, max_value=50.0,
                        step=0.5, key="x")
        b1, b2, b3 = st.columns(3)
        b1.button("x = -20", on_click=set_x, args=(-20,))
        b2.button("x = -10", on_click=set_x, args=(-10,))
        b3.button("x = 1", on_click=set_x, args=(1,))
    with right:
        n = st.slider("number of series terms", 1, 200, 100)

    x = st.session_state["x"]

    # --- run all six methods ---
    methods = [
        ("plain series", exp_series(x, n)[0]),
        ("reciprocal trick", exp_reciprocal(x, n)),
        ("range reduction", exp_range_reduction(x, n)),
        ("horner", exp_horner(x, n)),
        ("kahan", exp_kahan(x, n)),
        ("horner + reciprocal", exp_horner_reciprocal(x, n)),
    ]
    rows = []
    for name, value in methods:
        err = relative_error(value, x)
        rows.append({"Method": name, "Result": f"{value:.12e}",
                     "Relative error": f"{err:.1e}",
                     "Correct digits": round(correct_digits(err), 1)})
    table = pd.DataFrame(rows)

    true = mp.exp(mpf(x))
    st.markdown(f"**True value of e^{x:g}** (60-digit reference): `{float(true):.12e}`")

    c1, c2 = st.columns([3, 2])
    with c1:
        st.dataframe(table, hide_index=True)
    with c2:
        fig, ax = plt.subplots(figsize=(5, 3.4))
        names = table["Method"].tolist()[::-1]            # reversed so the first method is on top
        digits = table["Correct digits"].tolist()[::-1]
        bars = ax.barh(names, digits)
        for bar, d in zip(bars, digits):
            ax.text(d + 0.2, bar.get_y() + bar.get_height() / 2, f"{d:g}", va="center")
        ax.set_xlim(0, 18)
        ax.set_xlabel("correct digits (out of 16)")
        ax.grid(True, axis="x")
        fig.tight_layout()
        st.pyplot(fig)
        st.caption("A short bar means that method failed at this x.")

    # --- the diagnosis, as in lab.py ---
    total, largest = exp_series(x, n)
    plain_err = relative_error(total, x)
    if plain_err < 1e-12:
        st.success(f"The plain series is accurate here (error {plain_err:.1e}).")
    elif total == 0 or largest / abs(total) > 10000:
        st.error(f"**Cancellation.** The largest term is {largest:.2e} but the true answer is only "
                 f"{float(abs(true)):.2e}. Adding and subtracting numbers that big wipes out the "
                 f"digits, so more terms will not help. The reciprocal trick avoids it.")
    else:
        st.warning("**Stopped too early (truncation).** The terms you skipped still matter. "
                   "Move the slider up.")

    # --- error vs number of terms ---
    st.markdown("#### Error as you add terms")
    ns, plain, fixed = error_curve(x, 200)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(ns, plain, label="plain series")
    ax.plot(ns, fixed, linestyle="--", label="horner + reciprocal")
    ax.axvline(n, color="gray", linewidth=1)
    ax.set_yscale("log")
    ax.set_xlabel("number of terms")
    ax.set_ylabel("relative error (log scale)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    st.caption("If the blue line goes flat high up, more terms cannot rescue it: "
               "that is cancellation, not truncation.")


# =====================================================================
# TAB 2: NORMAL CDF (Phase 2)
# =====================================================================
@st.cache_data
def cdf_curve():
    """Error of both versions from x = -10 to 8 (cached: it is slow)."""
    xs = [i / 4 for i in range(-40, 33)]
    series_err, stable_err = [], []
    for x in xs:
        true = ncdf(mpf(x))
        series_err.append(max(rel_error(normal_cdf(x, 400), true), FLOOR))
        stable_err.append(max(rel_error(normal_cdf_stable(x), true), FLOOR))
    return xs, series_err, stable_err


def tab_cdf():
    st.subheader("The normal CDF: Phi(x)")
    st.write("Phi(x) is the fraction of a bell curve lying below x. Black-Scholes needs it. "
             "The series version subtracts two nearly equal numbers for negative x, "
             "so it loses digits in the left tail. A continued fraction avoids the subtraction.")

    x = st.slider("x", -20.0, 8.0, -8.0, 0.25)
    true = ncdf(mpf(x))
    series_value = normal_cdf(x, 400)
    stable_value = normal_cdf_stable(x)
    series_err = rel_error(series_value, true)
    stable_err = rel_error(stable_value, true)

    a, b, c = st.columns(3)
    a.metric("True Phi(x)", f"{float(true):.6e}")
    b.metric("Series only", f"{series_value:.6e}")
    b.caption(f"relative error {series_err:.1e}")
    c.metric("Series + continued fraction", f"{stable_value:.6e}")
    c.caption(f"relative error {stable_err:.1e}")

    if series_err > 1e-3:
        st.error("The series has lost essentially all its digits here. "
                 "The stable version is still accurate.")
    elif series_err > 1e-12:
        st.warning(f"The series has lost about {correct_digits(1e-16) - correct_digits(series_err):.0f} "
                   f"digits here. The stable version has not.")
    else:
        st.success("Both versions are accurate at this x.")

    xs, s_err, t_err = cdf_curve()
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(xs, s_err, marker="o", markersize=3, label="series only")
    ax.plot(xs, t_err, marker="o", markersize=3, linestyle="--", label="series + continued fraction")
    ax.axvline(x, color="gray", linewidth=1)
    ax.set_yscale("log")
    ax.set_xlabel("x")
    ax.set_ylabel("relative error (log scale)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)


# =====================================================================
# TAB 3: OPTION PRICER (Phase 2)
# =====================================================================
def volatility_label(sigma):
    if sigma < 0.15:
        return "low (a calm stock)"
    elif sigma < 0.30:
        return "moderate (typical for a large company)"
    elif sigma < 0.50:
        return "high (a lively stock)"
    return "very high (a wild stock)"


def tab_pricer():
    st.subheader("Black-Scholes option pricer")
    st.write("A **call** is the right (not the duty) to buy a stock at a fixed price K on a fixed date. "
             "A **put** is the right to sell. Move the sliders and watch the prices.")

    left, right = st.columns(2)
    with left:
        S = st.number_input("Stock price S", 1.0, 1000.0, 100.0, step=1.0)
        K = st.number_input("Strike price K", 1.0, 1000.0, 100.0, step=1.0)
        T = st.slider("Years to expiry T", 0.05, 3.0, 1.0, 0.05)
    with right:
        r = st.slider("Interest rate r", 0.0, 0.15, 0.05, 0.005)
        sigma = st.slider("Volatility sigma  (0.20 = 20% a year)", 0.05, 1.5, 0.20, 0.01)

    try:
        d1, d2 = d1_d2(S, K, T, r, sigma)
        call = call_price(S, K, T, r, sigma)
        put = put_price(S, K, T, r, sigma)
    except ValueError as problem:
        st.error(f"These inputs are too extreme for the pricer: {problem}. "
                 f"Move S and K closer together, or raise sigma or T.")
        return

    a, b, c, d = st.columns(4)
    a.metric("Call price", f"{call:.4f}")
    b.metric("Put price", f"{put:.4f}")
    c.metric("d1", f"{d1:.4f}")
    d.metric("Vega", f"{vega(S, K, T, r, sigma):.3f}")

    parity_gap = abs((call - put) - (S - K * math.exp(-r * T)))
    st.caption(f"Put-call parity check (call - put = S - K e^(-rT)): gap {parity_gap:.1e}, "
               f"which should be tiny.")

    # --- plain-English explanation of the call ---
    state = "in the money" if S > K else ("at the money" if S == K else "out of the money")
    move = sigma * math.sqrt(T)
    low, high = max(S * (1 - move), 0), S * (1 + move)
    intrinsic = max(S - K, 0)
    st.markdown("#### What this means")
    st.markdown(
        f"- **Volatility:** {sigma * 100:.0f}% a year is {volatility_label(sigma)}. "
        f"Over {T:g} year(s) the stock typically moves about {move * 100:.0f}%, so about two times "
        f"out of three it ends between {low:.0f} and {high:.0f}. *(A rough rule of thumb.)*\n"
        f"- **The call is {state}.** It costs {call:.2f}, which is {call / S * 100:.1f}% of the stock "
        f"price: {intrinsic:.2f} of intrinsic value plus {call - intrinsic:.2f} of time value "
        f"(the price of the *chance* of a favourable move).\n"
        f"- **Break-even:** the stock must finish above about {K + call:.2f} "
        f"(the strike plus what you paid) for you to profit.\n"
        f"- **Worst case:** you lose the {call:.2f} you paid, never more.\n"
        f"- **Chance:** the model puts about {normal_cdf_stable(d2) * 100:.0f}% on the stock "
        f"finishing above {K:g}. This is a *risk-neutral* probability (the pricing maths "
        f"pretends investors need no extra reward for risk), so it is a model number, "
        f"not a forecast of what will really happen."
    )

    # --- two charts ---
    g1, g2 = st.columns(2)
    with g1:
        lo, hi = 0.5 * min(S, K), 1.5 * max(S, K)
        ends = [lo + (hi - lo) * i / 200 for i in range(201)]
        profit = [max(price - K, 0) - call for price in ends]
        fig, ax = plt.subplots(figsize=(5.5, 3.6))
        ax.plot(ends, profit)
        ax.axhline(0, color="gray", linewidth=1)
        ax.axvline(K + call, color="red", linestyle=":", label=f"break-even {K + call:.1f}")
        ax.set_xlabel("stock price at expiry")
        ax.set_ylabel("profit of buying the call")
        ax.set_title("Profit at expiry")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
    with g2:
        sigmas, prices = [], []
        for i in range(1, 31):
            s = 0.05 * i
            try:
                prices.append(call_price(S, K, T, r, s))
                sigmas.append(s)
            except ValueError:
                pass
        fig, ax = plt.subplots(figsize=(5.5, 3.6))
        ax.plot(sigmas, prices)
        ax.scatter([sigma], [call], color="red", zorder=5, label="your sigma")
        ax.set_xlabel("volatility sigma")
        ax.set_ylabel("call price")
        ax.set_title("More volatility, higher price")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    # --- implied volatility ---
    st.markdown("#### Run it backwards: what volatility does a market price imply?")
    st.write("Real markets quote the price. The volatility behind it is *implied*. "
             "The solver tries Newton's method (fast), and falls back to bisection (safe) if it fails.")
    i1, i2 = st.columns(2)
    with i1:
        kind = st.radio("Option type", ["call", "put"], horizontal=True)
        market = st.number_input("Market price of the option", 0.0, 1000.0, 10.45, step=0.1)
    with i2:
        view = st.slider("Your own expected volatility", 0.05, 1.5, 0.30, 0.01)

    try:
        implied, steps, method = implied_vol(kind, market, S, K, T, r)
    except ValueError as problem:
        st.warning(f"No implied volatility for this price: {problem}")
        return

    x1, x2, x3 = st.columns(3)
    x1.metric("Implied volatility", f"{implied * 100:.2f}%")
    x2.metric("Found by", method)
    x3.metric("Steps", steps)

    if vega(S, K, T, r, implied) < 1e-6:
        st.warning("Vega is tiny: the price barely depends on volatility here, "
                   "so this answer is unreliable.")

    fair = model_price(kind, S, K, T, r, view)
    st.markdown(f"The market is pricing a typical yearly move of about **{implied * 100:.0f}%**. "
                f"With your view of **{view * 100:.0f}%** the {kind} would be worth **{fair:.2f}**, "
                f"against {market:.2f} in the market.")
    if view > implied:
        st.info("You expect more movement than the market, so this price looks **cheap** to you. "
                "(An illustration of the idea, not advice.)")
    elif view < implied:
        st.info("You expect less movement than the market, so this price looks **expensive** to you. "
                "(An illustration of the idea, not advice.)")
    else:
        st.info("Your view matches the market, so the price looks fair to you.")


# =====================================================================
# TAB 4: STABLE STATISTICS (Phase 2)
# =====================================================================
def tab_stats():
    st.subheader("Variance and log-sum-exp, done carefully")

    st.markdown("#### Variance of [offset+4, offset+7, offset+13, offset+16]")
    st.write("Shifting every number by the same amount does not change the spread, "
             "so the true variance is always **30**. The textbook formula does not agree.")
    exponent = st.slider("offset = 10 to the power of", 0, 12, 9)
    offset = 10.0 ** exponent
    data = [offset + v for v in [4, 7, 13, 16]]
    naive = variance_naive(data)
    welford = variance_welford(data)

    a, b, c = st.columns(3)
    a.metric("True variance", "30")
    b.metric("Textbook formula", f"{naive:.4f}")
    c.metric("Welford's method", f"{welford:.4f}")
    if naive < 0:
        st.error("The textbook formula returned a NEGATIVE variance, which is impossible. "
                 "It subtracted two huge, almost equal sums. Welford works with small distances "
                 "from a running mean instead.")
    elif abs(naive - 30) > 1e-6:
        st.warning("The textbook formula has started to lose digits. Welford has not.")
    else:
        st.success("Both are correct at this size. Push the offset up to see the difference.")

    st.markdown("#### log(e^a + e^b + e^c)")
    st.write("Used when combining very small probabilities stored as logs. "
             "The direct formula overflows for large values.")
    v1, v2, v3 = st.columns(3)
    a_val = v1.number_input("a", value=1000.0)
    b_val = v2.number_input("b", value=1000.0)
    c_val = v3.number_input("c", value=0.0)
    values = [a_val, b_val, c_val]

    try:
        naive_lse = f"{logsumexp_naive(values):.10f}"
    except (OverflowError, ValueError):
        naive_lse = "crashes"
    p, q = st.columns(2)
    p.metric("Direct formula", naive_lse)
    q.metric("Stable version", f"{logsumexp_stable(values):.10f}")
    st.caption("The stable version subtracts the biggest value first, so nothing overflows.")


# =====================================================================
# THE PAGE
# =====================================================================
st.title("Numerical Stability Lab")
st.caption("When correct maths gives wrong answers on a computer, and how to fix it.")

tab1, tab2, tab3, tab4 = st.tabs(["1. e^x lab", "2. Normal CDF",
                                  "3. Option pricer", "4. Stable statistics"])
with tab1:
    tab_exp()
with tab2:
    tab_cdf()
with tab3:
    tab_pricer()
with tab4:
    tab_stats()

st.divider()
st.caption("Source code and write-ups: https://github.com/Krish-290708/Numerical-Stability-Lab")