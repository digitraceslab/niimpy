"""Read data from various formats, user entery point.

"""

from . import database 

def read_sql(filename, table, user=database.ALL, limit=None, offset=None, start=None, end=None):
    db = database.Data1(filename)
    return db.raw(table, user, limit=limit, offset=offset, start=start, end=end)
    
        