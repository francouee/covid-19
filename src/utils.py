import pandas as pd
import numpy as np
from scipy.optimize import minimize
from tqdm import tqdm
import seaborn as sns


def get_country(data: pd.DataFrame, location: str):
    """return the projection of the DataFrame with the selected country"""
    return data[data.location == location]


def get_country_and_min_count(data: pd.DataFrame, location: str, min_count_total=15):
    """return the projection of the DataFrame with the selected country"""
    return data.loc[(data.location == location) & (data.total_cases >= min_count_total)]


def get_min_count(data: pd.DataFrame, min_count_total=15):
    """return the projection of the DataFrame with the selected country"""
    return data.loc[(data.total_cases >= min_count_total)]


def sigmoid(x, x0, K, r):
    """
    Compute the values of a generalized logistic function defined by x0, K, a and r

    Parameters
    ----------
    x: input function
    x0: lag of the generalized logistic function
    K: asymptote of the generalized logistic function
    r: generalized logistic function parameter

    Returns
    -------
    image of x with the generalized logistic function
    """

    return K / (1 + np.exp(-r * (x - x0)))


def fit_sigmoid_boostrap(data: pd.DataFrame, n_bootstrap=100, proba=True):
    """
    Compute the optimum parameters to fit a generalized logistic function
    on the data and estimate the paramters distribution with boostrap

    Parameters
    ----------
    data : pd.DataFrame containing the values to fit
    n_bootstrap : Number of boostrap to estimate the distribution of the fitted parameters
    proba : Whether or not to apply linear importance of the most recent values, default=True

    Returns
    -------
    list of all parameters computed for each boostrap sample

    """

    # --- Parameters to be optimized --- #
    params = {"x0": [], "K": [], "r": []}
    bootstrap_indexes = []

    # --- data used for the loss --- #
    data = data.reset_index()
    y = data.total_cases
    t = (data.index.values + 1)

    # --- begin bootstrap --- #
    for k in tqdm(range(n_bootstrap), position=0, leave=True):

        rng = np.random.RandomState()
        index_value = data.index.values

        # --- sample with a linear probability distribution if proba = True, uniform otherwise --- #

        proba = [1 / index_value.shape[0] for _ in range(index_value.shape[0])]
        if proba:
            proba = (index_value - np.min(index_value)) / np.sum((index_value - np.min(index_value)))

        # --- bootstrap index --- #
        index = rng.choice(y.shape[0], size=y.shape[0], p=proba)
        bootstrap_indexes.append(index)

        t_bootstrap = t[index]
        y_bootstrap = y.iloc[index]

        # --- loss function minimise (MSE) with x = (x0, K, r) --- #
        fun = lambda x: np.mean((y_bootstrap - sigmoid(t_bootstrap, *x)) ** 2)

        # --- initial parameters --- #

        x0 = (max(t) / 2, max(y) / 2, 0.1)

        # --- optimisation --- #
        res = minimize(fun, x0, method='Nelder-Mead')

        params["x0"].append(res["x"][0])
        params["K"].append(res["x"][1])
        params["r"].append(res["x"][2])

    return params, bootstrap_indexes


def get_prediction_sigmoid(data: pd.DataFrame, fitted_params: dict, n_prediction: int):
    """
    Compute the model predictions with for each quantile 25%, 50% and 75% of the parameter K

    Parameters
    ----------
    data : pd.DataFrame containing the values to fit
    fitted_params : list of all parameters computed for each boostrap sample
    n_prediction : Number of data point to predict

    Returns
    -------
    fitted_sigmoid DataFrame containing all
    """
    quantiles = {
        "25%": [0.5, 0.25, 0.5],
        "50%": [0.5, 0.5, 0.5],
        "75%": [0.5, 0.75, 0.5]
    }

    fitted_sigmoid_df = pd.DataFrame()
    paramters_values_sigmoid = pd.DataFrame()

    t_pred = np.arange(1, n_prediction, 1)
    t_pred_date = pd.date_range(start=data.date.iloc[0], freq="d", periods=t_pred.shape[0])

    fitted_sigmoid_df["date"] = t_pred_date

    for quantile, quantile_params in quantiles.items():
        # --- get the quantiles of parameters computed via bootstrap ---#
        x0, K, r = [np.quantile(list(fitted_params.values())[i], quantile_params[i]) for i in
                    range(len(quantile_params))]

        # --- use the parameters to compute the values of the fitted sigmoid --- #
        fitted_sigmoid_df[quantile] = sigmoid(t_pred, x0, K, r)

        # --- keep parameters values of each quantiles --- #
        paramters_values_sigmoid[quantile] = [x0, K, r]

    fitted_sigmoid_df["derivative"] = np.quantile(fitted_params['r'], 0.5) * fitted_sigmoid_df["50%"] * \
                                      (1 - fitted_sigmoid_df["50%"] / np.quantile(fitted_params['K'], 0.5))

    return fitted_sigmoid_df, paramters_values_sigmoid


def plot_params_distribution(params):
    """
    Plot the parameters distribution

    Parameters
    ----------
    params: list of all parameters computed for each boostrap sample

    Returns
    -------
    matplotlib figure
    """
    param_df = pd.DataFrame(data=params)
    figure = sns.pairplot(param_df, kind='reg', diag_kind='kde', height=3)

    return figure
