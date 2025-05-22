#!/usr/bin/env python
# python script for Aethalometer files files
#
# Aethalometer(datafile, model): Object for to contain datafiles (models 'AE33' or 'AE31')
#                                self.df contains a datetime indexed dataframe.
#                                The object returns dataframe subset with the function getSubset(self, start, end),
#                                where 'start' and 'end' are datetime values 
# create_plot(y):                function can be used to plot the data
#                                (one wavelength, use BC6 for eBC at 880nm)
# calculate_intervals_csv(intervalfile, data): calculates the mean BC value
#                                (all wavelengths) for time intervals
#                                defined on a intervalfile.
#                                'data' is an object capable of returning a dataframe subset via self.getSubset() function.
#                                The dataframe index musst be a 'Datetime'.
# def calculate_hourly_intervals(data, interval = 1, decimals = 0):
#                                Calculate hourly averaging groups, the interval variable sets the number of hours.
#                                e.g. 1 for each hour, or 4 for every 4 hours.
#                                'data' is an object capable of returning a dataframe subset via self.getSubset() function.
#                                The dataframe index musst be a 'Datetime'.
# def calculate_minutely_intervals(data, interval = 1, decimals = 0):
#                                Calculate hourly averaging groups, the interval variable sets the number of hours.
#                                e.g. 1 for each minute, or 30 for every 1/2 hour.
#                                'data' is an object capable of returning a dataframe subset via self.getSubset() function.
#                                The dataframe index musst be a 'Datetime'.
# def calculate_secondly_intervals(data, interval = 10, decimals = 0):
#                                Calculate hourly averaging groups, the interval variable sets the number of hours.
#                                e.g. 10 for every 10 seconds.
#                                'data' is an object capable of returning a dataframe subset via self.getSubset() function.
#                                The dataframe index musst be a 'Datetime'.

import configparser, argparse # for argument parsing
from dateutil.parser import parse
import sys, time, os, glob
from dateutil import rrule
from datetime import datetime, timedelta
import platform

import pandas as pd
from pandas.plotting import register_matplotlib_converters

import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

def my_date_formater(ax, delta):
    if delta.days < 3:
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.grid(True, which='minor')
        ax.tick_params(axis="x", which="major", pad=15)
        if delta.days < 0.75:
            ax.xaxis.set_minor_locator(mdates.HourLocator())
        if delta.days < 1:
            ax.xaxis.set_minor_locator(mdates.HourLocator((0,3,6,9,12,15,18,21,)))
        else:
            ax.xaxis.set_minor_locator(mdates.HourLocator((0,6,12,18,)))
    elif delta.days < 8:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%a %d'))
        ax.xaxis.grid(True, which='minor')
        ax.tick_params(axis="x", which="major", pad=15)
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.set(xlabel='date')
    else:
        xtick_locator = mdates.AutoDateLocator()
        xtick_formatter = mdates.AutoDateFormatter(xtick_locator)
        xtick_formatter.scaled[30.] = FuncFormatter(my_days_format_function)
        xtick_formatter.scaled[1.] = FuncFormatter(my_days_format_function)
        ax.xaxis.set_major_locator(xtick_locator)
        ax.xaxis.set_major_formatter(xtick_formatter)
        ax.set(xlabel='date')

def my_days_format_function(x, pos=None):
    dt = mdates.num2date(x)
    if pos == 0:
        fmt = '%b %d\n%Y'
    else:
        # Use platform-specific day formatting
        if platform.system() == 'Windows':
            fmt = '%b %#d'
        else:
            fmt = '%b %-d'
    label = dt.strftime(fmt)
    return label
    
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

def minute_rounder(t):
    # Rounds to nearest hour by adding a timedelta minute if seconds >= 30
    return (t.replace(second=0, microsecond=0, minute=t.minute, hour=t.hour)
               +timedelta(minutes=t.second//30))

def create_plot(y, x=None, yunits='ng/m$^3$', title="Aethalometer", ytitle='eBC'):
    plt.style.use('ggplot')
    register_matplotlib_converters()
    
    # definitions for the axes
    left, width = 0.1, 0.7
    bottom, height = 0.15, 0.75
    spacing = 0.005
    box_width = 1 - (1.5*left + width + spacing)

    rect_scatter = [left, bottom, width, height]
    rect_box = [left + width + spacing, bottom, box_width, height]

    # start with a rectangular Figure
    box = plt.figure("boxplot", figsize=(12, 6))

    ax_scatter = plt.axes(rect_scatter)
    ax_scatter.tick_params(direction='in', top=True, right=True)
    ax_box = plt.axes(rect_box)
    ax_box.tick_params(direction='in', labelleft=False, labelbottom=False)

    # the scatter plot:
    if x==None:
        ax_scatter.plot(y) # change plot type to scatter to have markers
        tdelta = y.index.max() - y.index.min()
    else:
        ax_scatter.plot(x, y) # change plot type to scatter to have markers
        tdelta = x.max() - x.min()
    ax_scatter.set(xlabel='date', ylabel=ytitle + ' (' + yunits + ')', title=title)
    my_date_formater(ax_scatter, tdelta)

    # now determine nice limits by hand:
    binwidth = 0.25
    lim0 = y.min()
    lim1 = y.max()
    if x==None:
        tlim0 = y.index.min()
        tlim1 = y.index.max()
    else:
        tlim0 = x.min()
        tlim1 = x.max()
    extra_space = (lim1 - lim0)/10
    extra_t = (tlim1 - tlim0)/10
    ax_scatter.set_xlim((tlim0-extra_t, tlim1+extra_t))
    ax_scatter.set_ylim((lim0-extra_space, lim1+extra_space))

    meanpointprops = dict(marker='D')
    ax_box.boxplot(y.dropna(), showmeans=True, meanprops=meanpointprops)
    ax_box.set_ylim(ax_scatter.get_ylim())
    mu = y.mean()
    sigma = y.std()
    text = r'$\mu={0:.2f},\ \sigma={1:.3f}$'.format(mu, sigma)
    ax_box.text(1, lim1 + extra_space/2, text, horizontalalignment="center", verticalalignment="center")
    
    plt.show()
    plt.close()

def calculate_intervals_csv(intervalfile, data, decimals = 0):
    df = pd.read_csv(intervalfile,
                     index_col = False,
                     parse_dates=['start','end'])
    for index, row in df.iterrows():
        subset = data.getSubset(row['start'], row['end'])
        for key, value in subset.mean().round(decimals).items():
            df.loc[index, key] = value
    df = df.set_index('end')
    return df

def calculate_hourly_intervals(data, interval = 1, decimals = 0):
    df = pd.DataFrame(columns=['start','end'])
    tmin = hour_rounder(data.df.first_valid_index())
    tmax = hour_rounder(data.df.last_valid_index()) - timedelta(hours=1)
    for dt in rrule.rrule(rrule.HOURLY, interval = interval, dtstart=tmin, until=tmax):
        start = dt
        end = dt+timedelta(hours=1)
        subset = data.getSubset(start, end)
        index = len(df)
        df.loc[index, 'start'] = start
        df.loc[index, 'end'] = end
        for key, value in subset.mean().round(decimals).items():
            df.loc[index, key] = value
    df = df.set_index('end')
    return df

def calculate_minutely_intervals(data, interval = 1, decimals = 0):
    df = pd.DataFrame(columns=['start','end'])
    tmin = minute_rounder(data.df.first_valid_index())
    tmax = minute_rounder(data.df.last_valid_index()) - timedelta(minutes=1)
    for dt in rrule.rrule(rrule.MINUTELY, interval = interval, dtstart=tmin, until=tmax):
        start = dt
        end = dt+timedelta(minutes=1)
        subset = data.getSubset(start, end)
        index = len(df)
        df.loc[index, 'start'] = start
        df.loc[index, 'end'] = end
        for key, value in subset.mean().round(decimals).items():
            df.loc[index, key] = value
    df = df.set_index('end')
    return df

def calculate_secondly_intervals(data, interval = 10, decimals = 0):
    df = pd.DataFrame(columns=['start','end'])
    tmin = minute_rounder(data.df.first_valid_index())
    tmax = minute_rounder(data.df.last_valid_index()) - timedelta(minutes=1)
    for dt in rrule.rrule(rrule.SECONDLY, interval = interval, dtstart=tmin, until=tmax):
        start = dt
        end = dt+timedelta(minutes=1)
        subset = data.getSubset(start, end)
        index = len(df)
        df.loc[index, 'start'] = start
        df.loc[index, 'end'] = end
        for key, value in subset.mean().round(decimals).items():
            df.loc[index, key] = value
    df = df.set_index('end')
    return df   

class Aethalometer(object):
    def __init__(self, datafile, model = 'AE33'): # datafile is a valid filepointer
        AE33 = [
            'Date',
            'Time',
            'Timebase',
            'RefCh1',
            'Sen1Ch1',
            'Sen2Ch1',
            'RefCh2',
            'Sen1Ch2',
            'Sen2Ch2',
            'RefCh3',
            'Sen1Ch3',
            'Sen2Ch3',
            'RefCh4',
            'Sen1Ch4',
            'Sen2Ch4',
            'RefCh5',
            'Sen1Ch5',
            'Sen2Ch5',
            'RefCh6',
            'Sen1Ch6',
            'Sen2Ch6',
            'RefCh7',
            'Sen1Ch7',
            'Sen2Ch7',
            'Flow1',
            'Flow2',
            'FlowC',
            'Pressure',
            'Temperature',
            'BB',
            'ContTemp',
            'SupplyTemp',
            'Status',
            'ContStatus',
            'DetectStatus',
            'LedStatus',
            'ValveStatus',
            'LedTemp',
            'BC11',
            'BC12',
            'BC1',
            'BC21',
            'BC22',
            'BC2',
            'BC31',
            'BC32',
            'BC3',
            'BC41',
            'BC42',
            'BC4',
            'BC51',
            'BC52',
            'BC5',
            'BC61',
            'BC62',
            'BC6',
            'BC71',
            'BC72',
            'BC7',
            'K1',
            'K2',
            'K3',
            'K4',
            'K5',
            'K6',
            'K7',
            'TapeAdvCount',
            'ID_com1',
            'ID_com2',
            'ID_com3']

        AE31 = [
            'Date',
            'Time',
            'BC1',
            'BC2',
            'BC3',
            'BC4',
            'BC5',
            'BC6',
            'BC7',
            'vflow',
            'Sample zero signal 1',
            'sensing beam signal 1',
            'reference zero signal 1',
            'reference beam signal 1',
            'fra 1',
            'optical attenuation 1',
            'Sample zero signal 2',
            'sensing beam signal 2',
            'reference zero signal 2',
            'reference beam signal 2',
            'fra 2',
            'optical attenuation 2',
            'Sample zero signal 3',
            'sensing beam signal 3',
            'reference zero signal 3',
            'reference beam signal 3',
            'fra 3',
            'optical attenuation 3',
            'Sample zero signal 4',
            'sensing beam signal 4',
            'reference zero signal 4',
            'reference beam signal 4',
            'fra 4',
            'optical attenuation 4',
            'Sample zero signal 5',
            'sensing beam signal 5',
            'reference zero signal 5',
            'reference beam signal 5',
            'fra 5',
            'optical attenuation 5',
            'Sample zero signal 6',
            'sensing beam signal 6',
            'reference zero signal 6',
            'reference beam signal 6',
            'fra 6',
            'optical attenuation 6',
            'Sample zero signal 7',
            'sensing beam signal 7',
            'reference zero signal 7',
            'reference beam signal 7',
            'fra 7',
            'optical attenuation 7',
            'massfl'
            ]
        
        self.BCKeys = ['BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7']
        self.BCKey = 'BC6'

        if model == 'AE33':
            columns = AE33
            separator = " "
            skiprows = 8
            append_text = ""
            self.BCKeys.append('BB')
        elif model == 'AE31':
            columns = AE31
            separator = ","
            skiprows = 0
            append_text = ":00"
        else:
            raise Exception("Aethalometer model {} unknown".format(model)) 


        self.units = {
            'Timebase': 'seconds',
            'Flow1': 'cc/min',
            'Flow2': 'cc/min',
            'FlowC': 'cc/min',
            'Pressure': 'Pa',
            'Temperature': '$^\circ$C',
            'BB': '%',
            'ContTemp': '$^\circ$C',
            'SupplyTemp': '$^\circ$C',
            'BC11': 'ng/m$^3$',
            'BC12': 'ng/m$^3$',
            'BC1': 'ng/m$^3$',
            'BC21': 'ng/m$^3$',
            'BC22': 'ng/m$^3$',
            'BC2': 'ng/m$^3$',
            'BC31': 'ng/m$^3$',
            'BC32': 'ng/m$^3$',
            'BC3': 'ng/m$^3$',
            'BC41': 'ng/m$^3$',
            'BC42': 'ng/m$^3$',
            'BC4': 'ng/m$^3$',
            'BC51': 'ng/m$^3$',
            'BC52': 'ng/m$^3$',
            'BC5': 'ng/m$^3$',
            'BC61': 'ng/m$^3$',
            'BC62': 'ng/m$^3$',
            'BC6': 'ng/m$^3$',
            'BC71': 'ng/m$^3$',
            'BC72': 'ng/m$^3$',
            'BC7': 'ng/m$^3$',
            'vflow': 'lpm',     #AE31
            'massfl': 'lpm'     #AE31
            }

        self.wavelengths = {
            'BC1': 370,
            'BC2': 470,
            'BC3': 520,
            'BC4': 590,
            'BC5': 660,
            'BC6': 880,
            'BC7': 950
            }

        #Date(yyyy/MM/dd); Time(hh:mm:ss)
        self.df = pd.read_csv(
            datafile,               # relative python path to subdirectory
            index_col = False,
            names = columns,        # use list of names
            sep=separator,          # Space-separated value file.
            quotechar='"',          # double quote allowed as quote character
            skiprows=skiprows       # Skip the first 8 rows of the file
        )

        #self.df['Datetime'] = pd.to_datetime(self.df['Date'] + " " + self.df['Time'], infer_datetime_format=True)
        self.df['Datetime'] = pd.to_datetime(self.df['Date'] + " " + self.df['Time'])
        self.df = self.df.set_index('Datetime')

    def getSubset(self, start, end):
        return self.df.loc[pd.to_datetime(start):pd.to_datetime(end), self.BCKeys]

if __name__ == "__main__":

    config_file = os.path.abspath(os.path.abspath(os.path.dirname(sys.argv[0])) + "/config.ini")        

    parser = argparse.ArgumentParser(description='Aethalometer datafile utilities')
    parser.add_argument('datafile', metavar='file', type=argparse.FileType('r'),
                        nargs='*', help='List of aethalometer files to be processed. Leave empty for newest file')
    parser.add_argument('--inifile', required=False, dest='INI', default=config_file,
                        help="Path to configuration file ({} if omitted)".format(config_file))
    model_parser = parser.add_mutually_exclusive_group(required=False)
    model_parser.add_argument('--ae33', action='store_true',
                              help='Uses file format for AE33 datafiles (default)')
    model_parser.add_argument('--ae31', action='store_true',
                              help='Uses file format for AE31 datafiles')
    parser.set_defaults(ae33=True)
#    interval_parser = parser.add_mutually_exclusive_group(required=False)
#    interval_parser.add_argument('--iON', action='store_true', dest='interval',
#                                 help='Calculates average values for given intervals, '
#                                      'and plot average values (default)')
#    interval_parser.add_argument('--iOFF', action='store_false', dest='interval',
#                                 help='Do not calculate intervals; plot all datapoints')
#    parser.set_defaults(interval=True)
    parser.add_argument('--freq', required=False, dest='FREQ', choices=['raw', 'hourly', 'minutely', 'secondly'],
                        help='Overides the interval frequency defined in the INI-file. Options are \'raw\' (no data averaging), '
                             '\'hourly\', \'minutely\', \'secondly\'.')
    parser.add_argument('--ilength', required=False, dest='ILEN', type=check_positive,
                        help='Overrides the interval length definded by the INI-file. '
                             'The length used in combination with the --freq variable '
                             '(e.g. INTERVAL: 10 would result in averaging of 10 hours, minutes or seconds)')
    parser.add_argument('--intervals', required=False, dest='CSV', type=argparse.FileType('r'),
                        help='csv file with start and end timestamps columns. '
                             'First row must be the column names (i.e. "start" and "end"). '
                             'Uses hourly, minutely, or secondly intervals if this parameter'
                             'is missing (as defined in config.ini or by --freq).')
    parser.add_argument('--bckey', required=False, dest='bckey',
                        help='Selects BC1 through BC7 (or BB for AE33). '
                             'Default: BC6=880nm')

    args = parser.parse_args()

    if args.ae31:
        print("using AE31 file structure", file=sys.stderr)
        model = 'AE31'
    elif args.ae33:
        print("using AE33 file structure", file=sys.stderr)
        model = 'AE33'

    config_file = args.INI
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        data_path   = eval(config['GENERAL_SETTINGS']['DATA_PATH']) + '/'
        file_mask   = '*' + eval(config['GENERAL_SETTINGS']['FILE_EXT'])
        freq        = eval(config['GENERAL_SETTINGS']['FREQ'])
        interval_l  = eval(config['GENERAL_SETTINGS']['INTERVAL'])
        if not interval_l:
            if freq == 'SECONDLY':
                interval_l = 10
            else:
                interval_l = 1
    else:
        print('Could not find the configuration file {0}'.format(config_file), file=sys.stderr)
        data_path   = os.path.abspath(os.path.abspath(os.path.dirname(sys.argv[0]))) + "/"
        file_mask   = '*.dat'
        freq        = 'HOURLY'
        interval_l  = 1

    if not args.datafile:
        list_of_events = glob.glob(data_path + file_mask) # * means all if need specific format then *.csv
        latest_event = max(list_of_events, key=os.path.getctime)
        args.datafile = [open(latest_event, 'r')]

    mydata = False
    for f in args.datafile:
        print('loading file: {0}'.format(f.name), file=sys.stderr)
        if not mydata:
            mydata = Aethalometer(f, model = model)
        else:
            #mydata.df = mydata.df.append(Aethalometer(f, model = model).df)
            mydata.df = pd.concat([mydata.df, Aethalometer(f, model = model).df])            
            
    if args.bckey:
        mydata.BCKey = args.bckey.upper()
        
    if args.FREQ == 'raw':
        interval = False             # use raw data
    elif args.FREQ:                  # overide INI-file averaging frequency   
        freq = args.FREQ.upper()
        interval = True
    else:
        interval = True              # use intervals defined in INI-file
        
    if args.ILEN:
        interval_l = int(args.ILEN)  # overide INI-file averaging intervals   
        

#    if args.interval:
    if interval:
        ### Output the csv file with the average values per interval
        if args.CSV:
            interval_df = calculate_intervals_csv(args.CSV, mydata)
        else:
            if freq == 'SECONDLY':
                interval_df = calculate_secondly_intervals(mydata, interval = interval_l)
            elif freq == 'MINUTELY':
                interval_df = calculate_minutely_intervals(mydata, interval = interval_l)
            else:
                interval_df = calculate_hourly_intervals(mydata, interval = interval_l)
        columns = interval_df.columns.values
        print("end," + ",".join(columns))
        units = (mydata.units[key] for key in columns if key in mydata.units)
        print("-,-," + ",".join(units))
        print(interval_df.to_csv(header=False))
        y = interval_df[mydata.BCKey]
    else:
        y = mydata.df[mydata.BCKey]

    plotTitle = "Aethalometer Model " + model
    if mydata.wavelengths.get(mydata.BCKey):
        plotTitle = plotTitle + " ($\lambda=$" + str(mydata.wavelengths.get(mydata.BCKey)) + "nm)"
        ytitle="Equivalent Black Carbon"
    else:
        ytitle = "Biomass Burning Fraction"
    create_plot(y, yunits=mydata.units.get(mydata.BCKey), title=plotTitle, ytitle=ytitle)
