"""Read data from various formats, user entery point.

"""

from . import database

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

