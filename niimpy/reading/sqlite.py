""" Read data from sqlite3 database.
"""

import warnings

from niimpy.reading import database
from niimpy.preprocessing import util


def read_sqlite(filename, table, add_group=None, user=database.ALL, limit=None, offset=None, start=None, end=None, tz=None):
    """Read DataFrame from sqlite3 database

    This will read data from a sqlite3 file, taking sensor data in a
    given table, and optionally apply various limits.

    Parameters
    ----------

    filename : str
        filename of sqlite3 database

    table : str
        table name of data within the database

    add_group : object
        If given, add a 'group' column with all values set to this.

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
    if tz is None:
        warnings.warn(DeprecationWarning("From now on, you should explicitely specify timezone with e.g. tz='Europe/Helsinki'"), stacklevel=2)

    db = database.Data1(filename, tz=tz)
    df = db.raw(table, user, limit=limit, offset=offset, start=start, end=end)
    df = util.read_preprocess(df, add_group=add_group)
    return df


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

    - database: extract the given table/user using .raw() and return

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
        df = df_or_database.raw(table=table, user=user)
    else:
        df = df_or_database
        # questions was *not*  dataframe.
        if user is not None and user is not database.ALL:
            df = df[df['user'] == user]
    return df
