from numpy import log, exp, maximum, nan, sign
from scipy.stats import norm


"""This code makes assumptions about column names in the options chain frames (full_frame variable).

column_name: description
Spot: Spot price
StrikePrice: Strike price
rate: risk free rate
DTE: Days to expiry as an integer
Type: Type of instrument between 'Put' and 'Call'
"""


def fast_price_wrapper(full_frame):
    """Calculates black scholes price for entire options chain. Only meant to be used with the faster_vol_calc module. If used independently,
    ensure that implied vol resides inside impl_vol_guess and price would be output to price_from_guess."""

    d1 = (log(full_frame.Spot / full_frame.StrikePrice) + (full_frame.rate + (full_frame.impl_vol_guess ** 2) / 2) * (full_frame.DTE / 365)) / \
         (full_frame.impl_vol_guess * ((full_frame.DTE / 365) ** 0.5))
    d2 = d1 - (full_frame.impl_vol_guess * ((full_frame.DTE / 365) ** 0.5))

    calls, puts = full_frame.Type == 'Call', full_frame.Type == 'Put'
    N = norm.cdf

    full_frame.loc[calls, 'price_from_guess'] = full_frame.loc[calls, 'Spot'] * N(d1[calls]) - \
                                           full_frame.loc[calls, 'StrikePrice'] * exp(
        -full_frame.loc[calls, 'rate'] * (full_frame.loc[calls, 'DTE'] / 365)) * N(d2[calls])

    full_frame.loc[puts, 'price_from_guess'] = full_frame.loc[puts, 'StrikePrice'] * exp(
        -full_frame.loc[puts, 'rate'] * (full_frame.loc[puts, 'DTE'] / 365)) * N(-d2[puts]) - \
                                          full_frame.loc[puts, 'Spot'] * N(-d1[puts])

    return full_frame


def faster_vol_calc(full_frame, iterations: int = 50):
    """Uses bisection root finding algo to make our calculations much faster than the efficient library used in py_vollib.
    All bad data is marked with an implied vol of nan"""

    calls, puts = full_frame.Type == 'Call', full_frame.Type == 'Put'
    full_frame['ForwardPrice'] = full_frame.Spot * exp(full_frame.rate * (full_frame.DTE / 365))
    full_frame['ForwardOptionPrice'] = full_frame.Mid * exp(full_frame.rate * (full_frame.DTE / 365))
    full_frame.loc[calls, 'IntrinsicPrice'] = maximum(full_frame.loc[calls, 'ForwardPrice'] - full_frame.loc[calls, 'StrikePrice'],
                                                  0)
    full_frame.loc[puts, 'IntrinsicPrice'] = maximum(full_frame.loc[puts, 'StrikePrice'] - full_frame.loc[puts, 'ForwardPrice'], 0)

    bad_data = (full_frame.ForwardOptionPrice < full_frame.IntrinsicPrice)
    bad_data |= ((full_frame.Type == 'Put') & (full_frame.ForwardOptionPrice >= full_frame.StrikePrice))
    bad_data |= ((full_frame.Type == 'Call') & (full_frame.ForwardOptionPrice >= full_frame.ForwardPrice))
    bad_data |= ((full_frame.Ask <= 0) | (full_frame.Bid <= 0) | (full_frame.Spot == 0) | (full_frame.DTE == 0))
    good_data = full_frame.drop(full_frame[bad_data].index)

    good_data['left'] = 0
    good_data['right'] = 100

    for i in range(iterations):
        good_data['impl_vol_guess'] = (good_data.left + good_data.right) / 2
        good_data = fast_price_wrapper(good_data)

        good_data['price_diff_sign'] = sign(good_data.Mid - good_data.price_from_guess)
        good_data.loc[good_data.price_diff_sign == -1, 'right'] = good_data.loc[good_data.price_diff_sign == -1, 'impl_vol_guess']
        good_data.loc[good_data.price_diff_sign == 1, 'left'] = good_data.loc[good_data.price_diff_sign == 1, 'impl_vol_guess']
        
    full_frame.loc[good_data.index, 'impl_vol'] = good_data['impl_vol_guess']
    full_frame.loc[full_frame.index.difference(good_data.index), 'impl_vol'] = nan