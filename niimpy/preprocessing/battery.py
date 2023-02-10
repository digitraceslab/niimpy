import numpy as np
import pandas as pd

import niimpy

def shutdown_info(df, feature_functions):
    """ Returns a DataFrame with the timestamps of when the phone has shutdown.
    This includes both events, when the phone has shut down and when the phone
    has been rebooted.
    NOTE: This is a helper function created originally to preprocess the application
    info data
    Parameters
    ----------
    bat: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc.
    Returns
    -------
    shutdown: pandas series
    """
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"

    if not "battery_column_name" in feature_functions.keys():
        col_name = "battery_status"
    else:
        col_name = feature_functions["battery_column_name"]

    df[col_name] = pd.to_numeric(df[col_name]) #convert to numeric in case it is not

    shutdown = df[df[col_name].between(-3, 0, inclusive=False)]
    return shutdown

def battery_mean_level(df, feature_functions):
    """ This function returns the mean battery level within the specified timeframe. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "battery_column_name" in feature_functions.keys():
        col_name = "battery_level"
    else:
        col_name = feature_functions["battery_column_name"]
    
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name] = pd.to_numeric(df[col_name]) #convert to numeric in case it is not
    
    if len(df)>0:
        result = df.groupby('user')[col_name].resample(**feature_functions["resample_args"]).mean()
        result = result.to_frame(name='battery_mean_level')
    return result


def battery_median_level(df, feature_functions):
    """ This function returns the median battery level within the specified timeframe. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "battery_column_name" in feature_functions.keys():
        col_name = "battery_level"
    else:
        col_name = feature_functions["battery_column_name"]
    
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name] = pd.to_numeric(df[col_name]) #convert to numeric in case it is not
    
    if len(df)>0:
        result = df.groupby('user')[col_name].resample(**feature_functions["resample_args"]).median()
        result = result.to_frame(name='battery_mean_level')
    return result


def battery_std_level(df, feature_functions):
    """ This function returns the standard deviation battery level within the specified timeframe. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "battery_column_name" in feature_functions.keys():
        col_name = "battery_level"
    else:
        col_name = feature_functions["battery_column_name"]
    
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name] = pd.to_numeric(df[col_name]) #convert to numeric in case it is not
    
    if len(df)>0:
        result = df.groupby('user')[col_name].resample(**feature_functions["resample_args"]).std()
        result = result.to_frame(name='battery_mean_level')
    return result

def battery_shutdown_time(df, feature_functions):
    """ This function returns the total time the phone has been turned off within a specified time window. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "battery_column_name" in feature_functions.keys():
        col_name = "battery_status"
    else:
        col_name = feature_functions["battery_column_name"]
    
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}

    df['next'] = df[col_name].astype(int).astype(str)+df[col_name].shift(-1).fillna(0).astype(int).astype(str) 
    ids = np.where((df.next=='-32') | (df.next=='-33') | (df.next=='-12') | (df.next=='-13') | (df.next=='-22') | (df.next=='-23'))[0]
    ids = ids.tolist()
    [ids.append(ids[i]+1) for i in range(len(ids))]
    ids.sort()
    
    df_u = df.iloc[ids]
    df_u.sort_values(by=["user","device","datetime"], inplace=True)
    df_u['duration']=np.nan
    df_u['duration']=df_u['datetime'].diff()
    df_u['duration'] = df_u['duration'].shift(-1)
    df_u["duration"] = df_u["duration"].dt.total_seconds()
    
    #Discard transitions between subjects
    if len(list(df_u.user.unique()))>1:
        df_u = df_u.groupby("user", as_index=False).apply(lambda x: x.iloc[:-1])
        df_u = df_u.droplevel(0)
       
    if len(df_u)>0:
        result = df_u.groupby('user')['duration'].resample(**feature_functions["resample_args"]).sum()
        result = result.to_frame(name='shutdown_time')
    return result

def battery_discharge(df, feature_functions):
    """ This function returns the mean discharge rate of the battery within a specified time window. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "battery_column_name" in feature_functions.keys():
        col_name = "battery_level"
    else:
        col_name = feature_functions["battery_column_name"]
    
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    df.sort_values(by=["user","device","datetime"], inplace=True)
    
    df['duration'] = np.nan
    df['duration'] = df['datetime'].diff()
    df['duration'] = df['duration'].shift(-1)
    df["duration"] = df["duration"].dt.total_seconds()
    df['discharge'] = (df[col_name].shift(-1) - df[col_name])/df['duration']
    df['discharge'] = df['discharge'].shift(1)
    
    #Discard transitions between subjects
    if len(list(df.user.unique()))>1:
        df = df.groupby("user", as_index=False).apply(lambda x: x.iloc[:-1])
        df = df.droplevel(0)
       
    if len(df)>0:
        result = df.groupby('user')['discharge'].resample(**feature_functions["resample_args"]).mean()
        result = result.to_frame(name='battery_discharge')
    return result

def get_battery_data(battery, batterylevel_column='battery_level',
                     user=None, start=None, end=None):
    """ Returns a DataFrame with battery data for a user.
    Parameters
    ----------
    battery: DataFrame with battery data
    user: string, optional
    start: datetime, optional
    end: datetime, optional
    """
    battery = niimpy.filter_dataframe(battery, begin=start, end=end, user=user)
    battery[batterylevel_column] = pd.to_numeric(battery[batterylevel_column])

    battery = battery.drop_duplicates(subset=['datetime', 'user', 'device'], keep='last')
    battery = battery.drop(['user', 'device', 'time', 'datetime'], axis=1)
    return battery


def battery_occurrences(battery_data, battery_status=False,
                        days=0, hours=6, minutes=0, seconds=0, milli=0, micro=0, nano=0,
                        user=None, start=None, end=None):
    """ Returns a dataframe showing the amount of battery data points found between a given interval and steps.
    The default interval is 6 hours.
    Parameters
    ----------
    battery_data: Dataframe
    user: string, optional
    start: datetime, optional
    end: datetime, optional
    battery_status: boolean, optional
    """

    assert isinstance(battery_data, pd.DataFrame), "data is not a pandas DataFrame"
    assert isinstance(user, (type(None), str)), "user not given in string format"

    if (user != None):
        ocurrence_data = battery_data[(battery_data['user'] == user)]
    else:
        occurrence_data = battery_data

    occurrence_data = occurrence_data.drop_duplicates(subset=['datetime', 'device'], keep='last')
    occurrence_data.sort_values(by=['time'], inplace=True)

    if (start == None):
        start = occurrence_data.iloc[0]['datetime']
        start = pd.to_datetime(start)

    td = pd.Timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milli, microseconds=micro,
                      nanoseconds=nano)

    delta = start + td

    if (end == None):
        end = occurrence_data.iloc[len(occurrence_data) - 1]['datetime']
        end = pd.to_datetime(end)

    idx_range = np.floor((end - start) / td).astype(int)
    idx = pd.date_range(start, periods=idx_range, freq=td)

    if ((battery_status == True) & ('battery_status' in occurrence_data.columns)):
        occurrences = pd.DataFrame(np.nan, index=idx, columns=list(['start', 'end', 'occurrences', 'battery_status']))
        for i in range(idx_range):
            idx_dat = occurrence_data.loc[
                (occurrence_data['datetime'] > start) & (occurrence_data['datetime'] <= delta)]
            battery_status = occurrence_data.loc[
                (occurrence_data['datetime'] > start) & (occurrence_data['datetime'] <= delta) & (
                            (occurrence_data['battery_status'] == '-1') | (
                                occurrence_data['battery_status'] == '-2') | (
                                        occurrence_data['battery_status'] == '-3'))]
            occurrences.iloc[i] = [start, delta, len(idx_dat), len(battery_status)]
            start = start + td
            delta = start + td


    else:
        occurrences = pd.DataFrame(np.nan, index=idx, columns=list(['start', 'end', 'occurrences']))
        for i in range(idx_range):
            idx_dat = occurrence_data.loc[
                (occurrence_data['datetime'] > start) & (occurrence_data['datetime'] <= delta)]
            occurrences.iloc[i] = [start, delta, len(idx_dat)]
            start = start + td
            delta = start + td
    return occurrences


def battery_gaps(data, min_duration_between=None):
    '''Returns a DataFrame including all battery data and showing the delta between
    consecutive battery timestamps. The minimum size of the considered deltas can be decided
    with the min_duration_between parameter.
    Parameters
    ----------
    data: dataframe with date index
    min_duration_between: Timedelta, for example, pd.Timedelta(hours=6)
    '''
    assert isinstance(data, pd.core.frame.DataFrame), "data is not a pandas DataFrame"
    assert isinstance(data.index, pd.core.indexes.datetimes.DatetimeIndex), "data index is not DatetimeIndex"

    gaps = data.copy()
    gaps['tvalue'] = gaps.index
    gaps['delta'] = (gaps['tvalue'] - gaps['tvalue'].shift()).fillna(pd.Timedelta(seconds=0))
    if (min_duration_between != None):
        gaps = gaps[gaps['delta'] >= min_duration_between]

    return gaps


def battery_charge_discharge(data):
    '''Returns a DataFrame including all battery data and showing the charge/discharge between each timestamp.
    Parameters
    ----------
    data: dataframe with date index
    '''
    assert isinstance(data, pd.core.frame.DataFrame), "data is not a pandas DataFrame"
    assert isinstance(data.index, pd.core.indexes.datetimes.DatetimeIndex), "data index is not DatetimeIndex"

    charge = data.copy()
    charge['battery_level'] = pd.to_numeric(charge['battery_level'])
    charge['tvalue'] = charge.index
    charge['tdelta'] = (charge['tvalue'] - charge['tvalue'].shift()).fillna(pd.Timedelta(seconds=0))
    charge['bdelta'] = (charge['battery_level'] - charge['battery_level'].shift()).fillna(0)
    charge['charge/discharge'] = ((charge['bdelta']) / ((charge['tdelta'] / pd.Timedelta(seconds=1))))

    return charge


def find_real_gaps(battery_data, other_data, start=None, end=None, days=0, hours=6, minutes=0, seconds=0, milli=0,
                   micro=0, nano=0):
    """ Returns a dataframe showing the gaps found both in the battery data and the other data.
    The default interval is 6 hours.
    Parameters
    ----------
    battery_data: Dataframe
    other_data: Dataframe
                The data you want to compare with
    start: datetime, optional
    end: datetime, optional
    """
    assert isinstance(battery_data, pd.core.frame.DataFrame), "battery_data is not a pandas DataFrame"
    assert isinstance(other_data, pd.core.frame.DataFrame), "other_data is not a pandas DataFrame"
    assert isinstance(battery_data.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "battery_data index is not DatetimeIndex"
    assert isinstance(other_data.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "other_data index is not DatetimeIndex"

    if (start != None):
        start = pd.to_datetime(start)
    else:
        start = battery_data.index[0] if (battery_data.index[0] <= other_data.index[0]) else other_data.index[0]
    if (end != None):
        end = pd.to_datetime(end)
    else:
        end = battery_data.index[-1] if (battery_data.index[-1] >= other_data.index[-1]) else other_data.index[-1]

    battery = battery_occurrences(battery_data, start=start, end=end, days=days, hours=hours, minutes=minutes,
                                  seconds=seconds, milli=milli, micro=micro, nano=nano)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_data, start=start, days=days, hours=hours, minutes=minutes, seconds=seconds,
                                milli=milli, micro=micro, nano=nano)

    mask = (battery['battery_occurrences'] == 0) & (other['occurrences'] == 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps


def find_non_battery_gaps(battery_data, other_data, start=None, end=None, days=0, hours=6, minutes=0, seconds=0,
                          milli=0, micro=0, nano=0):
    """ Returns a dataframe showing the gaps found only in the other data.
    The default interval is 6 hours.
    Parameters
    ----------
    battery_data: Dataframe
    other_data: Dataframe
                The data you want to compare with
    start: datetime, optional
    end: datetime, optional
    """
    assert isinstance(battery_data, pd.core.frame.DataFrame), "battery_data is not a pandas DataFrame"
    assert isinstance(other_data, pd.core.frame.DataFrame), "other_data is not a pandas DataFrame"
    assert isinstance(battery_data.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "battery_data index is not DatetimeIndex"
    assert isinstance(other_data.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "other_data index is not DatetimeIndex"

    if (start != None):
        start = pd.to_datetime(start)
    else:
        start = battery_data.index[0] if (battery_data.index[0] <= other_data.index[0]) else other_data.index[0]
    if (end != None):
        end = pd.to_datetime(end)
    else:
        end = battery_data.index[-1] if (battery_data.index[-1] >= other_data.index[-1]) else other_data.index[-1]

    battery = battery_occurrences(battery_data, start=start, end=end, days=days, hours=hours, minutes=minutes,
                                  seconds=seconds, milli=milli, micro=micro, nano=nano)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_data, start=start, days=days, hours=hours, minutes=minutes, seconds=seconds,
                                milli=milli, micro=micro, nano=nano)
    mask = (battery['battery_occurrences'] > 10) & (other['occurrences'] == 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps


def find_battery_gaps(battery_data, other_data, start=None, end=None, days=0, hours=6, minutes=0, seconds=0, milli=0,
                      micro=0, nano=0):
    """ Returns a dataframe showing the gaps found only in the battery data.
    The default interval is 6 hours.
    Parameters
    ----------
    battery_data: Dataframe
    other_data: Dataframe
                The data you want to compare with
    start: datetime, optional
    end: datetime, optional
    """
    assert isinstance(battery_data, pd.core.frame.DataFrame), "battery_data is not a pandas DataFrame"
    assert isinstance(other_data, pd.core.frame.DataFrame), "other_data is not a pandas DataFrame"
    assert isinstance(battery_data.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "battery_data index is not DatetimeIndex"
    assert isinstance(other_data.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "other_data index is not DatetimeIndex"

    if (start != None):
        start = pd.to_datetime(start)
    else:
        start = battery_data.index[0] if (battery_data.index[0] <= other_data.index[0]) else other_data.index[0]
    if (end != None):
        end = pd.to_datetime(end)
    else:
        end = battery_data.index[-1] if (battery_data.index[-1] >= other_data.index[-1]) else other_data.index[-1]

    battery = battery_occurrences(battery_data, start=start, end=end, days=days, hours=hours, minutes=minutes,
                                  seconds=seconds, milli=milli, micro=micro, nano=nano)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_data, start=start, end=end, days=days, hours=hours, minutes=minutes,
                                seconds=seconds, milli=milli, micro=micro, nano=nano)
    mask = (battery['battery_occurrences'] == 0) & (other['occurrences'] > 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps

ALL_FEATURE_FUNCTIONS = [globals()[name] for name in globals()
                         if name.startswith('battery_')]
ALL_FEATURE_FUNCTIONS = {x: {} for x in ALL_FEATURE_FUNCTIONS}


def extract_features_battery(df, feature_functions=None):
    """Calculates battery features

    Parameters
    ----------
    df : pd.DataFrame
        dataframe of location data. It must contain these columns:
        `battery_occurences`, `double_longitude`, `user`, `group`.
        `double_speed` is optional. If not provided, it will be
        computed manually.
    feature_functions : map (dictionary) of functions that compute features.
        it is a map of map, where the keys to the first map is the name of
        functions that compute features and the nested map contains the keyword
        arguments to that function. If there is no arguments use an empty map.
        Default is None. If None, all the available functions are used.
        Those functions are in the dict `location.ALL_FEATURE_FUNCTIONS`.
        You can implement your own function and use it instead or add it
        to the mentioned map.

    Returns
    -------
    features : pd.DataFrame
        Dataframe of computed features where the index is users and columns
        are the the features.
    """
    computed_features = []
    if feature_functions is None:
        feature_functions = ALL_FEATURE_FUNCTIONS
    for feature_function, kwargs in feature_functions.items():
        print(feature_function, kwargs)
        computed_feature = feature_function(df, **kwargs)
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)

    if 'group' in df:
        computed_features['group'] = df.groupby('user')['group'].first()

    return computed_features
