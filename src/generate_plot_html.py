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
subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

# ---- read data ---- #

data = pd.read_csv(data_path / "ecdc_full_data.csv")
data = data.rename(columns={"Total confirmed cases of COVID-19" : "total_cases"})
data['date'] = data.date.apply(pd.to_datetime)
data['date_str'] = data.date.apply(lambda x: x.strftime('%d/%m/%Y'))

df_all_prediction = pd.DataFrame()
countries = ["France", "Italy", 'South Korea', "China", "Japan", "Spain", "United Kingdom",
             "Germany", "Denmark", "Sweden", "Norway", "Netherlands", "Australia", "Austria"]


# ---- compute predictions data ---- #

for country in countries:
    df = get_country_and_min_count(data, country)

    fitted_params, _ = fit_sigmoid_boostrap(df, n_bootstrap=50)

    fitted_sigmoid_df, paramters_values_sigmoid = get_prediction_sigmoid(df, fitted_params, n_prediction=90)

    fitted_sigmoid_df["location"] = np.repeat(country, repeats=fitted_sigmoid_df.shape[0])
    df_all_prediction = pd.concat([df_all_prediction, fitted_sigmoid_df])


# ---- plot data ---- #

bokeh_plot.generate_plot(data, df_all_prediction)



