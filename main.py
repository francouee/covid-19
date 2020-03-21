import numpy as np
import pandas as pd
import pathlib

import bokeh.plotting as bkp
import bokeh.models as bkm
from bokeh.io import curdoc
from bokeh.palettes import d3
import subprocess


bashCommand = "rm -rf full_data.csv"
subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

bashCommand = "wget https://covid.ourworldindata.org/data/full_data.csv"
subprocess.call(bashCommand.split(), stdout=subprocess.PIPE)





def get_country(data: pd.DataFrame, location: str):
    """return the projection of the DataFrame with the selected country"""
    return data[data.location == location]


data = pd.read_csv("full_data.csv")
data = data.rename(columns={"Total confirmed cases of COVID-19" : "total_cases"})
data['date'] = data.date.apply(pd.to_datetime)

COLORS = d3['Category10'][10]

tooltips = f"""

    <div>         
        <div>
            <p>
                <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre de cas : </span>
                <span style="font-size: 12px; color: {COLORS[0]}; font-weight: bold;font-family:century gothic;">@total_cases</span>
            <br> 
                <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre de nouveaux cas : </span>
                <span style="font-size: 12px; color: {COLORS[1]}; font-weight: bold;font-family:century gothic;">@new_cases</span>
            <br> 
                <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre de décés : </span>
                <span style="font-size: 12px; color: {COLORS[3]}; font-weight: bold;font-family:century gothic;">@total_deaths</span>
            <br> 
                <span style="font-size: 12px; color: black;font-family:century gothic;">Nombre nouveaux décés : </span>
                <span style="font-size: 12px; color: {COLORS[5]}; font-weight: bold;font-family:century gothic;">@new_deaths</span>
            <br> 
                <span style="font-size: 12px; color: black;font-family:century gothic;">Date : </span>
                <span style="font-size: 12px; color: black; font-weight: bold;font-family:century gothic;">""" + """@date{%D}</span>
            </p>
        </div>
    </div>
    """

hover = bkm.tools.HoverTool(names=['line_total'],
                            tooltips=tooltips,
                            formatters={'@date': 'datetime'},
                            mode='vline'
                            )

source_all = bkm.ColumnDataSource(data)
country = 'South Korea'
source = bkm.ColumnDataSource(get_country(data, country))

panels = []

# for axis_type in ["linear", "log"]:

p = bkp.figure(y_axis_type="linear", x_axis_type='datetime',
               title=f'Evolution du nombre de cas: {country}', x_axis_label='date', y_axis_label='Number of cases',
               sizing_mode='stretch_width', tools=[hover, 'pan', 'wheel_zoom', 'reset'],
               y_range=[-get_country(data, country).total_cases.max() * 0.05,
                        get_country(data, country).total_cases.max() * 1.1])

p.toolbar.active_scroll = p.select_one(bkm.WheelZoomTool)

p.extra_y_ranges = {"Number of deaths": bkm.Range1d(start=-0.05 * get_country(data, country).new_cases.max(),
                                                    end=1.1 * get_country(data, country).new_cases.max())}
p.add_layout(bkm.LinearAxis(y_range_name="Number of deaths", axis_label="new_cases"), 'right')

# --- plot total cases --- #

p.line(source=source, x='date', y='total_cases', name='line_total', color=COLORS[0])
p.circle(source=source, x='date', y='total_cases', color=COLORS[0])

# --- plot new cases --- #

p.vbar(source=source, x='date', top='new_cases', color=COLORS[1], width=50e6, alpha=0.5, name='bar',
       y_range_name="Number of deaths")

# --- plot total death --- #

p.line(source=source, x='date', y='total_deaths', color=COLORS[3], y_range_name="Number of deaths", name='line_death')
p.circle(source=source, x='date', y='total_deaths', color=COLORS[3], y_range_name="Number of deaths")

# --- plot new death --- #

p.vbar(source=source, x='date', top='new_deaths', color=COLORS[5], width=50e6, alpha=0.5,
       y_range_name="Number of deaths")

select = bkm.Select(title="Country: ", value=country, options=list(data.location.unique()))
button_log = bkm.Button(label="Log Scale", button_type='primary')

callback = bkm.CustomJS(args=dict(source=source, source_all=source_all, select=select, x_range=p.x_range,
                                  y_range_left=p.y_range, y_range_right=p.extra_y_ranges['Number of deaths'],
                                  title=p.title), code=
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
            
                        title.text = "Evolution du nombre de cas en " + country
            
                        source.change.emit();
                        """)

callback_button = bkm.CustomJS(args=dict(y_axis=p.left, title=p.title), code=
"""
console.log(y_axis)
y_axis = LogAxis()
""")

select.js_on_change('value', callback)
button_log.js_on_click(callback_button)

curdoc().add_root(bkm.Column(bkm.Row(select), p, sizing_mode='stretch_width'))
curdoc().title = "Covid 19 cases"



