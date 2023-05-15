import numpy as np
import pandas as pd

import niimpy

def shutdown_info(df, feature_functions):
    """ Returns a pandas DataFrame with battery information for the timestamps when the phone
    has shutdown.
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

    shutdown = df[df[col_name].between(-3, 0, inclusive="neither")]
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
        result = result.to_frame(name='battery_median_level')
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
        result = result.to_frame(name='battery_std_level')
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

    def calculate_shutdown(df):
        df['next'] = df[col_name].astype(int).astype(str)+df[col_name].shift(-1).fillna(0).astype(int).astype(str) 
        ids = np.where((df.next=='-32') | (df.next=='-33') | (df.next=='-12') | (df.next=='-13') | (df.next=='-22') | (df.next=='-23'))[0]
        ids = ids.tolist()
        [ids.append(ids[i]+1) for i in range(len(ids))]
        ids.sort()
    
        df_u = df.iloc[ids]
        df_u.sort_index(inplace=True)
        duration = np.nan
        duration = df_u.index.to_series().diff()
        duration = duration.shift(-1).iloc[:-1]
        duration = duration.dt.total_seconds()
           
        result = duration.resample(**feature_functions["resample_args"]).sum()
        result = result.to_frame(name='shutdown_time')
        return result

    return df.groupby('user').apply(calculate_shutdown)
    

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
    
    if "battery_column_name" not in feature_functions.keys():
        col_name = "battery_level"
    else:
        col_name = feature_functions["battery_column_name"]
    
    if "resample_args" not in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    def calculate_discharge(df):
        df.sort_index(inplace=True)
    
        df['duration'] = np.nan
        df['duration'] = df.index.to_series().diff()
        df['duration'] = df['duration'].shift(-1)
        df["duration"] = df["duration"].dt.total_seconds()
        df['discharge'] = (df[col_name].shift(-1) - df[col_name])/df['duration']
        df['discharge'] = df['discharge'].shift(1)
       
        result = None
        if len(df)>0:
            result = df['discharge'].resample(**feature_functions["resample_args"]).mean()
            result = result.to_frame(name='battery_discharge')
        return result
    
    return df.groupby('user').apply(calculate_discharge)


def format_battery_data(df, feature_functions):
    """ Returns a DataFrame with battery data for a user.
    Parameters
    ----------
    battery: DataFrame with battery data
    """

    if "batterylevel_column" in feature_functions.keys():
        batterylevel_column = feature_functions["batterylevel_column"]
    else:
        batterylevel_column = "battery_level"

    df[batterylevel_column] = pd.to_numeric(df[batterylevel_column])
    return df

def battery_occurrences(df, feature_functions):
    """ Returns a dataframe showing the amount of battery data points found within a specified time window.
    If there is no specified timeframe, the function sets a 30 min default time window.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of batter
        information. Keys can be column names, other dictionaries, etc. 
    """
    assert isinstance(df, pd.DataFrame), "data is not a pandas DataFrame"

    if "resample_args" not in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}

    if "battery_status" in feature_functions.keys():
        battery_status = feature_functions["battery_status"]
    else:
        battery_status = False

    if "battery_status_column_name" not in feature_functions.keys():
        battery_status_col = "battery_status"
    else:
        battery_status_col = feature_functions["battery_status_column_name"]

    occurrence_data = df.drop_duplicates(subset=['datetime', 'device', battery_status_col], keep='last')

    if ((battery_status == True) & (battery_status_col in occurrence_data.columns)):
        def count_alive(series):
            return ((series == '-1') | (series == '-2') | (series == '-3')).sum()
        
        occurrence_data["time"] = occurrence_data.index
        occurrences = occurrence_data.groupby("user").resample(
            **feature_functions["resample_args"]
        ).agg({
            "time": "count",
            battery_status_col: count_alive
        }).to_frame(name='occurrences')

    else:
        occurrence_data["time"] = occurrence_data.index
        occurrences = occurrence_data.groupby("user").resample(
            **feature_functions["resample_args"]
        )["time"].count()
        occurrences = occurrences.to_frame(name='occurrences')
    return occurrences


def battery_gaps(df, feature_functions):
    '''Returns a DataFrame with the mean time difference between consecutive battery
    timestamps. The mean is calculated within intervals specified in feature_functions.
    The minimum size of the considered deltas can be decided with the min_duration_between
    parameter.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of batter
        information. Keys can be column names, other dictionaries, etc. 

    Optional arguments in feature_functions:
        min_duration_between: Timedelta, for example, pd.Timedelta(minutes=5)
    '''
    assert isinstance(df, pd.core.frame.DataFrame), "df is not a pandas DataFrame"
    assert isinstance(df.index, pd.core.indexes.datetimes.DatetimeIndex), "df index is not DatetimeIndex"

    if "resample_args" not in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}

    if "min_duration_between" in feature_functions.keys():
        min_duration_between = feature_functions["min_duration_between"]
    else:
        min_duration_between = None

    def calculate_gaps(df):
        tvalue = df.index.to_series()
        delta = (tvalue - tvalue.shift()).fillna(pd.Timedelta(seconds=0))
        if (min_duration_between is not None):
            delta[delta < min_duration_between] = None

        delta = delta.resample(**feature_functions["resample_args"]).mean()

        return pd.DataFrame({"battery_gap": delta})
    
    return df.groupby('user').apply(calculate_gaps)


def battery_charge_discharge(df, feature_functions):
    '''Returns a DataFrame showing the mean difference in battery values and mean battery
    charge/discharge rate within specified time windows.
    If there is no specified timeframe, the function sets a 30 min default time window.
    Parameters
    ----------
    df: dataframe with date index
    '''
    assert isinstance(df, pd.core.frame.DataFrame), "df is not a pandas DataFrame"
    assert isinstance(df.index, pd.core.indexes.datetimes.DatetimeIndex), "df index is not DatetimeIndex"

    if "battery_level_column" in feature_functions.keys():
        battery_level_column = feature_functions["battery_level_column"]
    else:
        battery_level_column = "battery_level"
    
    if "resample_args" not in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}

    def calculate_discharge(df):
        battery_level = pd.to_numeric(df[battery_level_column])
        tvalue = battery_level.index.to_series()
        tdelta = (tvalue - tvalue.shift()).fillna(pd.Timedelta(seconds=0))
        bdelta = (battery_level - battery_level.shift()).fillna(0)
        delta = bdelta / (tdelta / pd.Timedelta(seconds=1))
        bdelta = bdelta.resample(**feature_functions["resample_args"]).mean()
        delta = delta.resample(**feature_functions["resample_args"]).mean()
        return pd.DataFrame({
            'bdelta': bdelta,
            'charge/discharge': delta
        })

    discharge = df.groupby('user').apply(calculate_discharge)
    return discharge


def find_real_gaps(battery_df, other_df, feature_functions):
    """ Returns a dataframe showing the gaps found both in the battery data and the other data.
    The default interval is 6 hours.
    Parameters
    ----------
    battery_df: Dataframe
    other_df: Dataframe
                The data you want to compare with
    """
    assert isinstance(battery_df, pd.core.frame.DataFrame), "battery_df is not a pandas DataFrame"
    assert isinstance(other_df, pd.core.frame.DataFrame), "other_df is not a pandas DataFrame"
    assert isinstance(battery_df.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "battery_df index is not DatetimeIndex"
    assert isinstance(other_df.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "other_df index is not DatetimeIndex"

    battery = battery_occurrences(battery_df, feature_functions)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_df, feature_functions)

    mask = (battery['battery_occurrences'] == 0) & (other['occurrences'] == 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps


def find_non_battery_gaps(battery_df, other_df, feature_functions):
    """ Returns a dataframe showing the gaps found only in the other data.
    The default interval is 6 hours.
    Parameters
    ----------
    battery_df: Dataframe
    other_df: Dataframe
                The data you want to compare with
    """
    assert isinstance(battery_df, pd.core.frame.DataFrame), "battery_df is not a pandas DataFrame"
    assert isinstance(other_df, pd.core.frame.DataFrame), "other_df is not a pandas DataFrame"
    assert isinstance(battery_df.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "battery_df index is not DatetimeIndex"
    assert isinstance(other_df.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "other_df index is not DatetimeIndex"

    battery = battery_occurrences(battery_df, feature_functions)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_df, feature_functions)
    mask = (battery['battery_occurrences'] > 10) & (other['occurrences'] == 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps


def find_battery_gaps(battery_df, other_df, feature_functions):
    """ Returns a dataframe showing the gaps found only in the battery data.
    The default interval is 6 hours.
    Parameters
    ----------
    battery_df: Dataframe
    other_df: Dataframe
                The data you want to compare with
    """
    assert isinstance(battery_df, pd.core.frame.DataFrame), "battery_df is not a pandas DataFrame"
    assert isinstance(other_df, pd.core.frame.DataFrame), "other_df is not a pandas DataFrame"
    assert isinstance(battery_df.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "battery_df index is not DatetimeIndex"
    assert isinstance(other_df.index,
                      pd.core.indexes.datetimes.DatetimeIndex), "other_df index is not DatetimeIndex"

    battery = battery_occurrences(battery_df, feature_functions)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_df, feature_functions)
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
        dataframe of battery data. It must contain these columns:
        `battery_level` and `battery_status`.
    feature_functions : map (dictionary) of functions that compute features.
        it is a map of map, where the keys to the first map is the name of
        functions that compute features and the nested map contains the keyword
        arguments to that function. If there is no arguments use an empty map.
        Default is None. If None, all the available functions are used.
        Those functions are in the dict `battery.ALL_FEATURE_FUNCTIONS`.
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
        computed_feature = feature_function(df, kwargs)
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)

    if 'group' in df:
        computed_features['group'] = df.groupby('user')['group'].first()

    return computed_features
