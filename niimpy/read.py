"""Read data from various formats, user entery point.

"""

from . import database
from . import util
import pandas as pd

def read_sqlite(filename, table, user=database.ALL, limit=None, offset=None, start=None, end=None):
    """Read DataFrame from sqlite3 database

    This will read data from a sqlite3 file, taking sensor data in a
    given table, and optionally apply various limits.

    Parameters
    ----------

    filename : str
        filename of sqlite3 database

    table : str
        table name of data within the database

    user : str or database.ALL, optional
        If given, return only data matching this user (based an column 'user')

    limit : int, optional
        If given, return only this many rows

    offset : int, optional
        When used with limit, skip this many lines at the beginning

    start : int or float or str or datetime.datetime, optional
        If given, limit to this starting time.  Formats can be int/float
        (unixtime), string (parsed with dateutil.parser.parser, or
        datetime.datetime.

    end : int or float or str or datetime.datetime, optional
        Same meaning as 'start', but for end time
    """
    db = database.Data1(filename)
    return db.raw(table, user, limit=limit, offset=offset, start=start, end=end)

def read_sqlite_tables(filename):
    """Return names of all tables in this database

    Return a set of all tables contained in this database.  This may be
    useful when you need to see what data is available within a database.
    """
    db = database.Data1(filename)
    return db.tables()

def _get_dataframe(df_or_database, table, user=None):
    """Read from database or directly use DataFrame

    Functions used to accept a database only, now the standard is
    dataframe.  This provides some backwards compatability between the
    old and new systems: DataFrames are used as-is, but if a database is
    given, it extracts the right information out of the table (and does
    what the database used to do to filter by user).  This function
    could also be used to transparently accept other types of data
    inputs.

    If input is:

    - DataFrame: pass unchanged, but filter 'user' column
    - Database: extract the given table/user using .raw() and return

    A typical usage is::

        def function(df):
            # 'df' could be a DataFrame or database
            df = _get_dataframe(df, 'TableName')
            # 'df' is now always a DataFrame

    Returns
    -------
    df : DataFrame (same one if possible)

    """
    if isinstance(df_or_database, database.Data1):
        df = df_or_database.raw(table=table, user=subject)
    else:
        df = df_or_database
        # Maintain backwards compatibility in the case subject was passed and
        # questions was *not* a dataframe.
        if isinstance(user, str):
            df = df[df['user'] == user]
    return df





def read_csv(filename, read_csv_options={}):
    """Read DataFrame from csv file

    This will read data from a csv file and then process the result with
    `niimpy.util.df_normalize`.


    Parameters
    ----------

    filename : str
        filename of csv file

    read_csv_options: dict
        Dictionary of options to pandas.read_csv, if this is necessary for custom
        csv files.
    """
    df = pd.read_csv(filename, **read_csv_options)

    # df_normalize converts sets the index to time values and does other time
    # conversions.  Inplace.
    util.df_normalize(df)
    return df
