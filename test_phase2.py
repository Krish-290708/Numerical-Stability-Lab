# test_phase2.py
# Automated tests for Phase 2. Run with:   python -m pytest -v
# Each test has an ID (N = normal, B = Black-Scholes, I = implied vol, S = stats)
# and checks ONE thing. A good test must be able to fail: several of these
# check that the "naive" version really does fail, so the problem is proven.

import math
import random
import statistics

import pytest
from mpmath import mp, mpf, ncdf, log, sqrt, exp

from normal_lab import normal_pdf, normal_cdf, normal_cdf_stable, upper_tail
from Black_Scholes_lab import d1_d2, call_price, put_price
from iv_lab import model_price, vega, implied_vol, implied_vol_newton, implied_vol_bisection
from stats_lab import (variance_naive, variance_welford, log_returns,
                       historical_volatility, logsumexp_naive, logsumexp_stable)

mp.dps = 60


# helpers: 60-digit reference answers

def rel_error(value, true):
    return float(abs((mpf(value) - true) / true))


def reference_prices(S, K, T, r, sigma):
    S, K, T, r, sigma = map(mpf, (S, K, T, r, sigma))
    d1 = (log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    call = S * ncdf(d1) - K * exp(-r * T) * ncdf(d2)
    put = K * exp(-r * T) * ncdf(-d2) - S * ncdf(-d1)
    return call, put


# N: NORMAL DISTRIBUTION (normal_lab.py)

def test_N1_pdf_at_zero():
    """The bell curve is 1/sqrt(2*pi) = 0.39894... tall at x = 0."""
    assert normal_pdf(0) == pytest.approx(0.3989422804014327, rel=1e-12)


def test_N2_cdf_known_values():
    """Phi(0) = 0.5, Phi(1) = 0.84134..., Phi(1.96) = 0.97500..."""
    assert normal_cdf(0, 40) == pytest.approx(0.5, abs=1e-15)
    assert normal_cdf(1, 40) == pytest.approx(0.8413447460685429, rel=1e-12)
    assert normal_cdf(1.96, 40) == pytest.approx(0.9750021048517795, rel=1e-12)


def test_N3_cdf_symmetry():
    """Phi(x) + Phi(-x) must equal 1."""
    for x in [0.5, 1, 2, 3, 5]:
        assert normal_cdf_stable(x) + normal_cdf_stable(-x) == pytest.approx(1.0, abs=1e-14)


def test_N4_series_only_fails_in_left_tail():
    """The Stage 1 series is badly wrong at x = -8 (proves the problem exists)."""
    true = ncdf(mpf(-8))
    assert rel_error(normal_cdf(-8, 400), true) > 0.01


def test_N5_stable_version_accurate_in_left_tail():
    """The Stage 2 fix stays accurate all the way to x = -20."""
    for x in [-3, -5, -8, -10, -15, -20]:
        assert rel_error(normal_cdf_stable(x), ncdf(mpf(x))) < 1e-12


def test_N6_stable_version_accurate_everywhere_else():
    """Accuracy across the whole supported range, both sides of zero."""
    for x in [-1.5, -1, 0, 0.5, 1, 2, 3, 5, 8]:
        assert rel_error(normal_cdf_stable(x), ncdf(mpf(x))) < 1e-12


def test_N7_far_right_is_exactly_one():
    """Beyond x = 8.3 the true value is 1 to within 1e-16."""
    assert normal_cdf_stable(10) == 1.0


def test_N8_out_of_range_raises_error():
    """x below -20 is unsupported and must say so instead of guessing."""
    with pytest.raises(ValueError):
        normal_cdf_stable(-25)


def test_N9_upper_tail_matches_cdf():
    """upper_tail(x) is Phi(-x) by symmetry."""
    for x in [2, 3, 5, 8]:
        assert rel_error(upper_tail(x, 200), ncdf(mpf(-x))) < 1e-12


# B: BLACK-SCHOLES PRICER (bs_lab.py)

def test_B1_classic_case():
    """S=K=100, T=1, r=5%, sigma=20%: call 10.4506 and put 5.5735."""
    assert call_price(100, 100, 1, 0.05, 0.2) == pytest.approx(10.4506, abs=1e-4)
    assert put_price(100, 100, 1, 0.05, 0.2) == pytest.approx(5.5735, abs=1e-4)


def test_B2_matches_high_precision_reference():
    """Accurate to 1e-11 across in, at and out of the money options."""
    cases = [(100, 100, 1, 0.05, 0.2), (100, 90, 0.5, 0.03, 0.25), (100, 110, 1, 0.05, 0.2),
             (100, 150, 0.5, 0.05, 0.2), (100, 200, 0.25, 0.05, 0.2)]
    for S, K, T, r, sigma in cases:
        ref_call, ref_put = reference_prices(S, K, T, r, sigma)
        assert rel_error(call_price(S, K, T, r, sigma), ref_call) < 1e-11
        assert rel_error(put_price(S, K, T, r, sigma), ref_put) < 1e-11


def test_B3_put_call_parity():
    """call - put = S - K*e^(-rT), for many different inputs."""
    for S, K, T, r, sigma in [(100, 100, 1, 0.05, 0.2), (80, 120, 2, 0.01, 0.5),
                              (120, 80, 0.25, 0.08, 0.1), (50, 55, 3, 0.0, 0.3)]:
        gap = (call_price(S, K, T, r, sigma) - put_price(S, K, T, r, sigma)
               - (S - K * math.exp(-r * T)))
        assert abs(gap) < 1e-9


def test_B4_d2_equals_d1_minus_sigma_root_T():
    """The definition d2 = d1 - sigma*sqrt(T)."""
    d1, d2 = d1_d2(100, 110, 2, 0.05, 0.3)
    assert d2 == pytest.approx(d1 - 0.3 * math.sqrt(2), abs=1e-14)


def test_B5_price_rises_with_volatility():
    """More volatility makes both options worth more."""
    sigmas = [0.05, 0.1, 0.2, 0.4, 0.8]
    calls = [call_price(100, 100, 1, 0.05, s) for s in sigmas]
    puts = [put_price(100, 100, 1, 0.05, s) for s in sigmas]
    assert calls == sorted(calls) and puts == sorted(puts)


def test_B6_call_price_stays_within_bounds():
    """max(S - K*e^(-rT), 0) <= call <= S."""
    for K in [50, 80, 100, 120, 200]:
        c = call_price(100, K, 1, 0.05, 0.3)
        assert max(100 - K * math.exp(-0.05), 0) - 1e-9 <= c <= 100


def test_B7_bad_inputs_raise_errors():
    """Impossible inputs must be rejected with a clear error."""
    with pytest.raises(ValueError):
        call_price(100, 100, 0, 0.05, 0.2)       # no time left
    with pytest.raises(ValueError):
        call_price(100, 100, 1, 0.05, 0)         # no volatility
    with pytest.raises(ValueError):
        call_price(-100, 100, 1, 0.05, 0.2)      # negative stock price


# =====================================================================
# I: IMPLIED VOLATILITY (iv_lab.py)
# =====================================================================
def test_I1_round_trip_recovers_sigma():
    """sigma -> price -> implied sigma, for well-behaved cases."""
    for kind, K, T, sigma in [("call", 100, 1, 0.25), ("call", 110, 0.5, 0.3),
                              ("put", 90, 0.25, 0.4), ("call", 100, 2, 0.8)]:
        price = model_price(kind, 100, K, T, 0.05, sigma)
        found, steps, method = implied_vol(kind, price, 100, K, T, 0.05)
        assert abs(found - sigma) < 1e-9


def test_I2_newton_is_fast_when_it_works():
    """Newton needs about 5 steps."""
    price = model_price("call", 100, 100, 1, 0.05, 0.25)
    found, steps = implied_vol_newton("call", price, 100, 100, 1, 0.05)
    assert found is not None and steps <= 10


def test_I3_newton_fails_where_vega_is_tiny():
    """Put K=150, T=0.1: the price curve is flat at the first guess, Newton gives up."""
    price = model_price("put", 100, 150, 0.1, 0.05, 0.4)
    found, steps = implied_vol_newton("put", price, 100, 150, 0.1, 0.05)
    assert found is None


def test_I4_combined_solver_falls_back_to_bisection():
    """The same case is still solved, by the backup method."""
    price = model_price("put", 100, 150, 0.1, 0.05, 0.4)
    found, steps, method = implied_vol("put", price, 100, 150, 0.1, 0.05)
    assert method == "bisection" and abs(found - 0.4) < 1e-9


def test_I5_bisection_step_count():
    """Halving an interval of 5 down to 1e-12 takes about 43 steps."""
    price = model_price("call", 100, 100, 1, 0.05, 0.25)
    found, steps = implied_vol_bisection("call", price, 100, 100, 1, 0.05)
    assert 40 <= steps <= 45


def test_I6_price_outside_bounds_has_no_answer():
    """A call can't cost more than the stock."""
    with pytest.raises(ValueError):
        implied_vol("call", 150, 100, 100, 1, 0.05)


def test_I7_vega_matches_a_numerical_slope():
    """vega should equal the change in price per change in sigma."""
    h = 1e-5
    slope = (call_price(100, 100, 1, 0.05, 0.2 + h)
             - call_price(100, 100, 1, 0.05, 0.2 - h)) / (2 * h)
    assert vega(100, 100, 1, 0.05, 0.2) == pytest.approx(slope, rel=1e-6)


# =====================================================================
# S: STATISTICS (stats_lab.py)
# =====================================================================
def test_S1_variance_small_numbers():
    """Both methods agree on easy data: variance of [4, 7, 13, 16] is 30."""
    assert variance_naive([4, 7, 13, 16]) == pytest.approx(30)
    assert variance_welford([4, 7, 13, 16]) == pytest.approx(30)


def test_S2_naive_variance_fails_for_large_numbers():
    """At offset 1e9 the textbook formula is off by more than 100% (proves the problem)."""
    data = [1e9 + v for v in [4, 7, 13, 16]]
    assert abs(variance_naive(data) - 30) > 30


def test_S3_welford_variance_survives_large_numbers():
    """Welford still gives 30 at offsets up to 1e10."""
    for offset in [1e6, 1e8, 1e9, 1e10]:
        data = [offset + v for v in [4, 7, 13, 16]]
        assert variance_welford(data) == pytest.approx(30, rel=1e-6)


def test_S4_welford_matches_python_statistics():
    """On random data Welford equals Python's own statistics.variance."""
    random.seed(1)
    data = [random.gauss(50, 5) for _ in range(500)]
    assert variance_welford(data) == pytest.approx(statistics.variance(data), rel=1e-10)


def test_S5_variance_of_constant_data_is_zero():
    assert variance_welford([7, 7, 7, 7]) == pytest.approx(0, abs=1e-12)


def test_S6_log_returns():
    """100 -> 110 is ln(1.1); n prices give n-1 returns."""
    r = log_returns([100, 110, 121])
    assert len(r) == 2
    assert r[0] == pytest.approx(math.log(1.1), rel=1e-12)


def test_S7_historical_volatility_recovers_true_value():
    """10 years of simulated prices at 20% volatility: estimate within 0.02."""
    random.seed(42)
    daily = 0.2 / math.sqrt(252)
    prices = [100.0]
    for _ in range(2520):
        prices.append(prices[-1] * math.exp(random.gauss(0, daily)))
    assert abs(historical_volatility(prices) - 0.2) < 0.02


def test_S8_flat_prices_have_zero_volatility():
    assert historical_volatility([100, 100, 100, 100]) == pytest.approx(0, abs=1e-12)


def test_S9_naive_logsumexp_overflows():
    """The direct formula crashes for large values (proves the problem)."""
    with pytest.raises((OverflowError, ValueError)):
        logsumexp_naive([1000, 1000])


def test_S10_stable_logsumexp_correct():
    """Known answers, including the cases where the naive one crashes."""
    assert logsumexp_stable([1000, 1000]) == pytest.approx(1000 + math.log(2), rel=1e-14)
    assert logsumexp_stable([-1000, -1000]) == pytest.approx(-1000 + math.log(2), rel=1e-14)
    assert logsumexp_stable([1, 2, 3]) == pytest.approx(logsumexp_naive([1, 2, 3]), rel=1e-14)


def test_S11_logsumexp_shift_property():
    """Adding c to every value adds exactly c to the result."""
    base = logsumexp_stable([1, 2, 3])
    assert logsumexp_stable([501, 502, 503]) == pytest.approx(base + 500, rel=1e-14)