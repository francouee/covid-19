from src.utils import *
from src import bokeh_plot

import subprocess
import os
import pathlib

data_path = pathlib.Path("../data/")


# ---- Update data ---- #
if os.path.exists(str(data_path) + "/ecdc_full_data.csv"):
    print("Deleting file")
    os.remove(str(data_path) + "/ecdc_full_data.csv")

bashCommand = "wget https://covid.ourworldindata.org/data/ecdc/full_data.csv"
subprocess.call(bashCommand.split(), stdout=subprocess.PIPE)

bashCommand = "mv full_data.csv " + str(data_path) + "/ecdc_full_data.csv"
subprocess.call(bashCommand.split(), stdout=subprocess.PIPE)

# ---- read data ---- #

data = pd.read_csv(data_path / "ecdc_full_data.csv")
data = data.rename(columns={"Total confirmed cases of COVID-19" : "total_cases"})
data['date'] = data.date.apply(pd.to_datetime)
data['date_str'] = data.date.apply(lambda x: x.strftime('%d/%m/%Y'))
data = data_china_smoothing(data, n_days_smoothing=6, n_cases_true=5000)

df_all_prediction = pd.DataFrame()
countries = ["France", "Italy", 'South Korea', "China", "Japan", "Spain", "United Kingdom",
             "Germany", "Denmark", "Sweden", "Norway", "Netherlands", "Australia", "Austria"]


# ---- compute predictions data ---- #

for country in tqdm(countries, position=0, leave=True):
    print("fit model for " + country + " data")
    df = get_country_and_min_count(data, country)

    fitted_sigmoid_df, paramters_values_sigmoid = compute_moving_predictions(df, n_prediction=90, n_bootstrap=20,
                                                                             min_data=df.shape[0] - 6, step=1,
                                                                             loss='MSE', linear_proba=True)
    fitted_sigmoid_df["location"] = np.repeat(country, repeats=fitted_sigmoid_df.shape[0])

    df_all_prediction = pd.concat([df_all_prediction, fitted_sigmoid_df])


# ---- plot data ---- #

bokeh_plot.generate_plot(data, df_all_prediction)



