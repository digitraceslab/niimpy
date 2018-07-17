
from __future__ import print_function, division

import os
import sqlite3
import sys

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

class Data1(object):
    def __init__(self, db):
        if not os.path.exists(db):
            raise FileNotFoundError("Database does not exist: {}".format(db))
        self.conn = sqlite3.connect(db)
        if os.path.exists(SQLITE3_EXTENSIONS_FILENAME):
            self.conn.enable_load_extension(True)
            self.conn.load_extension(SQLITE3_EXTENSIONS_FILENAME)
        else:
            #print("SQLite3 extension module not available, some functions will not work.  Request that this be improved.",
            #      file=sys.stderr)
            #print("==>", SQLITE3_EXTENSIONS_FILENAME, file=sys.stderr)
            pass


    def tables(self):
        return {x[0] for x in self.conn.execute('SELECT name FROM sqlite_master WHERE type="table"')}

    @staticmethod
    def _user_selector(user):
        """SQL WHERE user={user} line, if needed."""
        if user is ALL:
            return ""
        elif user:
            return "AND user=:user"
        raise ValueError("Specify user or user='all' for all of them")

    @staticmethod
    def _sql_limit(limit):
        """SQL LIMIT line, if needed."""
        if limit is None: return ""
        assert isinstance(limit, int)
        return 'LIMIT %s'%limit


    def users(self, table=None):
        """Set of all users in all tables"""
        if table is not None:  tables = [table]
        else:                  tables = self.tables()
        users = set()
        for table_ in tables:
            users |= {x[0] for x in self.conn.execute('SELECT DISTINCT user FROM "%s"'%table_)}
        return users

    def user_table_counts(self):
        """More detailed user stats"""
        user_stats = pd.DataFrame(index=sorted(self.users()), columns=sorted(self.tables()))
        cur = self.conn.cursor()
        for table_ in self.tables():
            for user, count in cur.execute('SELECT user, count(*) FROM "{table}" GROUP BY user'.format(table=table_)):
                if user is None: continue
                user_stats[table_][user] = count
        return user_stats


    def quality(self, table, user, limit=None):
        n_intervals = 5
        interval_width = 60/n_intervals
        df = pd.read_sql("""SELECT day, hour, interval,
                                count(*) as quality, sum(bin_count) as count, group_concat(interval) AS withdata
                              FROM (
                              SELECT
                                strftime('%Y-%m-%d', time, 'unixepoch', 'localtime') AS day,
                                CAST(strftime('%H', time, 'unixepoch', 'localtime') AS INTEGER) AS hour,
                                CAST(strftime('%M', time, 'unixepoch', 'localtime')/:interval_width AS INTEGER) AS interval,
                                count(*) as bin_count
                               FROM "{table}"
                               WHERE 1 {user_selector}
                               GROUP BY day, hour, interval)
                             GROUP BY day, hour
                             {limit}
                        """.format(table=table, user_selector=self._user_selector(user), limit=self._sql_limit(limit)),
                        self.conn, params={'user':user, 'interval_width':interval_width})
        return df


    def hourly(self, table, user, columns='hr', limit=None):
        if isinstance(columns, str):
            columns = [columns]
        column_selector = ",\n".join("    avg({0}) AS {0}_mean, stdev({0}) AS {0}_std, count({0}) AS {0}_count".format(c) for c in columns)
        column_selector = ',\n'+column_selector

        df = pd.read_sql("""SELECT
                                strftime('%Y-%m-%d', time, 'unixepoch', 'localtime') AS day,
                                CAST(strftime('%H', time, 'unixepoch', 'localtime') AS INTEGER) AS hour,
                                count(*) as count {column_selector}
                            FROM "{table}"
                               WHERE 1 {user_selector}
                            GROUP BY day, hour
                            {limit}
                         """.format(table=table, column_selector=column_selector,
                                    user_selector=self._user_selector(user), limit=self._sql_limit(limit)),
                         self.conn, params={'user':user})
        return df


    def raw(self, table, user, limit=None):
        df = pd.read_sql("""SELECT
                                *
                            FROM "{table}"
                               WHERE 1 {user_selector}
                            {limit}
                        """.format(table=table, user_selector=self._user_selector(user), limit=self._sql_limit(limit)),
                        self.conn, params={'user':user})
        if 'time' in df:
            df['datetime'] = pd.to_datetime(df['time'],unit='s')
        return df

    def get_survey_score(self, table, user, survey):
        questions = self.raw(table=table, user=user)
        answers=questions[questions['id'].str.startswith(survey+'_')]
        answers['answer'] = pd.to_numeric(answers['answer'])
        survey_score=answers.groupby(['user','time'])['answer'].sum(skipna=False)
        survey_score=survey_score.to_frame()
        return survey_score
