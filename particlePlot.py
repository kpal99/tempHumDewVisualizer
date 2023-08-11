from bokeh.io import show, output_notebook, export_png
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.layouts import gridplot
from collections import defaultdict
import datetime
import numpy as np
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

#Take input alphabet and return index, A = 0
def get_alphabet_index(arg):
    alphabet = arg.upper()
    # Calculate the index of the input alphabet(s)
    index = 0
    for letter in alphabet:
        index = index * 26 + ord(letter) - ord('A') + 1
    return index - 1  # subtract 1 to get 0-based index

def getFileArray(list_):
    grouped_data = defaultdict(list)

    for item in list_:
        parts = item.split('_')
        prefix = parts[0]
        date_str = parts[1].split('.')[0]  # Remove the ".CSV" extension
        date = datetime.datetime.strptime(date_str, '%d%m%Y').date()
        grouped_data[date].append(item)

    return grouped_data

def makedf(filename, cols_num):
# Read in the df from the file
    df = pd.read_csv(filename, sep=',', header=None, skiprows=5, usecols=cols_num)

# Parse the dates and times into a single DateTime column
    df[0] = pd.to_datetime(df[0] + ' ' + df[1], format='%m/%d/%Y %I:%M:%S %p')

# Rename the columns and drop the original date and time columns
    df = df.drop(columns=[1])
    df.columns = ['DateTime', 'Flowrate', '0.3 µm', '0.5 µm', '5 µm']

# # remove commas from the columns
# df['0.3 µm'] = pd.to_numeric(df['0.3 µm'].str.replace(',', ''))
# df['0.5 µm'] = pd.to_numeric(df['0.5 µm'].str.replace(',', ''))
# df['5 µm'] = pd.to_numeric(df['5 µm'].str.replace(',', ''))

# Set the DateTime column as the index
    df = df.set_index('DateTime')
#print(df)
    return df




def makePlots(fileNameArray, date_value):
#Kindly put count type here i.e. raw, ft3, m3
    count_type = 'm3'

    cols_alphabet = ['A','B','E']
    cols_alphabet += ['Q','T','AC']

    cols_num = [get_alphabet_index(x) for x in cols_alphabet]

    from bokeh.io import show, output_notebook
    from bokeh.plotting import figure
#from bokeh.models import RELATIVE_DATETIME_CONTEXT
    from bokeh.models import DatetimeTickFormatter, Range1d, LinearAxis
    warnings.filterwarnings("ignore")

    output_notebook()
# Create a plot with interactive tools
    fig = figure(x_axis_type='datetime',
                 width=900,
                 height=450,
                 title="Particle count",
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
        days=["%d %b %H:%M"],
        months=["%b %Y"],
        years=["%Y"])
#fig.xaxis.formatter.context = RELATIVE_DATETIME_CONTEXT()

# Set the x and y axis label font style to normal
    fig.xaxis.axis_label_text_font_style = 'normal'
    fig.yaxis.axis_label_text_font_style = 'normal'
# Set the x and y labels
    fig.xaxis.axis_label="Datetime"
    if count_type == "raw":
        fig.yaxis.axis_label="Counts / 60s"
    elif count_type == "ft3":
        fig.yaxis.axis_label="Counts / ft³ / 60s"
    elif count_type == "m3":
        fig.yaxis.axis_label="Counts / m³ / 60s"


# Add a line glyph to the figure
    fig.line(x=df.index, y=df['0.3 µm'], line_width=1, line_color='black', legend_label="0.3 µm", muted_alpha=0.1)
    fig.line(x=df.index, y=df['0.5 µm'], line_width=1, line_color='blue', legend_label="0.5 µm", muted_alpha=0.1)
    fig.line(x=df.index, y=df['5 µm'], line_width=1, line_color='red', legend_label="5 µm", muted_alpha=0.1)
    fig.legend.orientation="horizontal"
    fig.legend.click_policy="mute"


# Display the plot in the notebook
    show(fig)

    date_value = "small_30-06_27-06"
    output_file = 'output_files/particlePlot_' + date_value + '.html'
    output_file_png = 'output_files/particlePlot_' + date_value + '.png'

# save the plot as a PNG file
    export_png(fig, filenameBig=output_file_png)
    print(f"File {output_file_png} created")

    with open(output_file, 'w') as f:
        f.write(file_html(fig, CDN, date_value))
        print(f"File {output_file} created")

def main():
    if len(sys.argv) < 3:
        print("f{Usage: python {sys.argv[0]} <csv_files>}")

    fileLists = getFileArray(sys.argv[1:])
    for key in fileLists.keys():
        if len(fileLists[key]) == 2:
            print(fileLists[key], key)
        else:
            print(f"{fileLists[key]} doesn't look okay, SKIPPING")


    # get array of array of files on the basis of dates small/big room


if __name__ == "__main__":
    main()
