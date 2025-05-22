# Aethalometer Visualization Scripts

Python script for visualization and data averaging of Aethalometer data files (models AE31 and AE33).

---

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/alejandrokeller/aethalometer
```

2. Navigate to the cloned folder:
```bash
cd aethalometer
```

3. Create and edit the configuration file:
```bash
cp config config.ini
```
Edit `config.ini` and define:
- `DATA_PATH`: default data directory
- `FILE_EXT`: file extension (e.g., `.dat`)
- `FREQ`: default averaging frequency (`HOURLY`, `MINUTELY`, `SECONDLY`)
- `INTERVAL`: time span used with `FREQ` (e.g., `10` = 10 hours, minutes, or seconds)

If run without specifying a file, the script uses this configuration to locate and process the most recent data file.

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## 🛠️ Usage

```bash
aeth.py [-h] [--inifile INI] [--ae33 | --ae31]
        [--freq {raw,hourly,minutely,secondly}] [--ilength ILEN]
        [--intervals CSV] [--bckey BCKEY]
        [file [file ...]]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `-h`, `--help` | Show help message and exit |
| `--inifile INI` | Path to an alternative `config.ini` file |
| `--ae33` | Use AE33 file format (default) |
| `--ae31` | Use AE31 file format |
| `--freq {raw,hourly,minutely,secondly}` | Override default frequency for averaging |
| `--ilength ILEN` | Set the averaging interval length (in hours, minutes, or seconds) |
| `--intervals CSV` | CSV file with `start` and `end` columns (timestamps); used for custom averaging intervals |
| `--bckey BCKEY` | Selects BC1–BC7 or BB (AE33 only); default is `BC6 = 880nm` |
| `file(s)` | One or more data files to process. If omitted, the latest file in the configured directory will be used. |

### Output

- The script prints averaged data (BC1–BC7, BB) to stdout.
- Use redirection (`>`) to save the output:
```bash
aeth.py sample.dat > averaged_data.csv
```

- Plots are generated using `matplotlib`. **They are not saved automatically** — use the GUI to save in your preferred format.

---

## 📊 Examples

**Hourly interval:**

![Hourly Aethalometer data](boxplot.png)

**Minutely interval:**

![Minutely Aethalometer data](boxplot-minutes.png)

---

## 📦 Objects & Functions Defined in `aeth.py`

| Function / Class | Description |
|------------------|-------------|
| `Aethalometer(datafile, model)` | Class to read and store AE31/AE33 files as a `pandas` DataFrame indexed by `Datetime`. |
| `create_plot(y)` | Generates a boxplot for the selected variable. Optional parameters: `x`, `yunits`, `title`, `ytitle`. |
| `calculate_intervals_csv(intervalfile, data)` | Averages values over intervals defined in a CSV with `start` and `end` columns. |
| `calculate_hourly_intervals(data, interval=1, decimals=0)` | Calculates hourly means (e.g., every 1 or 4 hours). |
| `calculate_minutely_intervals(data, interval=1, decimals=0)` | Calculates minute-level means (e.g., every 1 or 30 minutes). |
| `calculate_secondly_intervals(data, interval=10, decimals=0)` | Calculates second-level means (e.g., every 10 seconds). |

**Note:** All interval functions assume the input object supports `.getSubset(start, end)` and uses a `Datetime` index.
