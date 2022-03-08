# Niimpy

`niimpy` is a Python package for managing individual-level data.  The
best way to describe it is to look at the big picture:

- [koota-server](https://github.com/digitraceslab/koota-server) is a
  platform for collecting data from different sources, managing it for
  users and studies, and downloading it.  Before downloading, it can
  be converted into tabular format.

- Koota can provide data in the form of sqlite databases, which
  provides a nice interface for basic querying but still not enough
  for really efficient use.  You can access these databases using the
  Python `sqlite3` module, the `sqlite3` command line utility,
  `pandas.read_sql`, and many other options.

- `niimpy` can open these databases and provide a querying shortcut
  for basic operations, which saves you from having to write so much
  SQL yourself.

- `niimpy` also provides some more high-level operations, such as
  basic preprocessing/aggregation, visualizing data quality, and other
  transformations so that you can focus on your interesting work.

- ... but *you* need to do the real analysis work.  If you make good,
  generalizable functions, they can be added to `niimpy`.

Table of contents:

- [Installation](#installation)
- [Basic usage](#basic-usage)
  -  [Getting started with location data](#getting-started-with-location-data)
- [Documentation](#documentation)
- [Development](#development)
- [See also](#see-also)

## Installation

- Only supports Python 3 (tested on 3.5 and above)

- This is a normal Python package to install.  It is not currently in
  PyPI, so can be installed manually

  ```
  pip install https://github.com/digitraceslab/niimpy/archive/master.zip
  ```


## Basic usage

First, you need to download the data.  (Note: in normal use, this is
done for you).  You can download in the `sqlite3` format from the
Koota interface and import yourself to sqlite, or use the
`download_sync.sh` script in Koota.

So, then usage is fairly simple:

```
data = niimpy.open('/path/to/database.sqlite')

# Get hourly summaries of MurataBSN data (mean/std/count), hr and rr columns
d = data.hourly(table='MurataBSN', user='rkr561Rkn-3t', columns=['hr', 'rr'])
d.head(5)

                            day  hour  count    hr_mean     hr_std  hr_count       rr_mean    rr_std  rr_count
2017-06-08 21:00:00  2017-06-08    21   3575  52.565145  12.561495      3575      6.165038  2.165948      3555
```

The `hourly` function provides hourly summaries.  The output is always
[pandas]( 2.243038 4.184948 3555) data frames, which are a somewhat
standard way of representing tabular-like data.

There are different functions to provide summaries of the data in
different formats, but it is expected that *you* will be the one doing
the core analysis with your own code.

### Getting started with location data

All of the functions for reading, preprocessing, and feature extraction for location data is in [`location.py`](niimpy/location.py). Currently implemented features are:

- `dist_total`: total distance a person traveled in meter.
- `variance`, `log_variance`: variance is defined as sum of variance in latitudes and longitudes.
- `speed_average`, `speed_variance`, and `speed_max`: statistics of speed (m/s). Speed, if not given, can be calculated by dividing the distance between two consequitive bins by their time difference.
- `n_bins`: number of location bins that a user recorded in dataset.
- `n_static`: number of static points. Static points are defined as bins whose speed is lower than a threshold.
- `n_moving`: number of moving points. Equivalent to `n_bins - n_static`.
- `n_home`: number of static bins which are close to the person's home. Home is defined the place most visited during nights. More formally, all the locations recorded during 12 Am and 6 AM are clusterd and the center of largest cluster is assumed to be home.
- `max_dist_home`: maximum distance from home.
- `n_sps`: number of significant places. All of the static bins are clusterd using DBSCAN algorithm. Each cluster represents a Signicant Place (SP) for a user.
- `n_rare`: number of rarely visited (referred as outliers in DBSCAN).
- `n_transitions`: number of transitions between significant places.
- `n_top1`, `n_top2`, `n_top3`, `n_top4`, `n_top5`: number of bins in the top `N` cluster. In other words, `n_top1` shows the number of times the person has visited the most freqently visited place.
- `entropy`, `normalized_entropy`: entropy of time spent in clusters. Normalized entropy is the entropy divided by the number of clusters.

Usage:

```python
import pandas as pd
import niimpy
import niimpy.location as nilo

CONTROL_PATH = "PATH/TO/CONTROL/DATA"
PATIENT_PATH = "PATH/TO/PATIENT/DATA"

# Read data of control and patients from database
location_control = niimpy.read_sqlite(CONTROL_PATH, table='AwareLocation', add_group='control', tz='Europe/Helsinki')
location_patient = niimpy.read_sqlite(PATIENT_PATH, table='AwareLocation', add_group='patient', tz='Europe/Helsinki')

# Concatenate the two dataframes to have one dataframe
location = pd.concat([location_control, location_patient])

# Remove low-quality and outlier locations
location = nilo.filter_location(location)

# Downsample locations (median filter). Bin size is 10 minute.
location = niimpy.util.aggregate(location, freq='10T', method_numerical='median')
location = location.reset_index(0).dropna()

# Feature extraction
features = nilo.extract_distance_features(location)
```

## Documentation

For now, see the included [docs/Introduction.ipynb] and [docs/Manual.ipynb]
notebooks.

To learn about what converters exist and what they mean, see the
[Koota wiki](https://github.com/digitraceslab/koota-server/wiki), in
particular the data sources section.

## Development

This is a pretty typical Python project with code and documentation as
you might expect.

`requirements-dev.txt` contains some basic dev requirements, which
includes a editable dev install of niimpy itself (`pip install -e`).

Run tests with:
```
pytest .
```

Documentation is built with Sphinx:
```
cd docs
make html
# output in _build/html/
```

Enable nbdime Jupyter notebook diff and merge via git with:
```
nbdime config-git --enable
```


## See also

* To learn about pandas, see its documentation.  It is *not* the most
  clearly written documentation you will find, but you should try
  starting with the "Package overview" and "10 minutes to pandas"
  sections.

* [Matplotlib](https://matplotlib.org/) is the standard Python
  plotting package, but [Seaborn](https://seaborn.pydata.org/) will
  produce nicer graphics by default.  Hint: look for examples and copy
  them.
