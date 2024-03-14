"""Read data from sqlite3 databases.

**Direct use of this module is mostly deprecated.**

Read data from sqlite3 databases, both into pandas.DataFrame:s (Database.raw(),
among other functions), and Database objects.  The Database object does not
immediately load data, but provides some methods to load data on demand later,
possibly doing various filtering and preprocessing already at the loading
stage.  This can save memory and processing time, but is much more complex.

This module is mostly out-of-use now: read.read_sqlite is used instead, which
wraps the .raw() method and reads all data into memory.

Database format
---------------

When reading data, a table name must be specified (which allows multiple
datasets to be put in one file).  Table column names map to dataframe column
names, with various standard processing (for example the 'time' column being
converted to the index)


Quick usage
-----------

db = database.open(FILE_NAME, tz=TZ)
df = db.raw(TABLE_NAME, user=database.ALL)

Recommend usage:

df = niimpy.read_sqlite(FILE_NAME, TABLE_NAME, tz=TZ)

See also
--------

niimpy.reading.read_*: currently recommended functions to access all types of
data, including databases.

"""
#
# Conventions:
#  time     column is unixtime
#  datetime column is pandas.Timestamp
#  date     column is string 'YYYY-MM-DD'

from __future__ import print_function, division

import datetime
from math import sqrt
from numbers import Number
import os
import sqlite3
import sys

import dateutil.parser
import pandas as pd

from niimpy.preprocessing import util

class ALL:
    """Sentinel value for all users"""
    pass

#def datetime_selector(x):
#    selectors = [ ]
#    if isinstance(x, int):
#        pass
#    else:  pd
#    selectors.append('{0} < time'.format(x))
#    return ' AND time<'

def open(db, tz=None):
    """Open a database and return a Data1 object"""
    return Data1(db, tz=tz)


# Online variance calculation
# https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm
class sqlite3_stdev:
    """Sqlite sample standard deviation function in pure Python.

    With `conn.create_aggregate("stdev", 1, sqlite3_stdev)`, this adds a
    stdev function to sqlite.

    Edge cases:

    - Empty list = nan (different than C function, which is zero)
    - Ignores nan input values (does not count them).  (different than
      numpy: returns nan)
    - ignores non-numeric types (no conversion)
    """
    def __init__(self):
        self.N = 0
        self.mean = 0
        self.M2 = 0
    def step(self, value):
        if not isinstance(value, Number):
           return
        self.N += 1
        delta = value - self.mean
        self.mean += delta / self.N
        delta2 = value - self.mean
        self.M2 += delta * delta2
    def finalize(self):
        if self.N == 0:
            return float('nan')
        return sqrt(self.M2 / self.N)



class Data1(object):
    """Database wrapper for niimpy data.

    This opens a database and provides methods to do common operations.
    """
    def __init__(self, db, tz=None):
        """Open the database.

        Don't do anything yet, but stores the open connection object on
        self.conn for future functions to use.
        """
        if not os.path.exists(db):
            raise FileNotFoundError("Database does not exist: {}".format(db))
        self.conn = sqlite3.connect(db)
        if os.path.exists(util.SQLITE3_EXTENSIONS_FILENAME):
            self.conn.enable_load_extension(True)
            self.conn.load_extension(util.SQLITE3_EXTENSIONS_FILENAME)
        else:
            self.conn.create_aggregate("stdev", 1, sqlite3_stdev)
            #print("SQLite3 extension module not available, some functions will not work.", file=sys.stderr)
            #print("Future niimpy versions will improve this.", file=sys.stderr)
            #print("({0})".format(util.SQLITE3_EXTENSIONS_FILENAME), file=sys.stderr)
        self._singleuser = self._is_single_user()
        self._tz = tz

    def _is_single_user(self):
        """Detect if this is a single-user database

        Currently this is run at the start and set per-database, not
        per-table.  A single-user database is missing a 'user' column
        and thus requires a little bit of special-casing.  Not much, but
        some.
        """
        tables = self.tables()
        for table in tables:
            if table == 'errors': continue
            # Using pragma_table_info would be better, but this
            # requires about sqlite 3.16 or above, which is a bit much
            # (requires ubuntu 18.04 or anaconda).
            try:
                self.conn.execute("SELECT user FROM \"%s\" LIMIT 1"%table).fetchall()
            except sqlite3.OperationalError as e:
                if 'no such column' in e.args[0]:
                    self._singleuser = True
                    #print("Detected single-user database", file=sys.stderr)
                    return True
                else:
                    raise
        return False

    def execute(self, *args, **kwargs):
        """Execute rauw SQL code.

        Execute raw SQL.  Smply proxy all arguments to
        self.conn.execute().  This is simply a convenience shortcut.
        """
        return self.conn.execute(*args, **kwargs)

    def tables(self):
        """List all tables that are inside of this database.

        Returns a set."""
        return {x[0] for x in self.conn.execute('SELECT name FROM sqlite_master WHERE type="table"') if x[0]!='errors'}

    def _sql_where_user(self, user):
        """Query generation convenience.

        Generates a SQL "WHERE user={user}" line, if needed for this
        database and query.
        """
        if self._singleuser:
            return ""
        if user is ALL:
            return ""
        elif user:
            return "AND user=:user"
        raise ValueError("Specify user or user=niimpy.ALL for all users")

    def _sql_where_daterange(self, start, end):
        """Query generation convenience.

        Generates a SQL "WHERE start <= time AND time < end" line if
        needed for this query.
        """
        where = ""
        def to_timestamp(x):
            if isinstance(x, (int, float)): return x
            if isinstance(x, str): return dateutil.parser.parse(x).timestamp() # localtime
            if isinstance(x, datetime.datetime): return x.timestamp()
            raise ValueError("Unknown timestamp format: {}".format(x))
        if start:
            where += " AND %s <= time "%(to_timestamp(start))
        if end:
            where += " AND time < %s "%(to_timestamp(end))
        return where

    def _sql_select_user(self, user):
        """Query generation convenience.

        Generates a SQL "SELECT 'user, '" line, if needed.  This is
        needed to support both single-user and multi-user databases.
        """
        if self._singleuser:
            return ""
        if user is ALL:
            return "user, "
        elif user:
            return ""
        raise ValueError("Specify user or user=niimpy.ALL for all users")

    def _sql_limit(self, limit, offset=None):
        """Query generation convenience.

        Generates a SQL "LIMIT ... OFFSET" line, if needed."""
        if offset is not None:
            if limit is None:  return "LIMIT -1 OFFSET %s"%(int(offset), )
            else:  return "LIMIT %s OFFSET %s"%(int(limit), int(offset))
        if limit is None: return ""
        return 'LIMIT %s'%int(limit)

    def _sql_order_by(self, order=False):
        """Query generation convenience.

        Generates a SQL ORDER BY time line if needed."""
        if not order: return ""
        return "ORDER BY time"


    def _sql_group_by_user(self):
        """Query generation convenience.

        Generates a SQL "GROUP BY user" line, if needed for this query."""
        if self._singleuser:
            return ""
        return "GROUP BY user"

    def _sql(self, user, limit=None, offset=None, order=False, start=None, end=None):
        """Generate string substitutions for SQL queries.

        This looks at the various function parameters and will return a
        dict of substitutions for the query.  This makes the same query
        work for both single- and multi-user databases, and avoid
        reproducing logic where not needed.
        """
        return dict(select_user=self._sql_select_user(user),
                    where_user=self._sql_where_user(user),
                    where_daterange=self._sql_where_daterange(start, end),
                    limit=self._sql_limit(limit, offset=None),
                    order_by=self._sql_order_by(order),
                    group_by_user=self._sql_group_by_user(),
                   )



    def users(self, table=None):
        """Return set of all users in all tables"""
        if self._singleuser:
            return None
        if table is not None:  tables = [table]
        else:                  tables = self.tables()
        users = set()
        for table_ in tables:
            users |= {x[0] for x in self.conn.execute('SELECT DISTINCT user FROM "%s"'%table_)}
        return users

    def validate_username(self, user):
        """Validate a username, for single/multiuser database and so on.

        This function considers if the database is single or multi-user,
        and ensures a valid username or ALL.

        It returns a valid username, so can be used as a wrapper, to handle
        future special cases, e.g.::

           user = db.validate_username(user)
        """
        if self._singleuser:
            if user not in (ALL, None):
                raise ValueError("This is a single-user database and a user was given.")
            if user is None:
                user = ALL
        else: # multiuser
            if user is not ALL  and  not isinstance(user, str):
                raise ValueError("This is a multi-user database, a user must be given as a string (or niimpy.ALL).")
        return user

    def user_table_counts(self):
        """Return table of number of data points per user, per table.

        Return a dataframe of row=table, column=user, value=number of
        counts of that user in that table.
        """
        if self._singleuser:
            #print(self.tables())
            user_stats = pd.DataFrame(index=sorted(self.tables()), columns=("count",))
            #print(user_stats)
            cur = self.conn.cursor()
            for table_ in self.tables():
                for count, in cur.execute('SELECT count(*) FROM "{table}"'.format(table=table_, **self._sql(user=ALL))):
                    user_stats[table_, 'count'] = count
            return user_stats
        user_stats = pd.DataFrame(index=sorted(self.tables()), columns=sorted(self.users()))
        cur = self.conn.cursor()
        for table_ in self.tables():
            for user, count in cur.execute('SELECT {select_user} count(*) FROM "{table}" GROUP BY user'.format(table=table_, **self._sql(user=ALL))):
                if user is None: continue
                user_stats[user][table_] = count
        return user_stats

    def first(self, table, user, start=None, end=None, offset=None, _aggregate="min", _limit=None):
        """Return earliest data point.

        Return None if there is no data."""
        df = pd.read_sql("""SELECT {select_user} {aggregate}(time) AS {result_column_name}
                              FROM (
                                  SELECT * FROM "{table}"
                                  WHERE 1 {where_user} {where_daterange}
                                  {order_by} {limit}
                              )
                              {group_by_user}
                        """.format(table=table,
                                   aggregate=_aggregate,
                                   result_column_name='time' if _aggregate!='count' else 'count',
                                   **self._sql(user=user, limit=_limit, offset=offset, start=start, end=end)),
                        self.conn, params={'user':user, })
        if df.empty:
            return None
        if 'time' in df:
            df['datetime'] = util.to_datetime(df['time'])
        return df
    def last(self, *args, **kwargs):
        """Return the latest timestamp.

        See the "first" for more information."""
        return self.first(*args, _aggregate="max", **kwargs)
    def count(self, *args, **kwargs):
        """Return the number of rows

        See the "first" for more information."""
        return self.first(*args, _aggregate="count", **kwargs)
    def exists(self, *args, **kwargs):
        """Returns True if any data exists

        Follows the same syntax as .first(), .last(), and .count(), but
        the limit argument is not used.
        """
        kwargs.pop('limit', None)
        return self.count(*args, _limit=1, **kwargs) >= 1


    def occurrence(self, table, user, bin_width=720, limit=None, offset=None, start=None, end=None):
        n_intervals = 3600 / bin_width
        interval_width = 60/n_intervals
        df = pd.read_sql("""SELECT {select_user} day, hour,
                                count(*) as occurrence, sum(bin_count) as count, group_concat(interval) AS withdata
                            FROM (
                                SELECT
                                  strftime('%Y-%m-%d', time, 'unixepoch', 'localtime') AS day,
                                  CAST(strftime('%H', time, 'unixepoch', 'localtime') AS INTEGER) AS hour,
                                  CAST(strftime('%M', time, 'unixepoch', 'localtime')/:interval_width AS INTEGER) AS interval,
                                  count(*) as bin_count
                                 FROM "{table}"
                                 WHERE 1 {where_user} {where_daterange}
                                 GROUP BY day, hour, interval
                                 {limit}
                                )
                            GROUP BY day, hour
                        """.format(table=table,
                                   **self._sql(user=user, limit=limit, offset=offset, start=start, end=end)),
                        self.conn, params={'user':user, 'interval_width':interval_width})
        util.df_normalize(df, old_tz=util.SYSTEM_TZ, tz=self._tz)
        return df


    def hourly(self, table, user, columns=[], limit=None, offset=None, start=None, end=None):
        if isinstance(columns, str):
            columns = [columns]
        if columns:
            column_selector = ",\n".join("    avg({0}) AS {0}_mean, stdev({0}) AS {0}_std, count({0}) AS {0}_count".format(c) for c in columns)
            column_selector = ',\n'+column_selector
        else:
            column_selector = ""

        df = pd.read_sql("""SELECT
                                {select_user}
                                strftime('%Y-%m-%d', time, 'unixepoch', 'localtime') AS day,
                                CAST(strftime('%H', time, 'unixepoch', 'localtime') AS INTEGER) AS hour,
                                count(*) as count {column_selector}
                            FROM (
                                SELECT * FROM "{table}" {order_by} {limit}
                                )
                            WHERE 1 {where_user} {where_daterange}
                            GROUP BY day, hour
                            {limit}
                         """.format(table=table, column_selector=column_selector,
                                   **self._sql(user=user, limit=limit, offset=offset, start=start, end=end)),
                         self.conn, params={'user':user})
        util.df_normalize(df, old_tz=util.SYSTEM_TZ, tz=self._tz)
        return df


    def timestamps(self, table, user, limit=None, offset=None, start=None, end=None):
        df = pd.read_sql("""SELECT
                                {select_user} time
                            FROM "{table}"
                            WHERE 1 {where_user} {where_daterange}
                            {order_by}
                            {limit}
                        """.format(table=table,
                                   **self._sql(user=user, limit=limit, offset=offset, start=start, end=end)
                                   ),
                        self.conn, params={'user':user})
        if 'user' not in df:
            # Single user data:
            return util.to_datetime(df['time'])
        else:
            util.df_normalize(df, tz=self._tz)
            return df

    def raw(self, table, user, limit=None, offset=None, start=None, end=None):
        """Read all data in a table and return it as a DataFrame.

        This reads all data (subject to several possible filters) and
        returns it as a DataFrame.
        """
        df = pd.read_sql("""SELECT
                                *
                            FROM "{table}"
                            WHERE 1 {where_user} {where_daterange}
                            {order_by}
                            {limit}
                        """.format(table=table,
                                   **self._sql(user=user, limit=limit, offset=offset, start=start, end=end)
                                   #select_user=self._sql_select_user(user),  where_user=self._sql_where_user(user),
                                   #limit=self._sql_limit(limit)
                                   ),
                        self.conn, params={'user':user})
        if 'time' in df:
            util.df_normalize(df, tz=self._tz)
        return df

    def get_survey_score(self, table, user, survey, limit=None, start=None, end=None):
        """Get the survey results, summing scores.

        survey: The servey prefix in the 'id' column, e.g. 'PHQ9'.  An '_' is appended.
        """
        questions = self.raw(table=table, user=user, limit=limit, start=start, end=end)
        answers = questions[questions['id'].str.startswith(survey+'_')]
        answers['answer'] = pd.to_numeric(answers['answer'])
        survey_score = answers.groupby(['user','time'])['answer'].sum(skipna=False)
        survey_score = survey_score.to_frame()
        return survey_score
