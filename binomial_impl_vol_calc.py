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
    option_chain['dt'] = option_chain['DTE'] / 30 / steps
    option_chain['u'] = np.exp(option_chain.impl_vol_guess * (option_chain.dt ** 0.5))
    option_chain['d'] = 1 / option_chain['u']
    option_chain['p'] = (np.exp(option_chain.rate * option_chain.dt) - option_chain.d) / (option_chain.u - option_chain.d)

    option_chain['St'] = (option_chain.Spot.values * np.power(option_chain.u.values, np.tile(np.arange(steps, -(steps+1), -2), (option_chain.shape[0], 1)).T)).T
    option_chain['binom_expansion'] = [np.array(binom(steps, 1-p).pmf(range(steps+1))) for p in option_chain.p.values]

    calls, puts = option_chain.Type == 'Call', option_chain.Type == 'Put'
    option_chain.loc[calls, 'price_from_guess'] = np.maximum(0, option_chain['St'] - option_chain.loc[calls, 'StrikePrice'])
    option_chain.loc[puts, 'price_from_guess'] = np.maximum(0, option_chain.loc[puts, 'StrikePrice'] - option_chain.loc[puts, 'Spot'])


def main():
    pass


if __name__ == '__main__':
    main()
