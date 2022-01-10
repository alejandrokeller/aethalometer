# Aethalometer Visualization Scripts
## Python script visualization and data-averaging of Aethalometer datafiles (AE31 and AE33)

### **Installation**
1. Clone repository:
```bash
$ git clone https://github.com/alejandrokeller/aethalometer
```
2. Travel to cloned folder:
```bash
$ cd aethalometer
```
3. Create a local config.ini file:
```bash
$ cp config config.ini
```
4. Edit the config.ini file by adding the default data path and file extension (e.g. ".dat").
The script searches this path for the latest file if it is used used without a file argument.
The 'FREQ' option defines the default generated averaging interval (i.e. HOURLY, MINUTELY, SECONDLY). 'INTERVAL' defines the interval length used in combination with the 'FREQ' variable (e.g. INTERVAL: 10 would result in averaging of 10 hours, minutes or seconds).
The script outputs raw data if --ioff is used and no --intervals CSV file defined.

5. Install python requirements:
```bash
$ pip install -r requirements.txt
```

### **Usage**

`aeth.py [-h] [--inifile INI] [--ae33 | --ae31]
               [--freq {raw,hourly,minutely,secondly}] [--ilength ILEN]
               [--intervals CSV] [--bckey BCKEY]
               [file [file ...]]`
               
| Argument | Description |
| --- | --- |
|-h, --help     | show help message and exit|
|--inifile INI  | Path to an alternative configuration file|
|--ae33         | Uses file format for AE33 datafiles (default)|
|--ae31         | Uses file format for AE31 datafiles|
|--freq         | Overides the interval frequency defined in the INI-file. Options are 'raw' (no data averaging), 'hourly', 'minutely', 'secondly'.|
|--ilength      | Overrides the interval length definded by the INI-file. The length used in combination with the --freq variable (e.g. INTERVAL: 10 would result in averaging of 10 hours, minutes or seconds)|
|--intervals CSV| csv file with start and end timestamps columns. First row must be the column names (i.e. "start" and "end"). Uses hourly, minutely, or secondly intervals if this parameteris missing (as defined in config.ini)|
|--bckey BCKEY  | Selects the variable for the generated plot. Possible values: BC1 through BC7 (and BB for AE33). Default: BC6=880nm|
| file(s)       | path to file(s) to be plotted. If several files are given, they will be joined into a single dataframe. If empty, the script looks for the latest file in the default data directory defined in the inifile or by --freq.|  

The calculated averaged interval-data for BC1-BC7 and BB are printed by the command. Use `>` to save the data:
```bash
$ aeth.py sample.dat > averaged_data.csv
```

The plots, generated using `matplotlib`, are *NOT* automatically saved. Use the GUI for text editing and saving. Several formats are possible.

Hourly interval example:
![Aethalometer data, hourly](boxplot.png)

Minutely interval example:
![Aethalometer data, minutely](boxplot-minutes.png)

### Object and functions defined in the aeth.py

| Argument | Description |
| --- | --- |
| Aethalometer(datafile, model) | Object for importing and containing Aethalometer datafiles (models 'AE33' or 'AE31') |
| create_plot(y)                | Function that creates a box-plot. Optional parameters are x (default None, in this case the 'y' Dataframe index is used as 'x'), yunits ('ng/m$^3$'), \[plot\] title ("Aethalometer"), and ytitle ('eBC'). |
| calculate_intervals_csv(intervalfile, data)| calculates the average values based on intervals defined by a CSV file. 'data' is an object capable of returning a dataframe subset via self.getSubset() function. The dataframe index musst be a 'Datetime'. |
| calculate_hourly_intervals(data, interval = 1, decimals = 0) | Calculate hourly averaging groups, the interval variable sets the number of hours. e.g. 1 for each hour, or 4 for every 4 hours. 'data' is an object capable of returning a dataframe subset via self.getSubset() function. The dataframe index musst be a 'Datetime'. |
| calculate_minutely_intervals(data, interval = 1, decimals = 0) | Calculate hourly averaging groups, the interval variable sets the number of hours. e.g. 1 for each minute, or 30 for every 1/2 hour. 'data' is an object capable of returning a dataframe subset via self.getSubset() function.The dataframe index musst be a 'Datetime'. |
| calculate_secondly_intervals(data, interval = 10, decimals = 0) | Calculate hourly averaging groups, the interval variable sets the number of hours. e.g. 10 for every 10 seconds. 'data' is an object capable of returning a dataframe subset via self.getSubset() function. The dataframe index musst be a 'Datetime'. |
