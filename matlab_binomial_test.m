steps = 500;
dt = data{:, 'DTE'} / 365 / steps;
u = exp(data{:, 'impl_vol'} .* (dt .^ 0.5));
d = 1 / u;

St = data{:, 'Spot'} .* (u .^ repmat([steps:-2:-(steps+1)], size(data, 1), 1));