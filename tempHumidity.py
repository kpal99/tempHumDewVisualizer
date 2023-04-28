#!/usr/bin/env python
# coding: utf-8
import sys
import datetime
import numpy as np
import pandas as pd
import warnings
from bokeh.io import show, output_notebook
from bokeh.plotting import figure
#from bokeh.models import RELATIVE_DATETIME_CONTEXT
from bokeh.models import DatetimeTickFormatter, Range1d, LinearAxis
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.layouts import gridplot
warnings.filterwarnings("ignore")

def create_fig(df, date):
# Create a plot with interactive tools
    fig = figure(x_axis_type='datetime',
                 width=900,
                 height=450,
                 title="Temperature and Humidity",
                 tools="wheel_zoom,box_zoom,reset,save,pan")

# Customize the x-axis format
    fig.xaxis.formatter = DatetimeTickFormatter(
        microseconds=["%fus"],
        milliseconds=["%3Nms", "%S.%3Ns"],
        seconds=["%d %b %H:%M:%S"],
        minsec=["%d %b %H:%M:%S"],
        minutes=["%d %b %H:%M"],
        hourmin=["%d %b %H:%M"],
        hours=["%d %b %H:%M"],
        days=["%d %b"],
        months=["%b %Y"],
        years=["%Y"])
#fig.xaxis.formatter.context = RELATIVE_DATETIME_CONTEXT()

# Set the x and y axis label font style to normal
    fig.xaxis.axis_label_text_font_style = 'normal'
    fig.yaxis.axis_label_text_font_style = 'normal'
# Set the x and y labels
    fig.xaxis.axis_label="Datetime"
    fig.yaxis.axis_label="Temperature (°C)"

# Setting the second y axis range name and range
    fig.extra_y_ranges={"humid": Range1d(start=int(min(df['Humidity'])/10)*10, end=int(max(df['Humidity'])/10 + 1)*10)}
    fig.y_range=Range1d(start=int(min(df['Temperature'])/10)*10, end=int(max(df['Temperature'])/10 + 1)*10)

# Adding the second axis to the plot
    fig.add_layout(LinearAxis(y_range_name="humid",
                              axis_label="Humidity (%)",
                              axis_label_text_color='red',
                              axis_line_color='red',
                              major_label_text_color='red',
                              major_tick_line_color='red',
                              minor_tick_line_color='red',
                              axis_label_text_font_style='normal'), 'right')


# Add a line glyph to the figure
    fig.line(x=df.index, y=df['Temperature'], line_width=1, line_color='black', legend_label="Temperature", muted_alpha=0.1)
    fig.line(x=df.index, y=df['Humidity'], y_range_name="humid", line_width=1, line_color='red', legend_label="Humidity", muted_alpha=0.1)
    fig.legend.orientation="horizontal"
    fig.legend.click_policy="mute"

    return fig


def create_fig_avg(df1, date):
# Create a plot with interactive tools
    fig1 = figure(x_axis_type='datetime',
                 width=900,
                 height=450,
                 title="Temperature and Humidity (10 min avg)",
                 tools="wheel_zoom,box_zoom,reset,save,pan")

# Customize the x-axis format
    fig1.xaxis.formatter = DatetimeTickFormatter(
        microseconds=["%fus"],
        milliseconds=["%3Nms", "%S.%3Ns"],
        seconds=["%d %b %H:%M:%S"],
        minsec=["%d %b %H:%M:%S"],
        minutes=["%d %b %H:%M"],
        hourmin=["%d %b %H:%M"],
        hours=["%d %b %H:%M"],
        days=["%d %b"],
        months=["%b %Y"],
        years=["%Y"])
#fig.xaxis.formatter.context = RELATIVE_DATETIME_CONTEXT()

# Set the x and y axis label font style to normal
    fig1.xaxis.axis_label_text_font_style = 'normal'
    fig1.yaxis.axis_label_text_font_style = 'normal'
# Set the x and y labels
    fig1.xaxis.axis_label="Datetime"
    fig1.yaxis.axis_label="Temperature (°C)"

# Setting the second y axis range name and range
    fig1.extra_y_ranges={"humid": Range1d(start=int(min(df1['Humidity'])/10)*10, end=int(max(df1['Humidity'])/10 + 1)*10)}
    fig1.y_range=Range1d(start=int(min(df1['Temperature'])/10)*10, end=int(max(df1['Temperature'])/10 + 1)*10)

# Adding the second axis to the plot
    fig1.add_layout(LinearAxis(y_range_name="humid",
                              axis_label="Humidity (%)",
                              axis_label_text_color='red',
                              axis_line_color='red',
                              major_label_text_color='red',
                              major_tick_line_color='red',
                              minor_tick_line_color='red',
                              axis_label_text_font_style='normal'), 'right')


# Add a line glyph to the figure
    fig1.line(x=df1.index, y=df1['Temperature'], line_width=1, line_color='black', legend_label="Temperature", muted_alpha=0.1)
    fig1.line(x=df1.index, y=df1['Humidity'], y_range_name="humid", line_width=1, line_color='red', legend_label="Humidity", muted_alpha=0.1)
    fig1.legend.orientation="horizontal"
    fig1.legend.click_policy="mute"

    return fig1

def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    #Kindly put exported filename here
    print(filename)

    df = pd.read_csv(filename, skiprows=11, delimiter='\t', header=None, names=['NO', 'Temperature', 'Humidity', 'DateTime'])
    df = df.drop(columns=['NO'])
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d-%m-%y/%H:%M:%S ')
    df = df.set_index('DateTime')

    df['Temperature'] = np.where(df['Temperature'] > 100, 100, df['Temperature'])
    df['Humidity'] = np.where(df['Humidity'] > 100, 100, df['Humidity'])

    # group the data by the date column
    grouped_data = df.groupby(pd.Grouper(freq='D', level=0))

    for date, group in grouped_data:
    # do something with the data for this day
        print(f"Data for {date.date()}:")
        print(group)

        # get the last timestamp from the index
        last_timestamp = group.index[-1]
        # extract the time component
        last_time = last_timestamp.time()
        # compare the time to 23:30:00
        if last_time > datetime.time(hour=23, minute=00, second=0):
            print("Last entry is after 23:30:00")
        else:
            print("Last entry is before or at 23:30:00")

    return

    time_value = 15
    #resampling data to shallow the fluctuations
    df1 = df.resample(f"{time_value}T").mean()

    fig = create_fig(df, time_value)
    fig1 = create_fig_avg(df1, time_value)

    grid = gridplot([[fig1], [fig]])
    with open('output_files/7-days.html', 'w') as f:
        f.write(file_html(grid, CDN, "title"))

if __name__ == '__main__':
    main()
