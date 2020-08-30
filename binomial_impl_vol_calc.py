from scipy.stats import binom
import numpy as np


def old_wrapper(sigma=0.3, T=1, t=0, steps=2, r=0.03, S0=100, K=100):
    dt = T/steps
    u = np.exp(sigma * dt**0.5)
    d = 1/u
    p = (np.exp(r*dt)-d)/(u-d)
    
    St = S0 * (u ** np.arange(steps, -(steps+1), -2))
    binomial_expansion = np.array(binom(steps, 1-p).pmf(range(steps+1)))
    
    calls = np.array(list(map(max, np.zeros(len(St)), St-K)))
    puts = np.array(list(map(max, np.zeros(len(St)), K-St)))
    
    call_price = sum(binomial_expansion * calls) * np.exp(-r * T)
    put_price = sum(binomial_expansion * puts) * np.exp(-r * T)
    
    return call_price, put_price


def fast_eur_binomial_option_price_wrapper(option_chain, steps=500):
    dt = option_chain['DTE'].values / 365 / steps
    u = np.exp(option_chain.impl_vol_guess.values * (dt ** 0.5))
    d = 1 / u
    p = (np.exp(option_chain.rate.values * dt) - d) / (u - d)

    strikes = option_chain['StrikePrice'].values
    spots = option_chain['Spot'].values
    rfr = option_chain['rate'].values
    time = option_chain['DTE'].values / 365

    temp = np.arange(steps, -(steps+1), -2)
    call_price, put_price = [], []
    for ind in range(len(spots)):
        St = spots[ind] * (u[ind] ** temp)
        binom_expansion = np.array(binom(steps, 1-p[ind]).pmf(range(steps+1)))

        calls = np.array(list(map(max, np.zeros(len(St)), St - strikes[ind])))
        puts = np.array(list(map(max, np.zeros(len(St)), strikes[ind] - St)))

        call_price.append(sum(binom_expansion * calls) * np.exp(-rfr[ind] * time[ind]))
        put_price.append(sum(binom_expansion * puts) * np.exp(-rfr[ind] * time[ind]))

    # St = (option_chain.Spot.values * np.power(u, np.tile(np.arange(steps, -(steps+1), -2), (option_chain.shape[0], 1)).T))
    # binom_expansion = np.array([np.array(binom(steps, 1-p_).pmf(range(steps+1))) for p_ in p])
    #
    # calls_intrinsic = np.maximum(0, St - option_chain['StrikePrice'].values).T
    # puts_intrinsic = np.maximum(0, option_chain['StrikePrice'].values - St).T

    calls, puts = option_chain.Type == 'Call', option_chain.Type == 'Put'
    option_chain.loc[calls, 'price_from_guess'] = call_price[calls]
    option_chain.loc[puts, 'price_from_guess'] = put_price[puts]

    return option_chain['price_from_guess']


def main():
    pass


if __name__ == '__main__':
    main()
