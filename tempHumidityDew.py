#!/usr/bin/env python
# coding: utf-8
import sys
import datetime
import os
import numpy as np
import pandas as pd
import warnings
from bokeh.io import show, output_notebook, export_png
from bokeh.plotting import figure
#from bokeh.models import RELATIVE_DATETIME_CONTEXT
from bokeh.models import DatetimeTickFormatter, Range1d, LinearAxis
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.layouts import gridplot
warnings.filterwarnings("ignore")

def create_fig(df, title_str):
# Create a plot with interactive tools
    fig = figure(x_axis_type='datetime',
                 width=900,
                 height=450,
                 title=title_str,
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

    #find min/max of Dewpoint and Temperature combined
    miny1=min([min(df['Temperature']), min(df['Dewpoint'])])
    maxy1=max([max(df['Temperature']), max(df['Dewpoint'])])

    # Setting the second y axis range name and range
    #Here we are making the range in multiple of 10's by int(num/10)*10 and int(num/10 + 1) * 10
    fig.extra_y_ranges={"humid": Range1d(start=int(min(df['Humidity'])/10)*10, end=int(max(df['Humidity'])/10 + 1)*10),
                        "dew": Range1d(start=int(miny1/10)*10, end=int(maxy1/10 + 1)*10)}
    fig.y_range=Range1d(start=int(miny1/10)*10, end=int(maxy1/10 + 1)*10)

    # Adding the second axis to the plot
    fig.add_layout(LinearAxis(y_range_name="humid",
                              axis_label="Humidity (%)",
                              axis_label_text_color='red',
                              axis_line_color='red',
                              major_label_text_color='red',
                              major_tick_line_color='red',
                              minor_tick_line_color='red',
                              axis_label_text_font_style='normal'), 'right')
    fig.add_layout(LinearAxis(y_range_name="dew",
                              axis_label="Dewpoint (°C)",
                              axis_label_text_color='blue',
                              axis_line_color=None,
                              major_label_text_color=None,
                              major_tick_line_color=None,
                              minor_tick_line_color=None,
                              axis_label_text_font_style='normal'), 'left')


    # Add a line glyph to the figure
    fig.line(x=df.index, y=df['Temperature'], line_width=1, line_color='black', legend_label="Temperature", muted_alpha=0.1)
    fig.line(x=df.index, y=df['Dewpoint'], line_width=1, line_color='blue', legend_label="Dewpoint", muted_alpha=0.1)
    fig.line(x=df.index, y=df['Humidity'], y_range_name="humid", line_width=1, line_color='red', legend_label="Humidity", muted_alpha=0.1)
    fig.legend.orientation="horizontal"
    fig.legend.click_policy="mute"

    return fig

def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]

    # Read in the df from the file
    df = pd.read_csv(filename, sep=';', header=None, skiprows=2)

    # Parse the dates and times into a single DateTime column
    df[0] = pd.to_datetime(df[0] + ' ' + df[1], format='#%Y/%m/%d %H:%M:%S')

    # Rename the columns and drop the original date and time columns
    df = df.drop(columns=[1])
    df = df.drop(columns=[5])
    df.columns = ['DateTime', 'Temperature', 'Humidity', 'Dewpoint']

    # Convert temperature, humidity, and dewpoint columns to numeric
    df['Temperature'] = pd.to_numeric(df['Temperature'].str.replace('C', ''))
    df['Humidity'] = pd.to_numeric(df['Humidity'].str.replace('%', ''))
    df['Dewpoint'] = pd.to_numeric(df['Dewpoint'].str.replace('D', '').str.replace('C', ''))

    # Set the DateTime column as the index
    df = df.set_index('DateTime')

    # group the data by the date column
    grouped_data = df.groupby(pd.Grouper(freq='D', level=0))
    for i, (date, group) in enumerate(grouped_data):
        date_value = str(date.date())

        output_file = 'output_files/tempHumidityDew_' + date_value + '.html'
        output_file_png = 'output_files/tempHumidityDew_' + date_value + '.png'

        if os.path.exists(output_file):
            continue

        #check timestamp for last group
        if i == len(grouped_data) - 1:
            # get the last timestamp from the index
            last_timestamp = group.index[-1]
            # extract the time component
            last_time = last_timestamp.time()
            # compare the time to 23:30:00
            if last_time < datetime.time(hour=23, minute=00, second=0):
                continue

        #save group to csv
        group.to_csv('output_files/tempHumidityDew_' + date_value + '.csv', sep=';')
        print(f"File output_files/tempHumidityDew_{date_value}.csv created")

        time_value = 10
        #resampling data to shallow the fluctuations
        group1 = group.resample(f"{time_value}T").mean()

        fig = create_fig(group,"Temperature, Dewpoint and Humidity " + date_value)
        fig1 = create_fig(group1, "Temperature, Dewpoint and Humidity " + date_value + " (" + str(time_value) + " min avg)")

        # save the plot as a PNG file
        export_png(fig1, filename=output_file_png)
        print(f"File {output_file_png} created")

        grid = gridplot([[fig1], [fig]])
        with open(output_file, 'w') as f:
            f.write(file_html(grid, CDN, date_value))
            print(f"File {output_file} created")
            print()

if __name__ == '__main__':
    main()
