from exp_lab import exp_series, exp_reciprocal, relative_error, exp_range_reduction, exp_horner, exp_kahan, exp_horner_reciprocal


def test_series_accurate_for_positive_x():
    for x in [0.5, 1, 5, 10]:
        answer = exp_series(x, 100)[0]              # [0] picks the total out of the two values returned
        assert relative_error(answer, x) < 1e-12


def test_series_accurate_for_negative_x():
    for x  in [-20,-10,-5,-1]:
        answer = exp_reciprocal(x, 100)
        assert relative_error(answer, x) < 1e-12     #test 2: exp_reciprocal is accurate (error < 1e-12) for x in [-20, -10, -5, -1]

def test_plain_series_fails_at_x():
    answer = exp_series(-20, 100)[0]              # [0] picks the total out of the two values returned
    assert relative_error(answer, -20) > 0.1    # test 3: the plain series FAILS at x = -20 (error > 0.1). This documents the failure.

def test_x_zero_gives_one():
    assert exp_series(0, 100)[0] == 1
    assert exp_reciprocal(0, 100) == 1                      #test 4: x = 0 gives exactly 1 for both methods

def test_series_does_not_crash_at_n():
    exp_series(5,1)[0]
    exp_reciprocal(-5,1)      # test 5: n = 1 does not crash (just call both methods)

def test_methods_agree_for_positive_x():
    for x in [0.5, 1, 5]:
        assert exp_series(x, 100)[0] == exp_reciprocal(x, 100)       # test 6: for positive x, exp_reciprocal and exp_series give the same number

def test_range_reduction_is_accurate_for_x():
    for x in [-20, 1, 10]:
        answer = exp_range_reduction(x,100)
        assert relative_error(answer,x) < 1e-12            # test 7: exp_range_reduction is accurate (error < 1e-12) for x in [-20, 1, 10]

def test_horner_is_accurate_for_x():
    for x in [1, 10]:
        answer = exp_horner(x,100)
        assert relative_error(answer,x) < 1e-12        # test 8: exp_horner is accurate (error < 1e-12) for x = 1 and x = 10

def test_horner_fails_at_minus_20():
    assert relative_error(exp_horner(-20, 100), -20) > 0.1

def test_kahan_is_accurate_for_x():
    for x in [1, 10]:
        answer = exp_kahan(x,100)
        assert relative_error(answer,x) < 1e-12                         # test 10: exp_kahan is accurate (error < 1e-12) for x = 1 and x = 10

def test_kahan_fails_at_minus_20():
    assert relative_error(exp_kahan(-20, 100), -20) > 0.1               # test 11: exp_kahan FAILS at x = -20 (error > 0.1), recording that it doesn't help

def test_horner_reciprocal_is_accurate_for_x():
    for x in [-20,-10, 1, 10]:
        answer = exp_horner_reciprocal(x,100)
        assert relative_error(answer,x) < 1e-12
