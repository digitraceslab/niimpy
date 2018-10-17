import numpy as np
import pandas as pd

def occurrence(series, bin_width=12, grouping_width=60):
    """Number of 12-minute

    This reproduces the logic of the "occurrence" database function, without needing the database.

    inputs: pandas.Series of pandas.Timestamps
    
    Output: pandas.DataFrame with timestamp index and 'occurance' column.
    
    TODO: use the grouping_width option.
    """
    if grouping_width % bin_width != 0:
        raise ValueError("grouping_width must be a multiple of bin_width")
    
    if not np.issubdtype(series.dtype, np.datetime64):
        df = pd.to_datetime(series, unit='s')
        print(series.head())
    df = pd.DataFrame({"time":series})

    df['day'] = df['time'].dt.strftime("%Y-%m-%d")
    df['hour'] = df['time'].dt.hour
    df['bin'] = df['time'].dt.minute // bin_width

    gb1 = df.groupby(by=["day", "hour", "bin"], as_index=False).size()   # everything in the same bin goes to one row
    gb2 = gb1.groupby(by=["day", "hour"]).size().to_frame()         # count number of bins in an hour
    gb2.rename({0:"occurance"}, axis=1, inplace=True)
    # Following handles cases where there are not enough rows... TODO what is the right thing to do here?
    gb2.reset_index(inplace=True)
    gb2.index = gb2.loc[:, ['day', 'hour']].apply(lambda row: pd.Timestamp('%s %s:00'%(row['day'], row['hour'])), axis=1)
    return gb2
