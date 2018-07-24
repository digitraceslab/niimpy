
from __future__ import print_function, division

import datetime
import os
import sqlite3
import sys

import dateutil.parser
import pandas as pd

# https://sqlite.org/contrib/download/extension-functions.c?get=25
#SQLITE3_EXTENSIONS_FILENAME = '/m/cs/scratch/networks-nima/darst/sqlite-extension-functions.so'
SQLITE3_EXTENSIONS_FILENAME = os.path.join(os.path.dirname(__file__), 'sqlite-extension-functions.so')

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

def open(db):
    """Open a database and return a Data1 object"""
    return Data1(db)

class Data1(object):
    def __init__(self, db):
        if not os.path.exists(db):
            raise FileNotFoundError("Database does not exist: {}".format(db))
        self.conn = sqlite3.connect(db)
        if os.path.exists(SQLITE3_EXTENSIONS_FILENAME):
            self.conn.enable_load_extension(True)
            self.conn.load_extension(SQLITE3_EXTENSIONS_FILENAME)
        else:
            print("SQLite3 extension module not available, some functions will not work.", file=sys.stderr)
            print("Future niimpy versions will improve this.", file=sys.stderr)
            print("({0})".format(SQLITE3_EXTENSIONS_FILENAME), file=sys.stderr)
        self._singleuser = self._is_single_user()

    def _is_single_user(self):
        """Detect if this is a single-user database

        Currently this is run at the start and set per-database, not per-table.
        """
        tables = self.tables()
        for table in tables:
            if table == 'errors': continue
            has_user_column = self.conn.execute("SELECT name FROM pragma_table_info(\"AwareScreen\") WHERE name='user'").fetchall()
            if not has_user_column:
                self._singleuser = True
                print("Detected single-user database", file=sys.stderr)
                return True
        return False

    def execute(self, *args, **kwargs):
        """Execute rauw SQL code.

        Execute raw SQL.  Smply proxy all arguments to self.conn.execute()"""
        return self.conn.execute(*args, **kwargs)

    def tables(self):
        return {x[0] for x in self.conn.execute('SELECT name FROM sqlite_master WHERE type="table"') if x[0]!='errors'}

    def _sql_where_user(self, user):
        """SQL WHERE user={user} line, if needed."""
        if self._singleuser:
            return ""
        if user is ALL:
            return ""
        elif user:
            return "AND user=:user"
        raise ValueError("Specify user or user=niimpy.ALL for all users")

    def _sql_where_daterange(self, start, end):
        """SQL WHERE start <= time AND time < end."""
        where = ""
        def to_timestamp(x):
            if isinstance(x, int): return x
            if isinstance(x, str): return dateutil.parser.parse(x).timestamp()
            if isinstance(x, datetime.datetime): return x.timestamp()
            raise ValueError("Unknown timestamp format: {}".format(x))
        if start:
            where += " AND %s <= time "%(to_timestamp(start))
        if end:
            where += " AND time < %s "%(to_timestamp(end))
        return where

    def _sql_select_user(self, user):
        """SQL SELECT 'user, ' line, if needed."""
        if self._singleuser:
            return ""
        if user is ALL:
            return "user, "
        elif user:
            return ""
        raise ValueError("Specify user or user=niimpy.ALL for all users")

    def _sql_limit(self, limit, offset=None):
        """SQL LIMIT line, if needed."""
        if offset is not None:
            if limit is None:  return "LIMIT -1 OFFSET %s"%(int(offset), )
            else:  return "LIMIT %s OFFSET %s"%(int(limit), int(offset))
        if limit is None: return ""
        return 'LIMIT %s'%int(limit)

    def _sql_order_by(self, order=False):
        if not order: return ""
        return "ORDER BY time"


    def _sql_group_by_user(self):
        """SQL LIMIT line, if needed."""
        if self._singleuser:
            return ""
        return "GROUP BY user"

    def _sql(self, user, limit=None, offset=None, order=False, start=None, end=None):
        return dict(select_user=self._sql_select_user(user),
                    where_user=self._sql_where_user(user),
                    where_daterange=self._sql_where_daterange(start, end),
                    limit=self._sql_limit(limit, offset=None),
                    order=self._sql_order_by(order),
                    group_by_user=self._sql_group_by_user(),
                   )



    def users(self, table=None):
        """Set of all users in all tables"""
        if self._singleuser:
            return None
        if table is not None:  tables = [table]
        else:                  tables = self.tables()
        users = set()
        for table_ in tables:
            users |= {x[0] for x in self.conn.execute('SELECT DISTINCT user FROM "%s"'%table_)}
        return users

    def user_table_counts(self):
        """More detailed user stats"""
        if self._singleuser:
            print(self.tables())
            user_stats = pd.DataFrame(index=sorted(self.tables()), columns=("count",))
            print(user_stats)
            cur = self.conn.cursor()
            for table_ in self.tables():
                for count, in cur.execute('SELECT count(*) FROM "{table}"'.format(table=table_, **self._sql(user=ALL))):
                    user_stats['count'][table_] = count
            return user_stats
        user_stats = pd.DataFrame(index=sorted(self.users()), columns=sorted(self.tables()))
        cur = self.conn.cursor()
        for table_ in self.tables():
            for user, count in cur.execute('SELECT {select_user} count(*) FROM "{table}" GROUP BY user'.format(table=table_, **self._sql(user=ALL))):
                if user is None: continue
                user_stats[table_][user] = count
        return user_stats

    def first(self, table, user, start=None, end=None, _aggregate="min"):
        """Return earliest data point.

        Return None if there is no data."""
        df = pd.read_sql("""SELECT {select_user} {aggregate}(time) AS {result_column_name}
                              FROM "{table}"
                              WHERE 1 {where_user} {where_daterange}
                              {group_by_user}
                        """.format(table=table,
                                   aggregate=_aggregate,
                                   result_column_name='time' if _aggregate!='count' else 'count',
                                   **self._sql(user=user, limit=None, start=start, end=end)),
                        self.conn, params={'user':user, })
        if df.empty:
            return None
        if 'time' in df:
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
        return df
    def last(self, *args, **kwargs):
        """Return the latest timestamp.

        See the "first" for more information."""
        return self.first(*args, _aggregate="max", **kwargs)
    def count(self, *args, **kwargs):
        """Return the number of rows

        See the "first" for more information."""
        return self.first(*args, _aggregate="count", **kwargs)



    def quality(self, table, user, limit=None, start=None, end=None):
        n_intervals = 5
        interval_width = 60/n_intervals
        df = pd.read_sql("""SELECT {select_user} day, hour, interval,
                                count(*) as quality, sum(bin_count) as count, group_concat(interval) AS withdata
                              FROM (
                              SELECT
                                strftime('%Y-%m-%d', time, 'unixepoch', 'localtime') AS day,
                                CAST(strftime('%H', time, 'unixepoch', 'localtime') AS INTEGER) AS hour,
                                CAST(strftime('%M', time, 'unixepoch', 'localtime')/:interval_width AS INTEGER) AS interval,
                                count(*) as bin_count
                               FROM "{table}"
                               WHERE 1 {where_user} {where_daterange}
                               GROUP BY day, hour, interval)
                             GROUP BY day, hour
                             {limit}
                        """.format(table=table,
                                   **self._sql(user=user, limit=limit, start=start, end=end)),
                        self.conn, params={'user':user, 'interval_width':interval_width})
        return df


    def hourly(self, table, user, columns='hr', limit=None, start=None, end=None):
        if isinstance(columns, str):
            columns = [columns]
        column_selector = ",\n".join("    avg({0}) AS {0}_mean, stdev({0}) AS {0}_std, count({0}) AS {0}_count".format(c) for c in columns)
        column_selector = ',\n'+column_selector

        df = pd.read_sql("""SELECT
                                {select_user}
                                strftime('%Y-%m-%d', time, 'unixepoch', 'localtime') AS day,
                                CAST(strftime('%H', time, 'unixepoch', 'localtime') AS INTEGER) AS hour,
                                count(*) as count {column_selector}
                            FROM "{table}"
                               WHERE 1 {where_user} {where_daterange}
                            GROUP BY day, hour
                            {limit}
                         """.format(table=table, column_selector=column_selector,
                                   **self._sql(user=user, limit=limit, start=start, end=end)),
                         self.conn, params={'user':user})
        return df


    def raw(self, table, user, limit=None, offset=None, start=None, end=None):
        df = pd.read_sql("""SELECT
                                *
                            FROM "{table}"
                               WHERE 1 {where_user} {where_daterange}
                            {limit}
                        """.format(table=table,
                                   **self._sql(user=user, limit=limit, start=start, end=end)
                                   #select_user=self._sql_select_user(user),  where_user=self._sql_where_user(user),
                                   #limit=self._sql_limit(limit)
                                   ),
                        self.conn, params={'user':user})
        if 'time' in df:
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
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
