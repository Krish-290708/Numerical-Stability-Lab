# Careful statistics for price data. Three jobs:
#   1) variance (how spread out numbers are), the safe way
#   2) historical volatility (turn a list of prices into one number)
#   3) log-sum-exp (add very big or very small exponentials without breaking)
# For each job there is an "obvious" version that can fail, and a safe one.

import math


# 1. VARIANCE

# Variance = how spread out the numbers are.
#   small variance -> numbers close together
#   big variance   -> numbers far apart
# We divide by (n - 1) because we only have a SAMPLE of the data.

def variance_naive(data):
    """The textbook shortcut:  (sum of squares - n * mean^2) / (n - 1).

    Looks fine on paper, but with big numbers close together it breaks.
    """
    n = len(data)             # how many numbers
    total = 0.0               # running sum of the numbers
    total_sq = 0.0            # running sum of the SQUARES of the numbers

    for x in data:
        total = total + x
        total_sq = total_sq + x * x    # for x = 1,000,000,000 this is 1e18: huge!

    mean = total / n

    # Here is the problem: total_sq and n*mean*mean are two HUGE almost-equal
    # numbers. Subtracting them wipes out the digits that mattered
    # (the same cancellation you saw in Phase 1).
    return (total_sq - n * mean * mean) / (n - 1)


def variance_welford(data):
    """Welford's method: the safe way.

    Instead of squaring big numbers, keep a running average and add up the
    small distances from it. Nothing huge is ever created.
    """
    n = 0              # how many numbers seen so far
    mean = 0.0         # average of the numbers seen so far
    m2 = 0.0           # sum of squared distances from the average

    for x in data:
        n = n + 1
        delta = x - mean               # how far the new number is from the old average
        mean = mean + delta / n        # nudge the average toward the new number
        m2 = m2 + delta * (x - mean)   # note: uses the UPDATED mean

    return m2 / (n - 1)


# 2. HISTORICAL VOLATILITY

# Volatility = how much a price jumps around. "Historical" means we measure it
# from past prices (as opposed to "implied", which comes from option prices).

def log_returns(prices):
    """Daily 'growth' of the price, as ln(today / yesterday).

    Example: 100 -> 101 gives ln(1.01) = 0.00995 (about +1%).
    Logs are used because they ADD UP across days.
    """
    returns = []
    for i in range(1, len(prices)):               # start at day 1: day 0 has no 'yesterday'
        returns.append(math.log(prices[i] / prices[i - 1]))
    return returns


def historical_volatility(prices, trading_days=252):
    """Yearly volatility estimated from a list of daily prices."""
    returns = log_returns(prices)
    daily_var = variance_welford(returns)         # the safe variance from above

    # daily_var is for ONE day. Variance adds up over days, so for a year
    # multiply by 252, and take the square root to get volatility.
    # That is the same as sqrt(daily_var) * sqrt(252).
    return math.sqrt(daily_var) * math.sqrt(trading_days)


# 3. LOG-SUM-EXP

# Goal: compute  log( e^a + e^b + e^c + ... )
# Problem: e^1000 is too big for a computer (overflow),
#          e^-1000 is too small and becomes 0 (then log(0) fails).

def logsumexp_naive(values):
    """The direct way. Crashes for big or very small values."""
    total = 0.0
    for v in values:
        total = total + math.exp(v)     # math.exp(1000) -> OverflowError
    return math.log(total)              # log(0) -> ValueError


def logsumexp_stable(values):
    """The same answer, without the crash.

    Trick: take the biggest value m out of every exponent.
        log( e^a + e^b )  =  m + log( e^(a-m) + e^(b-m) )
    Now the biggest exponent is e^0 = 1, so nothing overflows,
    and the sum is at least 1, so the log always works.
    """
    m = max(values)                     # the biggest value

    total = 0.0
    for v in values:
        total = total + math.exp(v - m)    # v - m is 0 or negative: safe

    return m + math.log(total)             # put the m back in