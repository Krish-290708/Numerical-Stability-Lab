from mpmath import mp, mpf, exp as mp_exp
mp.dps = 50


def exp_series(x, n):
    term, total = 1.0, 1.0          #this means that the first term of the Taylor series is 1, and the total sum starts at 1 as well (the first term)
    largest_term = abs(term)
    for k in range(1, n + 1):       #this loop iterates from 1 to n (inclusive), where n is the number of terms specified by the user
        term *= x / k               #this line updates the term by multiplying it by x/k, which is the formula for the k-th term in the Taylor series expansion of e^x
        total += term               #this line adds the current term to the total sum, effectively accumulating the sum of the Taylor series
        largest_term = max(largest_term, abs(term))     #this line is used to first find the largest absolute term in the Taylor series expansion of e^x. It compares the current largest absolute term with the absolute value of the current term and updates largest_term accordingly.
    return total, largest_term  
    
def exp_reciprocal(x, n):
    total, largest_term = exp_series(abs(x), n)    # series for the positive version of x
    if x < 0:
        return 1.0 / total                         # e^-20 = 1 / e^20
    else:
        return total                               # x is not negative: no trick needed
      
def relative_error(approx, x):
    true = mp_exp(mpf(x))
    return float(abs((mpf(approx) - true) / true))

def exp_range_reduction(x, n):
    total, largest_term = exp_series(x / 16, n)     # series on the small input x / 16
    return total ** 16                              # raise to the 16th power to get back to e^x

def exp_horner(x, n):
    # Work from the INSIDE of the brackets OUT.
    result = 1                              #start with result = 1.0   (the innermost bracket)
    for k in range(n,0,-1):                 #loop k from n DOWN to 1:  for k in range(n, 0, -1): (range(n, 0, -1) counts n, n-1, ..., 2, 1)
        result = result*x/k + 1.0 
    return result  

def exp_kahan(x, n):
    term, total = 1.0, 1.0
    c = 0.0                          # the crumb jar, starts empty
    for k in range(1, n + 1):
        term *= x / k
        y = term - c                  #  y = term - c    put the saved crumbs back into this term
        t = total + y                 # t = total + y  do the addition (this is where digits get dropped)
        c = (t-total) - y             # c = (t - total) - y    work out what was dropped, save it in the jar
        total = t                     # total = t     the new total
    return total                       

def exp_horner_reciprocal(x, n):
    value = exp_horner(abs(x), n)       #combining the horner method(fastest) with the reciprocal method(most accurate) to get the best outcome.
    if x < 0:
        return 1.0/value
    else:
        return value