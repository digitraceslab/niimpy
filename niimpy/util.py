import contextlib
from dateutil.tz import tzlocal
import numpy as np
import os
import pandas as pd
import sys


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


#TODO: reanme to data.py

def df_normalize(df, old_tz=None):
    """Normalize a df (from sql) before presenting it to the user.

    This sets the dataframe index to the time values, and converts times
    to pandas.TimeStamp:s.  Modifies the data frame inplace.
    """
    if 'time' in df:
        df.index = to_datetime(df['time'])
        df.index.name = None
        df['datetime'] = df.index
    elif 'day' in df and 'hour' in df:
        index = df[['day', 'hour']].apply(lambda row: pd.Timestamp('%s %s:00'%(row['day'], row['hour'])), axis=1)
        if old_tz is not None:
            # old_tz is given - e.g. sqlite already converts it to localtime
            index = index.dt.tz_localize(old_tz).dt.tz_convert(TZ)
        else:
            index = index.dt.tz_localize(TZ)
        df.index = index
        df.index.name = None


def to_datetime(value):
    times = pd.to_datetime(value, unit='s', utc=True)
    if isinstance(times, pd.Series):
        return times.dt.tz_convert(TZ)
    else:
        return times.tz_convert(TZ)



def occurrence(series, bin_width=720, grouping_width=3600):
    """Number of 12-minute

    This reproduces the logic of the "occurrence" database function, without needing the database.

    inputs: pandas.Series of pandas.Timestamps

    Output: pandas.DataFrame with timestamp index and 'occurance' column.

    TODO: use the grouping_width option.
    """
    if grouping_width != 3600:
        raise ValueError("Changing grouping_width is not currently supported.")
    if grouping_width % bin_width != 0:
        raise ValueError("grouping_width must be a multiple of bin_width")

    if not isinstance(series, (pd.Series, pd.Index)):
        raise ValueError("The input to niimpy.util.occurrence must be a "
                         "pandas Series or Index, not a DataFrame.  "
                         "(your input type was: %s)"%type(series))

    if not np.issubdtype(series.dtype.base, np.datetime64):
        df = pd.to_datetime(series, unit='s')
    df = pd.DataFrame({"time":series})

    df['day'] = df['time'].dt.strftime("%Y-%m-%d")
    df['hour'] = df['time'].dt.hour
    df['bin'] = df['time'].dt.minute // (bin_width//60)

    gb1 = df.groupby(by=["day", "hour", "bin"], as_index=False).size()   # everything in the same bin goes to one row
    gb2 = gb1.groupby(by=["day", "hour"]).size().to_frame()         # count number of bins in an hour
    gb2.rename({0:"occurrence"}, axis=1, inplace=True)
    # Following handles cases where there are not enough rows... TODO what is the right thing to do here?
    gb2.reset_index(inplace=True)
    gb2.index = gb2.loc[:, ['day', 'hour']].apply(lambda row: pd.Timestamp('%s %s:00'%(row['day'], row['hour'])), axis=1)
    return gb2
