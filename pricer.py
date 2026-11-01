# pricer.py
# Interactive option calculator (type values, get answers).
#   1) Price an option      volatility -> call and put prices
#   2) Implied volatility   market price -> volatility
#   3) Quit

import math
from Black_Scholes_lab import d1_d2, call_price, put_price
from iv_lab import implied_vol, vega, model_price
from normal_lab import normal_cdf_stable

# PLAIN-ENGLISH HELPERS (they only print explanations)

def volatility_label(sigma):
    """A rough rule of thumb for how lively a volatility number is."""
    if sigma < 0.15:
        return "low (a calm stock)"
    elif sigma < 0.30:
        return "moderate (typical for a large company)"
    elif sigma < 0.50:
        return "high (a lively stock)"
    else:
        return "very high (a wild stock)"


def typical_range(S, sigma, T):
    """Where the stock ends up about two times out of three (rough)."""
    move = sigma * math.sqrt(T)               # typical size of the move
    return max(S * (1 - move), 0), S * (1 + move), move * 100


def explain_price(S, K, T, sigma, call, d2):
    """Explain the numbers of option 1 in simple words."""
    low, high, move_pct = typical_range(S, sigma, T)
    intrinsic = max(S - K, 0)                 # what you would gain by using the right immediately
    time_value = call - intrinsic             # the rest: the price of the CHANCE
    chance = normal_cdf_stable(d2) * 100      # model's chance of finishing above K

    print("\nWHAT THIS MEANS")
    print("-" * 50)
    print(f"Volatility: {sigma * 100:.0f}% a year is {volatility_label(sigma)}.")
    print(f"  Over {T:g} year(s) the stock typically moves about {move_pct:.0f}%,")
    print(f"  so about two times out of three it ends between {low:.0f} and {high:.0f}.")
    print(f"Price: the call costs {call:.2f}, which is {call / S * 100:.1f}% of the stock price.")
    print(f"  {intrinsic:.2f} is intrinsic value (what using the right immediately would give you).")
    print(f"  {time_value:.2f} is time value (what you pay for the CHANCE of a move in your favour).")
    print(f"Break-even: to profit, the stock must finish above about {K + call:.2f}")
    print(f"  (the strike {K:g} plus the {call:.2f} you paid).")
    print(f"Worst case: you lose the {call:.2f} you paid, never more.")
    print(f"Chance: the model puts about {chance:.0f}% on the stock finishing above {K:g}.")
    print("  (That is the model's own estimate, not a forecast.)")


def explain_implied_vol(kind, market, S, K, T, r, sigma):
    """Explain the result of option 2, and compare it with the user's own view."""
    low, high, move_pct = typical_range(S, sigma, T)

    print("\nWHAT THIS MEANS")
    print("-" * 50)
    print(f"The market charges {market:.2f} for this {kind}. For that price to be fair,")
    print(f"the stock must have a volatility of {sigma * 100:.1f}% a year: {volatility_label(sigma)}.")
    print(f"So the market is expecting typical moves of about {move_pct:.0f}% over {T:g} year(s),")
    print(f"roughly from {low:.0f} to {high:.0f}. That is the market's view of how much it will move.")

    text = input("\nYour own expected volatility (for example 0.3), or Enter to skip: ").strip()
    if text != "":
        view = float(text)
        fair = model_price(kind, S, K, T, r, view)
        print("-" * 50)
        print(f"With your view of {view * 100:.0f}% the {kind} would be worth {fair:.2f}.")
        if view > sigma:
            print(f"You expect MORE movement than the market, so the {market:.2f} price looks cheap to you.")
        elif view < sigma:
            print(f"You expect LESS movement than the market, so the {market:.2f} price looks expensive to you.")
        else:
            print("Your view matches the market, so the price looks fair to you.")
        print("(An illustration of the idea, not advice. Bigger moves raise the value of both calls and puts.)")


def print_basics():
    """A short glossary in plain words."""
    print("\nTHE BASICS")
    print("=" * 50)
    print("Stock price (S)   what one share costs today.")
    print("Strike (K)        the fixed price written into the option.")
    print("Call option       the right (not the duty) to BUY the stock at K.")
    print("Put option        the right (not the duty) to SELL the stock at K.")
    print("Premium           the price you pay today for that right.")
    print("Expiry (T)        when the right runs out, in years (0.5 = six months).")
    print("Interest rate (r) what money earns safely per year. It slightly changes the price.")
    print("Volatility        how much the stock tends to jump around, per year.")
    print("                  20% means a typical yearly move of about 20%.")
    print("Implied volatility the volatility the market PRICE is assuming. Found backwards.")
    print("In the money      using the right now would give a gain (call: S above K).")
    print("Out of the money  using the right now would give nothing (call: S below K).")
    print("Intrinsic value   the gain you would get by using the right immediately.")
    print("Time value        the rest of the price: the chance things move your way.")
    print("Vega              how much the price changes if volatility rises by 1.00.")
    print("Break-even        strike plus premium (for a call): where you start to profit.")


print("=" * 50)
print("  Option pricer")
print("=" * 50)

print("S = stock price, K = strike price, T = years to expiry,")
print("r = interest rate, sigma = volatility. Use decimals: 5% = 0.05")

while True:
    print("\n1) Price an option")
    print("2) Implied volatility")
    print("3) Learn the basics")
    print("4) Quit")
    choice = input("Choose 1, 2, 3 or 4: ").strip()

    if choice == "4":
        print("Goodbye.")
        break

    # Anything that goes wrong (text instead of a number, T = 0, a price
    # outside the bounds ...) raises a ValueError and lands in 'except' below.
    try:
        if choice == "1":
            # ---------- volatility in, price out ----------
            S = float(input("Stock price S: "))
            K = float(input("Strike price K: "))
            T = float(input("Years to expiry T: "))
            r = float(input("Interest rate r (0.05 = 5%): "))
            sigma = float(input("Volatility sigma (0.2 = 20%): "))

            d1, d2 = d1_d2(S, K, T, r, sigma)
            call = call_price(S, K, T, r, sigma)
            put = put_price(S, K, T, r, sigma)

            # In, at or out of the money? (this describes the call)
            if S > K:
                state = "in the money"
            elif S == K:
                state = "at the money"
            else:
                state = "out of the money"

            # Put-call parity: call - put must equal S - K*e^(-rT)
            parity_gap = abs((call - put) - (S - K * math.exp(-r * T)))

            print("-" * 50)
            print(f"The call is {state} (stock {S:g}, strike {K:g})")
            print(f"  d1            {d1:12.6f}")
            print(f"  d2            {d2:12.6f}")
            print(f"  Call price    {call:12.6f}")
            print(f"  Put price     {put:12.6f}")
            print(f"  Vega          {vega(S, K, T, r, sigma):12.6f}")
            print(f"  Parity check  {parity_gap:12.1e}   (should be about 1e-14 or smaller)")
            explain_price(S, K, T, sigma, call, d2)

            # Round trip: feed the call price back in and see if we get sigma back
            try:
                back, steps, method = implied_vol("call", call, S, K, T, r)
                print(f"Round trip: that call price implies sigma = {back:.6f} (you typed {sigma:g})")
            except ValueError:
                print("Round trip: not available for these inputs.")

        elif choice == "2":
            # ---------- price in, volatility out ----------
            kind = input("call or put: ").strip().lower()
            if kind != "call" and kind != "put":
                raise ValueError("please type call or put")
            market = float(input("Market price of the option: "))
            S = float(input("Stock price S: "))
            K = float(input("Strike price K: "))
            T = float(input("Years to expiry T: "))
            r = float(input("Interest rate r (0.05 = 5%): "))

            sigma, steps, method = implied_vol(kind, market, S, K, T, r)

            print("-" * 50)
            print(f"  Implied volatility  {sigma:.6f}   ({sigma * 100:.2f}% per year)")
            print(f"  Found by            {method} in {steps} steps")
            explain_implied_vol(kind, market, S, K, T, r, sigma)
            if vega(S, K, T, r, sigma) < 1e-6:
                print("WARNING: the price barely depends on volatility, so this is unreliable.")

        elif choice == "3":
            print_basics()

        else:
            print("Please type 1, 2, 3 or 4.")

    except ValueError as problem:
        print("Could not compute:", problem)