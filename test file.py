import bisection_impl_vol_calc as module1
import binomial_impl_vol_calc as module2
import pandas as pd


def main():
    data = pd.read_csv('data.csv', parse_dates=['Date', 'ExpiryDate'])
    col_renames = {'CallPut': 'Type', 'Close': 'Spot', 'Strike': 'StrikePrice'}
    data.rename(columns=col_renames, inplace=True)

    data['impl_vol_guess'] = module1.faster_vol_calc(data).rename('impl_vol_guess')
    data.to_csv('data.csv', index=False)


if __name__ == '__main__':
    main()
