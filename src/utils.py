import pandas as pd
import numpy as np
from scipy.optimize import minimize
from tqdm import tqdm
import seaborn as sns
from sklearn.base import BaseEstimator
import datetime


def get_country(data: pd.DataFrame, location: str):
    """return the projection of the DataFrame with the selected country"""
    return data[data.location == location]


def get_country_and_min_count(data: pd.DataFrame, location: str, min_count_total=15):
    """return the projection of the DataFrame with the selected country"""
    return data.loc[(data.location == location) & (data.total_cases >= min_count_total)]


def get_min_count(data: pd.DataFrame, min_count_total=15):
    """return the projection of the DataFrame with the selected country"""
    return data.loc[(data.total_cases >= min_count_total)]


def data_china_smoothing(data: pd.DataFrame, n_days_smoothing: int, n_cases_true=4000):
    """
    smooth new cases data from 2020-02-13 where the covid 19 cases
    definition changed in china

    Parameters
    ----------
    data: Covid 19 dataset
    n_days_smoothing: number of days the 2020-02-13 should be smoothed
    n_cases_true: Number of true cases the count definition changed
    """

    data_china = get_country(data, "China").copy()
    date_change_count = "2020-02-13"
    date_begin_smooth = datetime.datetime(2020, 2, 13) - datetime.timedelta(days=n_days_smoothing - 1)

    time_mask = (data_china.date >= date_begin_smooth) & (data_china.date < date_change_count)
    data_to_change = data_china[time_mask].copy()

    new_cases_to_smooth = data_china.loc[data_china.date == date_change_count, "new_cases"].values[0] - n_cases_true


    # --- remove new_cases to total_cases to add smoothed new_cases afterward --- #
    data_to_change["total_cases"] -= np.cumsum(data_to_change["new_cases"])

    # --- Smooth new_cases over the period  --- #
    index = np.arange(1, n_days_smoothing, 1)
    data_to_change["new_cases"] += index * new_cases_to_smooth / np.sum(index)
    data_to_change["new_cases"] = data_to_change["new_cases"].astype("int16")


    data_to_change["total_cases"] += np.cumsum(data_to_change["new_cases"])

    # --- add smoothed data ---- #

    data_china[time_mask] = data_to_change
    data_china.loc[data_china.date == date_change_count, "new_cases"] = n_cases_true
    data_china["location"] = "China Smooth"

    data = pd.concat([data, data_china])

    return data



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


def two_mode_growth(x, x0, K, r1, r2, y, t1):
    """
    Compute the values of a generalized logistic function defined by x0, K, a and r

    Parameters
    ----------
    x: input function
    x0: lag of the generalized logistic function
    K: asymptote of the generalized logistic function
    r1: generalized logistic function parameter

    Returns
    -------
    image of x with the generalized logistic function
    """

    return (1 - y) * np.exp(r1 * x) + \
           y * (np.exp(r1 * t1) + K * (1 / (1 + np.exp(-r2 * (x - x0))) - 1 / (1 + np.exp(-r2 * (t1 - x0)))))


class SigmoidModel(BaseEstimator):
    """
    Parameters
    ----------
    n_bootstrap : Number of boostrap to estimate the distribution of the fitted parameters
    linear_proba : Whether or not to apply linear importance of the most recent values, default=True
    """

    def __init__(self, n_bootstrap=100, linear_proba=True, loss='MSE'):
        super(SigmoidModel).__init__()
        self.n_bootstrap = n_bootstrap
        self.linear_proba = linear_proba
        self.loss = loss
        self.params = {}
        self.bootstrap_indexes = []

    def fit(self, X: pd.DataFrame):
        """
        Compute the optimum parameters to fit a generalized logistic function
        on the data and estimate the paramters distribution with boostrap

        Parameters
        ----------
        X : pd.DataFrame containing the values to fit
        Returns
        -------
        list of all parameters computed for each boostrap sample

        """

        # --- Parameters to be optimized --- #
        params = {"x0": [], "K": [], "r": []}
        bootstrap_indexes = []

        # --- data used for the loss --- #
        data = X.reset_index()
        y = data.total_cases
        t = (data.index.values + 1)

        # --- begin bootstrap --- #
        for k in range(self.n_bootstrap):

            rng = np.random.RandomState()
            index_value = data.index.values

            # --- sample with a linear probability distribution if proba = True, uniform otherwise --- #

            proba = [1 / index_value.shape[0] for _ in range(index_value.shape[0])]
            if self.linear_proba:
                proba = (index_value - np.min(index_value)) / np.sum((index_value - np.min(index_value)))

            # --- bootstrap index --- #
            index = rng.choice(y.shape[0], size=y.shape[0], p=proba)
            bootstrap_indexes.append(index)

            t_bootstrap = t[index]
            y_bootstrap = y.iloc[index]

            # --- loss function minimise (MSE) with x = (x0, K, r) --- #
            if self.loss == 'MSE':
                loss = lambda x: np.mean((y_bootstrap - sigmoid(t_bootstrap, *x)) ** 2)

            elif self.loss == 'MAD':
                loss = lambda x: np.mean(np.abs((y_bootstrap - sigmoid(t_bootstrap, *x))))

            else:
                loss = lambda x: np.mean((y_bootstrap - sigmoid(t_bootstrap, *x)) ** 2)

            # --- initial parameters --- #

            x0 = (max(t) / 2, max(y) / 2, 0.1)

            # --- optimisation --- #
            res = minimize(loss, x0, method='Nelder-Mead')

            params["x0"].append(res["x"][0])
            params["K"].append(res["x"][1])
            params["r"].append(res["x"][2])

        self.params = params
        self.bootstrap_indexes = bootstrap_indexes

        return params, bootstrap_indexes

    def predict(self, t_pred, X):
        """
        Compute the model predictions with for each quantile 25%, 50% and 75% of the parameter K

        Parameters
        ----------
        X : pd.DataFrame containing the values fitted in .fit method
        t_pred : values to predict ex: t_pred = np.arange(1, n_prediction, 1)

        Returns
        -------
        fitted_sigmoid DataFrame containing all
        """
        quantiles = {
            "25%": [0.5, 0.25, 0.5],
            "median": [0.5, 0.5, 0.5],
            "75%": [0.5, 0.75, 0.5]
        }

        fitted_sigmoid_df = pd.DataFrame()
        paramters_values_sigmoid = pd.DataFrame()

        t_pred_date = pd.date_range(start=X.date.iloc[0], freq="d", periods=t_pred.shape[0])

        fitted_sigmoid_df["date"] = t_pred_date
        fitted_sigmoid_df["date_str"] = fitted_sigmoid_df.date.apply(lambda x: x.strftime('%d/%m/%Y'))

        for quantile, quantile_params in quantiles.items():
            # --- get the quantiles of parameters computed via bootstrap ---#
            x0, K, r = [np.quantile(list(self.params.values())[i], quantile_params[i]) for i in
                        range(len(quantile_params))]

            # --- use the parameters to compute the values of the fitted sigmoid --- #
            fitted_sigmoid_df[quantile] = sigmoid(t_pred, x0, K, r)

            # --- keep parameters values of each quantiles --- #
            paramters_values_sigmoid[quantile] = [x0, K, r]

        fitted_sigmoid_df["derivative"] = np.quantile(self.params['r'], 0.5) * fitted_sigmoid_df["median"] * \
                                          (1 - fitted_sigmoid_df["median"] / np.quantile(self.params['K'], 0.5))

        fitted_sigmoid_df["median_display"] = fitted_sigmoid_df["median"].apply(lambda x: '{:,}'.format(int(x)))

        return fitted_sigmoid_df, paramters_values_sigmoid

    def plot_params_distribution(self, height=3.5, **plot_kws):
        """
        Plot the parameters distribution

        Returns
        -------
        matplotlib figure
        """
        param_df = pd.DataFrame(data=self.params)
        figure = sns.pairplot(param_df, diag_kind='kde', height=height, plot_kws=plot_kws)

        return figure


def compute_moving_predictions(X: pd.DataFrame, n_prediction, step=5, min_data=10, n_bootstrap=10,
                               linear_proba=False, loss='MSE', verbose=False):
    fitted_sigmoid_moving = pd.DataFrame()
    paramters_values_moving = pd.DataFrame()

    n = X.shape[0]

    for k in range((n - min_data) // step + 1):
        sigmoid_model = SigmoidModel(n_bootstrap=n_bootstrap, linear_proba=linear_proba, loss=loss)

        end_data_index = min_data + step * k
        if k == (n - min_data) // step:
            # Take all data
            X_train = X
            end_data_index = X.shape[0]
        else:
            # Take a subset
            X_train = X.iloc[:end_data_index, :]

        if verbose:
            print(f"index values from 0 to {end_data_index}")

        t_pred_end = X_train.date.iloc[-1]
        t_pred = np.arange(1, n_prediction, 1)
        fitted_params, _ = sigmoid_model.fit(X_train)
        fitted_sigmoid_df, paramters_values_sigmoid = sigmoid_model.predict(t_pred, X_train)

        fitted_sigmoid_df["date_end_train"] = np.repeat(t_pred_end, repeats=fitted_sigmoid_df.shape[0])

        fitted_sigmoid_moving = pd.concat([fitted_sigmoid_moving, fitted_sigmoid_df])
        paramters_values_moving = pd.concat([paramters_values_moving, paramters_values_sigmoid])

    return fitted_sigmoid_moving, paramters_values_moving
