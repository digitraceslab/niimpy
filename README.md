# Niimpy

`niimpy` is a Python package for managing individual-level data.  The
best way to describe it is to look at the big picture:

- [koota-server](https://github.com/CxAalto/koota-server) is a
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

## Documentation

For now, see the included [Introduction.ipynb] and [Reference.ipynb]
notebooks.

To learn about what converters exist and what they mean, see the
[Koota wiki](https://github.com/CxAalto/koota-server/wiki), in
particular the data sources section.

## See also

* To learn about pandas, see its documentation.  It is *not* the most
  clearly written documentation you will find, but you should try
  starting with the "Package overview" and "10 minutes to pandas"
  sections.

* [Matplotlib](https://matplotlib.org/) is the standard Python
  plotting package, but [Seaborn](https://seaborn.pydata.org/) will
  produce nicer graphics by default.  Hint: look for examples and copy
  them.