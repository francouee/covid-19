import subprocess
import os
from pathlib import Path
import sys
import logging
from tqdm import tqdm

import bokeh.models as bkm
from bokeh.embed import file_html
from bokeh.resources import Resources

sys.path.append(str(Path(os.getcwd()).parent))
sys.path.append(os.getcwd())

from src.utils import *
from src import bokeh_plot

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

data_path = Path("../data/")
includes_path = Path("../_includes/")

# ---- Update data ---- #
if os.path.exists(str(data_path) + "/ecdc_full_data.csv"):
    logger.info("Deleting file")
    os.remove(str(data_path) + "/ecdc_full_data.csv")

bashCommand = "wget https://covid.ourworldindata.org/data/ecdc/full_data.csv"
subprocess.call(bashCommand.split(), stdout=subprocess.PIPE)

bashCommand = "mv full_data.csv " + str(data_path) + "/ecdc_full_data.csv"
subprocess.call(bashCommand.split(), stdout=subprocess.PIPE)

# ---- read data ---- #

data = pd.read_csv(data_path / "ecdc_full_data.csv")
data = data.rename(
    columns={"Total confirmed cases of COVID-19": "total_cases"})
data = data[data.location.isin(['World', 'France', 'China'])].dropna()
data['date'] = data.date.apply(pd.to_datetime)
data['date_str'] = data.date.apply(lambda x: x.strftime('%d/%m/%Y'))
data = data_china_smoothing(data, n_days_smoothing=6, n_cases_true=5000)

df_all_prediction = pd.DataFrame()
countries = ["World", ]


# ---- compute predictions data ---- #

for country in tqdm(countries, position=0, leave=True):
    logger.info(" fit model for " + country + " data")
    df = get_country_and_min_count(data, country)

    n_prediction = df.shape[0]

    fitted_sigmoid_df, parameters_values_sigmoid = compute_moving_predictions(df, n_prediction=n_prediction + 200,
                                                                              n_bootstrap=5,
                                                                              min_data=df.shape[0] - 10, step=1,
                                                                              loss='MSE', linear_proba=True)
    fitted_sigmoid_df["location"] = np.repeat(country, repeats=fitted_sigmoid_df.shape[0])

    df_all_prediction = pd.concat([df_all_prediction, fitted_sigmoid_df])


# ---- plot data ---- #

select, button_prediction, slider, p = bokeh_plot.generate_plot(data, df_all_prediction)

html = file_html(bkm.Column(bkm.Row(select, button_prediction, slider, sizing_mode='stretch_width'), p,
                            sizing_mode='stretch_width'), Resources(mode='cdn'), "plot")

html = html.replace("<!DOCTYPE html>", " ")

with open("plot.html", 'w') as f:
    f.write(html)

bashCommand = "mv plot.html " + str(includes_path) + "/plot.html"
subprocess.call(bashCommand.split(), stdout=subprocess.PIPE)
