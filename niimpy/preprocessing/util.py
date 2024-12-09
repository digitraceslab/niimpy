import contextlib
from dateutil.tz import tzlocal
import numpy as np
import os
import pandas as pd
import re
import sys
import warnings

from scipy import stats


def ensure_dataframe(df):
    if df is None:
        return pd.DataFrame()
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    return df


def date_range(df, start, end):
    """Extract out a certain date range from a DataFrame.

    Extract out a certain data range from a dataframe.  The index must be the
    dates, and the index must be sorted.
    """
    # TODO: is this needed?  Do normal pandas operation, timestamp
    # checking is not really needed (and limits the formats that can
    # be used, pandas can take more than pd.Timestamp)
    # Move this function to utils
    # Deal with pandas timestamp compatibility 
    if(start!=None):
        assert isinstance(start,pd.Timestamp),"start not given in timestamp format"
    else:
        start = df.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = df.index[-1]

    df_new = df.loc[start:end]
    return df_new

#SYSTEM_TZ = tzlocal()  # the operating system timezone - for sqlite output compat
SYSTEM_TZ = 'Europe/Helsinki'
TZ = tzlocal()
TZ = 'Europe/Helsinki'

def set_tz(tz):
    """Globally set the preferred local timezone"""
    global TZ
    TZ = tz

@contextlib.contextmanager
def tmp_timezone(new_tz):
    """Temporarily override the global timezone for a black.

    This is used as a context manager::

      with tmp_timezone('Europe/Berlin'):
          ....

    Note: this overrides the global timezone.  In the future, there will
    be a way to handle timezones as non-global variables, which should
    be preferred.
    """
    global TZ
    old_tz = TZ
    TZ = new_tz
    yield
    TZ = old_tz

SQLITE3_EXTENSIONS_BASENAME = os.path.join(os.path.dirname(__file__), 'sqlite-extension-functions.c')
SQLITE3_EXTENSIONS_FILENAME = os.path.join(os.path.dirname(__file__), 'sqlite-extension-functions.so')

def install_extensions():
    """Automatically install sqlite extension functions.

    Only works on Linux for now, improvements welcome."""
    import hashlib
    if not os.path.exists(SQLITE3_EXTENSIONS_BASENAME):
        import urllib.request
        extension_url = 'https://sqlite.org/contrib/download/extension-functions.c?get=25'
        urllib.request.urlretrieve(extension_url, SQLITE3_EXTENSIONS_BASENAME)
    expected_digest = '991b40fe8b2799edc215f7260b890f14a833512c9d9896aa080891330ffe4052'
    if hashlib.sha256(open(SQLITE3_EXTENSIONS_BASENAME, 'rb').read()).hexdigest() != expected_digest:
        print("sqlite-extension-functions.c has wrong sha256 hash", file=sys.stderr)
    os.system('cd %s; gcc -lm -shared -fPIC sqlite-extension-functions.c -o sqlite-extension-functions.so'%
              os.path.dirname(__file__))
    print("Sqlite extension successfully compiled.")

def uninstall_extensions():
    """Uninstall any installed extensions"""
    def unlink_if_exists(x):
        if os.path.exists(x):
            os.unlink(x)
    unlink_if_exists(SQLITE3_EXTENSIONS_FILENAME)


def read_preprocess(df, add_group=None):
    """Standard preprocessing arguments when reading.

    This is a preprocessing filter which handles some standard arguments
    when reading files.  This should be considered a private, unstable
    function.


    Parameters
    ----------

    df: pandas.DataFrame

        Input data frame

    add_group: string, optional

        If given, add a new 'group' column with all values set to this
        given identifier.


    Returns
    -------

    df: dataframe

        Resulting dataframe (modified in-place if possible, but may also
        be a copy)

    """
    if add_group is not None:
        df['group'] = add_group
        #df['group'] = df['group'].astype('category')
        #pd.Categorical(add_group)
    return df


def df_normalize(df, tz=None, old_tz=None):
    """Normalize a df (from sql) before presenting it to the user.

    This sets the dataframe index to the time values, and converts times
    to pandas.TimeStamp:s.  Modifies the data frame inplace.
    """
    if tz is None:
        warnings.warn(DeprecationWarning("From now on, you should explicitely specify timezone with e.g. tz='Europe/Helsinki'.  Specify as part of the reading function."))
        tz = TZ
    if 'time' in df:
        df.index = to_datetime(df['time'])
        df.index.name = None
        df['datetime'] = df.index
    elif 'day' in df and 'hour' in df:
        index = df[['day', 'hour']].apply(lambda row: pd.Timestamp('%s %s:00'%(row['day'], row['hour'])), axis=1)
        if old_tz is not None:
            # old_tz is given - e.g. sqlite already converts it to localtime
            index = index.dt.tz_localize(old_tz).dt.tz_convert(tz)
        else:
            index = index.dt.tz_localize(tz)
        df.index = index
        df.index.name = None


def to_datetime(value):
    times = pd.to_datetime(value, unit='s', utc=True)
    if isinstance(times, pd.Series):
        return times.dt.tz_convert(TZ)
    else:
        return times.tz_convert(TZ)


def identifier_columns(df, id_columns = ["user", "device", "group"]):
    """ build a list of standard Niimpy identifier columns in the 
    dataframe.
    """
    columns = list(set(id_columns) & set(df.columns))
    return columns


def select_columns(df, columns, id_columns = ["user", "device", "group"]):
    """ Select Niimpy identifier columns and listed feature columns """
    columns = identifier_columns(df, id_columns + columns)
    return df[columns]


def group_data(df, additional_columns=None, id_columns=["user", "device", "group"]):
    """ Group the dataframe by Niimpy standard user identifier columns present in
    the dataframe. The columns are 'user', 'device', and 'group'. An addional
    column may be added and used for grouping.
    """
    if type(additional_columns) is str:
        additional_columns = [additional_columns]
    elif additional_columns is None:
        additional_columns = []
    columns = identifier_columns(df, id_columns + additional_columns)
    return df.groupby(columns)


def reset_groups(df, additional_columns=None, id_columns = ["user", "device", "group"]):
    """ Reset id columns and optional addional columns in the dataframe index. """
    if type(additional_columns) is str:
        additional_columns = [additional_columns]
    elif additional_columns is None:
        additional_columns = []
    columns = list(set(id_columns + additional_columns) & set(df.index.names))
    return df.reset_index(columns)


def set_conserved_index(df, additional_columns=None, id_columns = ["user", "device", "group"]):
    """ Set standard id columns as index. This allows concatenating dataframes
    with different measurements.
    """
    if type(additional_columns) is str:
        additional_columns = [additional_columns]
    elif additional_columns is None:
        additional_columns = []
    index_by = list(set(id_columns + additional_columns) & set(df.columns))
    df = df.set_index(index_by, append=True)
    return df


def set_encoding(df, to_encoding = 'utf-8', from_encoding = 'iso-8859-1'):
    """ Recode the dataframe to a different encoding. This is useful when
    the encoding in a data file is set incorrectly and utf characters are
    garbled.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to recode
    to_encoding : str
        Encoding to convert to. Default is 'utf-8'.
    from_encoding : str
        Encoding to convert from. Default is 'iso-8859-1'.

    Returns
    -------
    pandas.DataFrame
        Recoded dataframe.
    """

    for column in df.columns:
        if df[column].dtype == 'object':
            df[column] = df[column].str.encode(from_encoding).str.decode(to_encoding)

    return df


def occurrence(series, bins=5, interval="1h"):
    """ Resamples by grouping_width and aggregates by the number of bins
    with data.
    
    With default options, this reproduces the logic of the "occurrence" database
    function, without needing the database.

    Parameters
    ----------
    series : pandas.Series
        A pandas series of pandas.Timestamps.
    bins : int
        The number of bins each time interval is divided into.
    interval : str
        Length of the time interval. Default is "1h".

    Returns
    -------
    pandas.DataFrame
        Dataframe with timestamp index and 'occurance' column.
    """

    if not isinstance(series, (pd.Series, pd.Index)):
        raise ValueError("The input to niimpy.util.occurrence must be a "
                         "pandas Series or Index, not a DataFrame.  "
                         "(your input type was: %s)"%type(series))

    if not np.issubdtype(series.dtype.base, np.datetime64):
        series = pd.to_datetime(series, unit='s')

    dt = pd.to_timedelta(interval)
    bin_width = dt/bins
    
    df = pd.DataFrame({"time": series})
    df.set_index('time', inplace=True)
    df["occurrence"] = 1

    df = df.resample(bin_width).count()
    df = df[df['occurrence'] > 0]
    df = df.resample(interval).count()

    return df


def aggregate(df, freq, method_numerical='mean', method_categorical='first', groups=['user'], **resample_kwargs):
    """ Grouping and resampling the data. This function performs separated resampling
    for different types of columns: numerical and categorical.

    Parameters
    ----------
    df : pandas Dataframe
        Dataframe to resample
    freq : string
        Frequency to resample the data. Requires the dataframe to have datetime-like index.
    method_numerical : str
        Resampling method for numerical columns. Possible values:
        'sum', 'mean', 'median'. Default value is 'mean'.
    method_categorical : str
        Resampling method for categorical columns. Possible values: 'first', 'mode', 'last'.
    groups : list
        Columns used for groupby operation.
    resample_kwargs : dict
        keywords to pass pandas resampling function

    Returns
    -------
        An aggregated and resampled multi-index dataframe.
    """

    #Groupby user
    groupby = df.groupby(groups)

    #Resample numerical columns -> sub_df1
    assert method_numerical in ['mean', 'sum', 'median'], \
        'Cannot recognize sampling method. Possible values: "mean", "sum", "median".'
    if method_numerical == 'sum':
        sub_df1 = groupby.resample(freq, **resample_kwargs, include_groups=False).sum(numeric_only=True)
    elif method_numerical == 'mean':
        sub_df1 = groupby.resample(freq, **resample_kwargs, include_groups=False).mean(numeric_only=True)
    elif method_numerical == 'median':
        sub_df1 = groupby.resample(freq, **resample_kwargs, include_groups=False).median(numeric_only=True)
    else:
        print("Can't recognize sampling method")


    #Resample cat columns -> sub_df2
    cat_cols = df.select_dtypes(include=['object']).columns.to_list()
    cat_cols.extend(groups)
    cat_cols = list(set(cat_cols))

    groupby = df[cat_cols].groupby(groups)
    assert method_categorical in ['first', 'mode', 'last']
    if method_categorical == 'first':
        sub_df2 = groupby.resample(freq, **resample_kwargs, include_groups=False).first()
    elif method_categorical == 'last':
        sub_df2 = groupby.resample(freq, **resample_kwargs, include_groups=False).last()
    elif method_categorical == 'mode':
        sub_df2 = groupby.resample(freq, **resample_kwargs, include_groups=False).agg(lambda x: tuple(stats.mode(x)[0]))

    #Merge sub_df1 and sub_df2
    sub_df1 = sub_df1.drop(groups, axis=1, errors='ignore')
    sub_df2 = sub_df2.drop(groups, axis=1, errors='ignore')
    final_df = sub_df1.join(sub_df2)

    # Reset the user index, user should be a column
    final_df.reset_index(groups, inplace=True)

    return final_df
