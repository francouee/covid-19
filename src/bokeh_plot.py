import bokeh.plotting as bkp
import bokeh.models as bkm
from bokeh.palettes import d3

import pathlib
import datetime

from src.utils import get_country
import numpy as np

includes_path = pathlib.Path("../_includes/")


def generate_plot(data, df_all_prediction):
    COLORS = d3['Category10'][10]

    tooltips = f"""
            <div>
                <p>
                    <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre de cas : </span>
                    <span style="font-size: 12px; color: {COLORS[0]}; font-weight: bold;font-family:century gothic;">@total_cases</span>
                <br> 
                    <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre de nouveaux cas : </span>
                    <span style="font-size: 12px; color: {COLORS[1]}; font-weight: bold;font-family:century gothic;">@new_cases</span>
                <br> 
                    <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre de deces : </span>
                    <span style="font-size: 12px; color: {COLORS[3]}; font-weight: bold;font-family:century gothic;">@total_deaths</span>
                <br> 
                    <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre nouveaux deces : </span>
                    <span style="font-size: 12px; color: {COLORS[5]}; font-weight: bold;font-family:century gothic;">@new_deaths</span>
                <br> 
                    <span style="font-size: 12px; color: black;font-family:century gothic;">Date : </span>
                    <span style="font-size: 12px; color: black; font-weight: bold;font-family:century gothic;">@date_str</span>
                </p>
            </div>
        """

    tooltips_predictions = f"""
            <div>
                <p>
                    <span style="font-size: 12px; color: black;font-family:century gothic;">Prédiction nombre de cas : </span>
                    <span style="font-size: 12px; color: {COLORS[0]}; font-weight: bold;font-family:century gothic;">@median_display</span>
                <br> 
                    <span style="font-size: 12px; color: black;font-family:century gothic;">Date : </span>
                    <span style="font-size: 12px; color: black; font-weight: bold;font-family:century gothic;">""" + """@date_str</span>
                </p>
            </div>
        """

    hover = bkm.tools.HoverTool(names=['line_total'],
                                tooltips=tooltips,
                                mode='vline'
                                )

    hover_prediction = bkm.tools.HoverTool(names=['prediction'],
                                           tooltips=tooltips_predictions,
                                           )

    # --- define all DataSource needed --- #

    source_all = bkm.ColumnDataSource(data)
    country = 'France'
    source = bkm.ColumnDataSource(get_country(data, country))

    source_all_prediction = bkm.ColumnDataSource(df_all_prediction)
    source_prediction = bkm.ColumnDataSource(
        get_country(df_all_prediction, country))

    date_end_training = np.unique(get_country(
        df_all_prediction, country)["date_end_train"])[-1]
    source_prediction_end_date = bkm.ColumnDataSource(get_country(df_all_prediction, country)[
                                                      get_country(df_all_prediction,
                                                                  country).date_end_train == date_end_training])

    slider = bkm.Slider(start=0, end=len(np.unique(get_country(df_all_prediction, country)["date_end_train"])) - 1,
                        value=0, step=1, title="Days dropped for prediction")

    # ----------- #

    p = bkp.figure(y_axis_type="linear", x_axis_type='datetime',
                   title=f'Covid 19 evolution: {country}', x_axis_label='date',
                   y_axis_label='Total number of Covid 19 cases',
                   width=1400, tools=[hover, 'pan', 'wheel_zoom', 'reset'],
                   x_range=[get_country(data, country).date.min(),
                            get_country(data, country).date.max() + datetime.timedelta(days=1)],
                   y_range=[-get_country(data, country).total_cases.max() * 0.05,
                            get_country(data, country).total_cases.max() * 1.1])
    p.yaxis.formatter = bkm.formatters.NumeralTickFormatter(format='0,0')
    p.xaxis.formatter = bkm.formatters.DatetimeTickFormatter(
        days=['%d/%m', '%d%a'], months=['%m/%Y', '%b %Y'])
    p.add_tools(hover_prediction)

    # p.toolbar.active_scroll = p.select_one(bkm.WheelZoomTool)

    y_extra_range_max = np.max([np.max(get_country(data, country).new_cases.values), np.max(get_country(data, country).total_deaths.values)])

    p.extra_y_ranges = {"Number of deaths": bkm.Range1d(start=-0.05 * y_extra_range_max,
                                                        end=1.1 * y_extra_range_max)}
    p.add_layout(bkm.LinearAxis(y_range_name="Number of deaths", axis_label="New Covid 19 cases",
                                formatter=bkm.formatters.NumeralTickFormatter(format='0,0')), 'right')

    # --- plot total cases --- #

    p.line(source=source, x='date', y='total_cases', name='line_total', color=COLORS[0], legend_label='total cases',
           muted_alpha=0.1)
    p.circle(source=source, x='date', y='total_cases',
             color=COLORS[0], muted_alpha=0.1)

    # --- plot new cases --- #

    p.vbar(source=source, x='date', top='new_cases', color=COLORS[1], width=50e6, alpha=0.5, name='bar',
           y_range_name="Number of deaths", legend_label='new cases', muted_alpha=0.1)

    # --- plot total death --- #

    p.line(source=source, x='date', y='total_deaths', color=COLORS[3], y_range_name="Number of deaths",
           name='line_death', legend_label='total deaths', muted_alpha=0.1)
    p.circle(source=source, x='date', y='total_deaths', color=COLORS[3], y_range_name="Number of deaths",
             muted_alpha=0.1)

    # --- plot new death --- #

    p.vbar(source=source, x='date', top='new_deaths', color=COLORS[5], width=50e6, alpha=0.5,
           y_range_name="Number of deaths", legend_label='new deaths', muted_alpha=0.1)

    button_click_count = bkm.ColumnDataSource({"clicks": [0]})

    select = bkm.Select(title="Country: ", value=country,
                        options=list(data.location.unique()))
    button_log = bkm.Button(label="Log Scale", button_type='primary')

    # --- Predictions --- #

    median_prediction = p.line(source=source_prediction_end_date, x='date', y='median', line_color=COLORS[0],
                               name='prediction')
    prediction_cases_line = p.line(source=source_prediction_end_date, x='date', y='derivative', color=COLORS[1],
                                   y_range_name="Number of deaths")

    band_low = bkm.Band(source=source_prediction_end_date, base='date', lower='25%', upper='median',
                        fill_color=COLORS[0],
                        level='underlay', fill_alpha=0.1, line_width=0.5, line_color='black')

    band_high = bkm.Band(source=source_prediction_end_date, base='date', lower='median', upper='75%',
                         fill_color=COLORS[0],
                         level='underlay', fill_alpha=0.1, line_width=0.5, line_color='black')

    median_prediction.visible = False
    prediction_cases_line.visible = False
    band_low.visible = False
    band_high.visible = False

    p.add_layout(band_low)
    p.add_layout(band_high)

    button_prediction = bkm.Button(
        label="Show predictions", button_type="primary")

    # -- Callback -- #

    callback = bkm.CustomJS(args=dict(source=source, source_all=source_all, select=select, x_range=p.x_range,
                                      y_range_left=p.y_range, y_range_right=p.extra_y_ranges[
                                          'Number of deaths'],
                                      title=p.title,
                                      button_click_count=button_click_count, slider=slider,
                                      source_all_prediction=source_all_prediction,
                                      source_prediction=source_prediction,
                                      source_prediction_end_date=source_prediction_end_date,
                                      median_prediction=median_prediction,
                                      band_low=band_low,
                                      prediction_cases_line=prediction_cases_line,
                                      band_high=band_high), code="""
                            var country = select.value

                            var date = source_all.data['date']
                            var date_str = source_all.data['date_str']
                            var location = source_all.data['location']
                            var total_cases = source_all.data['total_cases']
                            var new_cases = source_all.data['new_cases']
                            var total_deaths = source_all.data['total_deaths']
                            var new_deaths = source_all.data['new_deaths']


                            var new_date = []
                            var new_date_str = []
                            var new_total_cases = []
                            var new_new_cases = []
                            var new_total_deaths = []
                            var new_new_deaths = []


                            for(var i=0; i < date.length; i++){
                                if(location[i]==country){
                                    new_date.push(date[i]);
                                    new_date_str.push(date_str[i])
                                    new_total_cases.push(total_cases[i]);
                                    new_new_cases.push(new_cases[i]);
                                    new_total_deaths.push(total_deaths[i]);
                                    new_new_deaths.push(new_deaths[i]);
                                }
                            }

                            source.data['date']=new_date;
                            source.data['date_str']=new_date_str;
                            source.data['total_cases']=new_total_cases;
                            source.data['new_cases']=new_new_cases;
                            source.data['total_deaths']=new_total_deaths;
                            source.data['new_deaths']=new_new_deaths;

                            const new_cases_no_Nan = new_new_cases.filter(function (value) {
                                return !Number.isNaN(value);
                            });
                            const cases_no_Nan = new_total_cases.filter(function (value) {
                                return !Number.isNaN(value);
                            });

                            y_range_right.setv({"start": -0.05*Math.max.apply(Math, new_cases_no_Nan.concat(new_total_deaths)), 
                                                "end": 1.1*Math.max.apply(Math, new_cases_no_Nan.concat(new_total_deaths))})

                            y_range_left.setv({"start": -0.05*Math.max.apply(Math, cases_no_Nan), 
                                               "end": 1.1*Math.max.apply(Math, cases_no_Nan)})

                            x_range.setv({"start": Math.min.apply(Math, new_date), "end": 1.0001*Math.max.apply(Math, new_date)})

                            title.text = "Evolution du nombre de cas en " + country

                            source.change.emit();


                            // change value of predictions

                            button_click_count.data.clicks = 0

                            median_prediction.visible = false
                            band_low.visible = false
                            band_high.visible = false
                            prediction_cases_line.visble = false

                            var date_end_prediction = source_all_prediction.data['date_end_train']

                            var location = source_all_prediction.data['location']
                            var date = source_all_prediction.data['date']
                            var date_str = source_all_prediction.data['date_str']
                            var quantile_1 = source_all_prediction.data['25%']
                            var quantile_2 = source_all_prediction.data['median']
                            var quantile_3 = source_all_prediction.data['75%']
                            var new_cases = source_all_prediction.data['derivative']
                            var median_prediction = source_all_prediction.data['median_display']

                            var new_date = []
                            var new_date_str = []
                            var new_date_end_prediction = []
                            var new_quantile_1 = []
                            var new_quantile_2 = []
                            var new_quantile_3 = []
                            var new_new_cases = []
                            var new_median_prediction = []

                            for(var i=0; i < quantile_1.length; i++){
                                if(location[i]==country){
                                    new_date.push(date[i])
                                    new_date_str.push(date_str[i])
                                    new_date_end_prediction.push(date_end_prediction[i])
                                    new_quantile_1.push(quantile_1[i]);
                                    new_quantile_2.push(quantile_2[i]);
                                    new_quantile_3.push(quantile_3[i]);
                                    new_new_cases.push(new_cases[i]);
                                    new_median_prediction.push(median_prediction[i]);
                                }
                            }   
                            source_prediction.data['date']=new_date
                            source_prediction.data['date_str']=new_date_str
                            source_prediction.data['date_end_train']=new_date_end_prediction
                            source_prediction.data['25%']=new_quantile_1;
                            source_prediction.data['median']=new_quantile_2;
                            source_prediction.data['75%']=new_quantile_3;
                            source_prediction.data['derivative']=new_new_cases;
                            source_prediction.data['median_display']=new_median_prediction;


                            var n = new_date.length
                            var max_date = Math.max.apply(Math, new_date_end_prediction)

                            var new_date_bis = []
                            var new_date_str_bis = []
                            var new_date_end_prediction_bis = []
                            var new_quantile_1_bis = []
                            var new_quantile_2_bis = []
                            var new_quantile_3_bis = []
                            var new_new_cases_bis = []
                            var new_median_prediction_bis = []

                            for(var i=0; i < n; i++){
                                if(new_date_end_prediction[i]==max_date){
                                    new_date_bis.push(new_date[i])
                                    new_date_str_bis.push(new_date_str[i])
                                    new_date_end_prediction_bis.push(new_date_end_prediction[i])
                                    new_quantile_1_bis.push(new_quantile_1[i]);
                                    new_quantile_2_bis.push(new_quantile_2[i]);
                                    new_quantile_3_bis.push(new_quantile_3[i]);
                                    new_new_cases_bis.push(new_new_cases[i]);
                                    new_median_prediction_bis.push(new_median_prediction[i]);
                                }
                            }

                            var n = new_date_bis.length
                            var max_date = Math.max.apply(Math, new_date_end_prediction_bis)

                            source_prediction_end_date.data['date']=new_date_bis
                            source_prediction_end_date.data['date_str']=new_date_str_bis
                            source_prediction_end_date.data['date_end_train']=new_date_end_prediction_bis
                            source_prediction_end_date.data['25%']=new_quantile_1_bis;
                            source_prediction_end_date.data['median']=new_quantile_2_bis;
                            source_prediction_end_date.data['75%']=new_quantile_3_bis;
                            source_prediction_end_date.data['derivative']=new_new_cases_bis;
                            source_prediction_end_date.data['median_display']=new_median_prediction_bis;

                            source_prediction.change.emit();
                            source_prediction_end_date.change.emit()



                            const unique = (value, index, self) => {
                                       return self.indexOf(value) === index
                                   }

                            // change slider value

                            slider.setv({"end": new_date_end_prediction.filter(unique).length - 1, "value": 0})

                            """)

    callback_button = bkm.CustomJS(args=dict(y_axis=p.left, title=p.title), code="""
    console.log(y_axis)
    y_axis = LogAxis()
    """)

    select.js_on_change('value', callback)
    button_log.js_on_click(callback_button)

    callback_button = bkm.CustomJS(
        args=dict(source=source, source_prediction=source_prediction, source_all_prediction=source_all_prediction,
                  source_prediction_end_date=source_prediction_end_date, select=select,
                  button_prediction=button_prediction, median_prediction=median_prediction, band_low=band_low,
                  prediction_cases_line=prediction_cases_line,
                  band_high=band_high, button_click_count=button_click_count,
                  x_range=p.x_range, y_range_left=p.y_range,
                  y_range_right=p.extra_y_ranges['Number of deaths']), code="""
                                   // function to get unique value of an array
                                   const unique = (value, index, self) => {
                                       return self.indexOf(value) === index
                                   }

                                   var date = source.data['date'];
                                   var total_cases = source.data['total_cases'];
                                   var new_cases = source.data['new_cases'];
                                   var total_deaths = source.data['total_deaths'];

                                   var date_prediction = source_prediction.data['date'];
                                   var total_cases_prediction = source_prediction.data['75%'];

                                   const new_cases_no_Nan = new_cases.filter(function (value) {
                                       return !Number.isNaN(value);
                                   });
                                   const cases_no_Nan = total_cases.filter(function (value) {
                                       return !Number.isNaN(value);
                                   });

                                   var country = select.value
                                   button_click_count.data.clicks ++
                                   var show_prediction = (button_click_count.data.clicks % 2) == 1

                                   var locations_predicted = source_all_prediction.data['location'].filter(unique)

                                   if (locations_predicted.includes(country) == false){
                                       window.alert("This country doesn't have prediction: Available countries are: " + locations_predicted);
                                   }
                                   else{
                                       if (show_prediction == true){
                                           median_prediction.visible = true
                                           band_low.visible = true
                                           band_high.visible = true
                                           prediction_cases_line.visble = true

                                           y_range_left.setv({"start": -0.05*Math.max.apply(Math, total_cases_prediction), "end": 1.1*Math.max.apply(Math, total_cases_prediction)})
                                           y_range_right.setv({"start": -0.05*Math.max.apply(Math, new_cases_no_Nan.concat(total_deaths)) * Math.max.apply(Math, total_cases_prediction)/Math.max.apply(Math, cases_no_Nan),
                                                               "end": 1.1*Math.max.apply(Math, new_cases_no_Nan.concat(total_deaths)) * Math.max.apply(Math, total_cases_prediction)/Math.max.apply(Math, cases_no_Nan)})

                                           x_range.setv({"start": Math.min.apply(Math, date_prediction), "end": 1.0001*Math.max.apply(Math, date_prediction)})
                                       }
                                       else{
                                           median_prediction.visible = false
                                           band_low.visible = false
                                           band_high.visible = false
                                           prediction_cases_line.visble = false

                                           y_range_left.setv({"start": -0.05*Math.max.apply(Math, cases_no_Nan), "end": 1.1*Math.max.apply(Math, cases_no_Nan)})
                                           y_range_right.setv({"start": -0.05*Math.max.apply(Math, new_cases_no_Nan.concat(total_deaths)), "end": 1.1*Math.max.apply(Math, new_cases_no_Nan.concat(total_deaths))})
                                           x_range.setv({"start": Math.min.apply(Math, date), "end": 1.0001*Math.max.apply(Math, date)})

                                       }
                                   }


                                   """)

    button_prediction.js_on_click(callback_button)

    callback_slider = bkm.CustomJS(
        args=dict(source=source, source_prediction=source_prediction, source_all_prediction=source_all_prediction,
                  source_prediction_end_date=source_prediction_end_date, select=select,
                  prediction_cases_line=prediction_cases_line, slider=slider, button_click_count=button_click_count,
                  x_range=p.x_range, y_range_left=p.y_range,
                  y_range_right=p.extra_y_ranges['Number of deaths']), code="""

                           // function to get unique value of an array
                           const unique = (value, index, self) => {
                               return self.indexOf(value) === index
                           }

                           var slider_value = slider.value
                           var country = select.value

                           var date_prediction = source_prediction.data['date']
                           var date_str = source_prediction.data['date_str']
                           var date_end_prediction = source_prediction.data['date_end_train']
                           var quantile_1 = source_prediction.data['25%'];
                           var quantile_2 = source_prediction.data['median']
                           var quantile_3 = source_prediction.data['75%']
                           var new_cases = source_prediction.data['derivative'];
                           var median_prediction = source_prediction.data['median_display']

                           var unique_end_prediction = date_end_prediction.filter(unique)

                           var show_prediction = (button_click_count.data.clicks % 2) == 1
                           var locations_predicted = source_all_prediction.data['location'].filter(unique)

                           if (show_prediction == true && locations_predicted.includes(country)){
                                var new_date_prediction = []
                                var new_date_str = []
                                var new_date_end_prediction = []
                                var new_quantile_1 = []
                                var new_quantile_2 = []
                                var new_quantile_3 = []
                                var new_new_cases = []
                                var new_median_prediction = []

                                for(var i=0; i < quantile_1.length; i++){
                                    if(date_end_prediction[i]==unique_end_prediction[slider.end - slider_value]){
                                        new_date_prediction.push(date_prediction[i])
                                        new_date_str.push(date_str[i])
                                        new_date_end_prediction.push(date_end_prediction[i])
                                        new_quantile_1.push(quantile_1[i]);
                                        new_quantile_2.push(quantile_2[i]);
                                        new_quantile_3.push(quantile_3[i]);
                                        new_new_cases.push(new_cases[i]);
                                        new_median_prediction.push(median_prediction[i]);
                                    }
                                }   


                                source_prediction_end_date.data['date']=new_date_prediction
                                source_prediction_end_date.data['date_str']=new_date_str
                                source_prediction_end_date.data['date_end_train']=new_date_end_prediction
                                source_prediction_end_date.data['25%']=new_quantile_1;
                                source_prediction_end_date.data['median']=new_quantile_2;
                                source_prediction_end_date.data['75%']=new_quantile_3;
                                source_prediction_end_date.data['derivative']=new_new_cases;
                                source_prediction_end_date.data['median_display']=new_median_prediction;

                                source_prediction_end_date.change.emit();

                                var date_prediction = source_prediction_end_date.data['date'];
                                var total_cases_prediction = source_prediction_end_date.data['75%'];

                                const new_cases_no_Nan = new_cases.filter(function (value) {
                                    return !Number.isNaN(value);
                                 });
                                const cases_no_Nan = quantile_2.filter(function (value) {
                                   return !Number.isNaN(value);
                                 });


                                // y_range_left.setv({"start": -0.05*Math.max.apply(Math, total_cases_prediction), "end": 1.1*Math.max.apply(Math, total_cases_prediction)})
                                // x_range.setv({"start": Math.min.apply(Math, date_prediction), "end": 1.0001*Math.max.apply(Math, date_prediction)})

                           }

                                   """)

    slider.js_on_change('value', callback_slider)

    p.legend.location = "top_left"
    p.legend.click_policy = "mute"

    return select, button_prediction, slider, p
