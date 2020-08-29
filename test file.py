import bisection_impl_vol_calc as module1
import binomial_impl_vol_calc as module2
import pandas as pd


def main():
    data = pd.read_csv('data.csv', parse_dates=['Date', 'ExpiryDate'])
    col_renames = {'CallPut': 'Type', 'Close': 'Spot', 'Strike': 'StrikePrice'}
    data.rename(columns=col_renames, inplace=True)

    module2.fast_eur_binomial_option_price_wrapper(data[~pd.isnull(data.impl_vol_guess)].iloc[:1000])


if __name__ == '__main__':
    main()
