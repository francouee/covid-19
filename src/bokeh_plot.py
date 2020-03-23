import bokeh.plotting as bkp
import bokeh.models as bkm
from bokeh.io import curdoc
from bokeh.palettes import d3
from bokeh.embed import file_html
from bokeh.resources import Resources
import subprocess

import pathlib
import datetime

includes_path = pathlib.Path("../_includes/")

from src.utils import get_country


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
                    <span style="font-size: 12px; color: black; font-weight: bold;font-family:century gothic;">""" + """@date_str</span>
                </p>
            </div>
        """

    tooltips_predictions = f"""
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
                    <span style="font-size: 12px; color: black; font-weight: bold;font-family:century gothic;">""" + """@date_str</span>
                </p>
            </div>
        """

    hover = bkm.tools.HoverTool(names=['line_total'],
                                tooltips=tooltips,
                                mode='vline'
                                )

    # --- define all DataSource needed --- #

    source_all = bkm.ColumnDataSource(data)
    country = 'France'
    source = bkm.ColumnDataSource(get_country(data, country))

    source_all_prediction = bkm.ColumnDataSource(df_all_prediction)
    source_prediction = bkm.ColumnDataSource(get_country(df_all_prediction, country))

    # ----------- #

    p = bkp.figure(y_axis_type="linear", x_axis_type='datetime',
                   title=f'Covid 19 evolution: {country}', x_axis_label='date', y_axis_label='Number of cases',
                   width=1400, tools=[hover, 'pan', 'wheel_zoom', 'reset'],
                   x_range=[get_country(data, country).date.min(),
                            get_country(data, country).date.max() + datetime.timedelta(days=1)],
                   y_range=[-get_country(data, country).total_cases.max() * 0.05,
                            get_country(data, country).total_cases.max() * 1.1])
    p.yaxis.formatter = bkm.formatters.NumeralTickFormatter(format='0,0')
    p.xaxis.formatter = bkm.formatters.DatetimeTickFormatter(days=['%d/%m', '%d%a'], months=['%m/%Y', '%b %Y'])

    # p.toolbar.active_scroll = p.select_one(bkm.WheelZoomTool)

    p.extra_y_ranges = {"Number of deaths": bkm.Range1d(start=-0.05 * get_country(data, country).new_cases.max(),
                                                        end=1.1 * get_country(data, country).new_cases.max())}
    p.add_layout(bkm.LinearAxis(y_range_name="Number of deaths", axis_label="new_cases",
                                formatter=bkm.formatters.NumeralTickFormatter(format='0,0')), 'right')

    # --- plot total cases --- #

    p.line(source=source, x='date', y='total_cases', name='line_total', color=COLORS[0], legend_label='total cases',
           muted_alpha=0.1)
    p.circle(source=source, x='date', y='total_cases', color=COLORS[0], muted_alpha=0.1)

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

    select = bkm.Select(title="Country: ", value=country, options=list(data.location.unique()))
    button_log = bkm.Button(label="Log Scale", button_type='primary')

    # --- Predictions --- #

    median_prediction = p.line(source=source_prediction, x='date', y='50%', line_color=COLORS[0])
    prediction_cases_line = p.line(source=source_prediction, x='date', y='derivative', color=COLORS[1],
                                   y_range_name="Number of deaths")

    band_low = bkm.Band(source=source_prediction, base='date', lower='25%', upper='50%', fill_color=COLORS[0],
                        level='underlay', fill_alpha=0.1, line_width=0.5, line_color='black')

    band_high = bkm.Band(source=source_prediction, base='date', lower='50%', upper='75%', fill_color=COLORS[0],
                         level='underlay', fill_alpha=0.1, line_width=0.5, line_color='black')

    median_prediction.visible = False
    prediction_cases_line.visible = False
    band_low.visible = False
    band_high.visible = False

    p.add_layout(band_low)
    p.add_layout(band_high)

    button_prediction = bkm.Button(label="Show predictions", button_type="primary")

    # -- Callback -- #

    callback = bkm.CustomJS(args=dict(source=source, source_all=source_all, select=select, x_range=p.x_range,
                                      y_range_left=p.y_range, y_range_right=p.extra_y_ranges['Number of deaths'],
                                      title=p.title,
                                      button_click_count=button_click_count,
                                      source_all_prediction=source_all_prediction,
                                      source_prediction=source_prediction, median_prediction=median_prediction,
                                      band_low=band_low,
                                      prediction_cases_line=prediction_cases_line,
                                      band_high=band_high), code=
                            """
                            var country = select.value
            
                            var date = source_all.data['date']
                            var location = source_all.data['location']
                            var total_cases = source_all.data['total_cases']
                            var new_cases = source_all.data['new_cases']
                            var total_deaths = source_all.data['total_deaths']
                            var new_deaths = source_all.data['new_deaths']
            
            
                            var new_date = []
                            var new_total_cases = []
                            var new_new_cases = []
                            var new_total_deaths = []
                            var new_new_deaths = []
            
            
                            for(var i=0; i < date.length; i++){
                                if(location[i]==country){
                                    new_date.push(date[i]);
                                    new_total_cases.push(total_cases[i]);
                                    new_new_cases.push(new_cases[i]);
                                    new_total_deaths.push(total_deaths[i]);
                                    new_new_deaths.push(new_deaths[i]);
                                }
                            }
            
                            source.data['date']=new_date;
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
            
                            y_range_right.setv({"start": -0.05*Math.max.apply(Math, new_cases_no_Nan), "end": 1.1*Math.max.apply(Math, new_cases_no_Nan)})
                            y_range_left.setv({"start": -0.05*Math.max.apply(Math, cases_no_Nan), "end": 1.1*Math.max.apply(Math, cases_no_Nan)})
            
                            x_range.setv({"start": Math.min.apply(Math, new_date), "end": 1.0001*Math.max.apply(Math, new_date)})
            
                            title.text = "Evolution du nombre de cas en " + country
            
                            source.change.emit();
            
            
                            // change value of predictions
            
                            button_click_count.data.clicks = 0
            
                            median_prediction.visible = false
                            band_low.visible = false
                            band_high.visible = false
                            prediction_cases_line.visble = false
            
                            var location = source_all_prediction.data['location']
                            var date = source_all_prediction.data['date']
                            var quantile_1 = source_all_prediction.data['25%']
                            var quantile_2 = source_all_prediction.data['50%']
                            var quantile_3 = source_all_prediction.data['75%']
                            var new_cases = source_all_prediction.data['derivative']
            
            
                            var new_date = []
                            var new_quantile_1 = []
                            var new_quantile_2 = []
                            var new_quantile_3 = []
                            var new_new_cases = []
            
                            for(var i=0; i < quantile_1.length; i++){
                                if(location[i]==country){
                                    new_date.push(date[i])
                                    new_quantile_1.push(quantile_1[i]);
                                    new_quantile_2.push(quantile_2[i]);
                                    new_quantile_3.push(quantile_3[i]);
                                    new_new_cases.push(new_cases[i]);
                                }
                            }   
            
                            source_prediction.data['date']=new_date
                            source_prediction.data['25%']=new_quantile_1;
                            source_prediction.data['50%']=new_quantile_2;
                            source_prediction.data['75%']=new_quantile_3;
                            source_prediction.data['derivative']=new_new_cases;
            
                            source_prediction.change.emit();
            
                            """)

    callback_button = bkm.CustomJS(args=dict(y_axis=p.left, title=p.title), code=
    """
    console.log(y_axis)
    y_axis = LogAxis()
    """)

    select.js_on_change('value', callback)
    button_log.js_on_click(callback_button)

    callback_button = bkm.CustomJS(
        args=dict(source=source, source_prediction=source_prediction, source_all_prediction=source_all_prediction,
                  select=select,
                  button_prediction=button_prediction, median_prediction=median_prediction, band_low=band_low,
                  prediction_cases_line=prediction_cases_line,
                  band_high=band_high, button_click_count=button_click_count,
                  x_range=p.x_range, y_range_left=p.y_range,
                  y_range_right=p.extra_y_ranges['Number of deaths']), code=
        """
                                   // function to get unique value of an array
                                   const unique = (value, index, self) => {
                                       return self.indexOf(value) === index
                                   }
                       
                                   var date = source.data['date'];
                                   var total_cases = source.data['total_cases'];
                                   var new_cases = source.data['new_cases'];
                       
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
                                           y_range_right.setv({"start": -0.05*Math.max.apply(Math, new_cases_no_Nan) * Math.max.apply(Math, total_cases_prediction)/Math.max.apply(Math, cases_no_Nan),
                                                               "end": 1.1*Math.max.apply(Math, new_cases_no_Nan) * Math.max.apply(Math, total_cases_prediction)/Math.max.apply(Math, cases_no_Nan)})
                       
                                           x_range.setv({"start": Math.min.apply(Math, date_prediction), "end": 1.0001*Math.max.apply(Math, date_prediction)})
                                       }
                                       else{
                                           median_prediction.visible = false
                                           band_low.visible = false
                                           band_high.visible = false
                                           prediction_cases_line.visble = false
                       
                                           y_range_left.setv({"start": -0.05*Math.max.apply(Math, cases_no_Nan), "end": 1.1*Math.max.apply(Math, cases_no_Nan)})
                                           y_range_right.setv({"start": -0.05*Math.max.apply(Math, new_cases_no_Nan), "end": 1.1*Math.max.apply(Math, new_cases_no_Nan)})
                                           x_range.setv({"start": Math.min.apply(Math, date), "end": 1.0001*Math.max.apply(Math, date)})
                       
                                       }
                                   }
                       
                       
                                   """)

    button_prediction.js_on_click(callback_button)
    p.legend.location = "top_left"
    p.legend.click_policy = "mute"

    html = file_html(bkm.Column(bkm.Row(select, button_prediction), p,
                                sizing_mode='stretch_width'), Resources(mode='cdn'), "plot")


    html = html.replace("<!DOCTYPE html>", " ")

    with open("plot.html", 'w') as f:
        f.write(html)


    bashCommand = "mv plot.html " + str(includes_path) + "/plot.html"
    subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)




