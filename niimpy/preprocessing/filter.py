"""Generic DataFrame filtering

This module provides functions for generic DataFrame filtering.  In many
cases, it is simpler to do these filtering operations yourself directly
on the DataFrames, but these functions simplify the operations of
standard arguments in other functions.
"""


def filter_dataframe(df, user=None, start=None, end=None, rename_columns={}):
    """Standard dataframe preprocessing filter.

    This implements some standard and common dataframe preprocessing
    options, which are used in very many functions.  It is likely
    simpler and more clear to do these yourself on the DataFrames
    directly.

    - select only certain user: `df['user'] == user`
    - select date range:  `df[start:end]`
- column map: `df.rename(columns=rename_columns)`

    It returns a new dataframe (and does not modify the passed one in-place).
    """
    if user:
        df = df[df['user'] == user]
    # Slice by time
    time_slice = None
    # start and end
    if start is not None and end is not None:
        time_slice = slice(start, end)
    # start only
    elif start is not None:
        time_slice = slice(start, None)
    # end only
    elif end is not None:
        time_slice = slice(None, end)
    if time_slice is not None:
        df = df.loc[time_slice]

    if rename_columns:
        df = df.rename(columns=rename_columns)

    return df
