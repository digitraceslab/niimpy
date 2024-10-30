# Niimpy

![maintenance-status](https://img.shields.io/badge/maintenance-actively--developed-brightgreen.svg)
[![Test](https://github.com/digitraceslab/niimpy/actions/workflows/test.yml/badge.svg)](https://github.com/digitraceslab/niimpy/actions/workflows/test.yml)
[![Build](https://github.com/digitraceslab/niimpy/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/digitraceslab/niimpy/actions/workflows/pages/pages-build-deployment)
[![Test installation from source](https://github.com/digitraceslab/niimpy/actions/workflows/install.yml/badge.svg)](https://github.com/digitraceslab/niimpy/actions/workflows/install.yml)
[![codecov](https://codecov.io/gh/digitraceslab/niimpy/branch/master/graph/badge.svg?token=SEEOOF7A70)](https://codecov.io/gh/digitraceslab/niimpy)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/digitraceslab/niimpy/HEAD?labpath=docs)

What
----

Niimpy is a Python package for analyzing and quantifying behavioral data. It uses pandas to read data from disk, perform basic manipulations, provides explorative data analysis functions, offers many high-level preprocessing functions for various types of data, and has functions for behavioral data analysis.

For Who
-------

Niimpy is intended for researchers and data scientists analyzing digital digital behavioral data. Its purpose is to facilitate data analysis by providing a standardized replicable workflow.

Why
---

Digital behavioral studies using personal digital devices typically produce rich multi-sensor longitudinal datasets of mixed data types. Analyzing such data requires multidisciplinary expertise and software designed for the purpose. Currently, no standardized workflow or tools exist to analyze such data sets. The analysis requires domain knowledge in multiple fields and programming expertise. Niimpy package is specifically designed to analyze longitudinal, multimodal behavioral data. Niimpy is a user-friendly open-source package that can be easily expanded and adapted to specific research requirements. The toolbox facilitates the analysis phase by providing tools for data management, preprocessing, feature extraction, and visualization. The more advanced analysis methods will be incorporated into the toolbox in the future.


How
---

The toolbox is divided into four layers by functionality: 1) reading, 2) preprocessing, 3) exploration, and 4) analysis. For more information about the layers, refer the toolbox architecture chapter :doc:`architecture`. Quickstart guide would be a good place to start :doc:`quick-start`. More detailed demo Jupyter notebooks are provided in user guide chapter :doc:`demo_notebooks/Exploration`. Instructions for individual functions can be found under API chapter :doc:`api/niimpy`.


## Installation

- Only supports Python 3 (tested on 3.8 and above)

- This is a normal Python package to install. 

  ```
  pip install niimpy
  ```

- It can also be installed manually:

  ```
  pip install https://github.com/digitraceslab/niimpy/archive/master.zip
  ```

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
location = niimpy.util.aggregate(location, freq='10min', method_numerical='median')
location = location.reset_index(0).dropna()

# Feature extraction
features = nilo.extract_features(
  lats=location['latitude'],
  lons=location['longitude'],
  users=location['user'],
  groups=location['group'],
  times=location.index,
  speeds=location['speed']
)
```

## Documentation

Niimpy documentation is hosted at [readthedocs]https://digitraceslab.github.io/niimpy/.

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
