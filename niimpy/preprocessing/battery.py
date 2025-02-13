import numpy as np
import pandas as pd

from niimpy.preprocessing import util


def shutdown_info(df, battery_column_name = "battery_status", **kwargs):
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
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc.
    Returns
    -------
    shutdown: pandas series
    """
    df[battery_column_name] = pd.to_numeric(df[battery_column_name]) #convert to numeric in case it is not

    shutdown = df[df[battery_column_name].between(-3, 0, inclusive="neither")]
    return shutdown


def battery_mean_level(df, battery_column_name = "battery_level", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the mean battery level within the specified timeframe. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    df[battery_column_name] = pd.to_numeric(df[battery_column_name]) #convert to numeric in case it is not
    
    if len(df)>0:
        result = util.group_data(df)[battery_column_name].resample(**resample_args).mean()
        result = result.to_frame(name='battery_mean_level')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["battery_mean_level"])
    return result


def battery_median_level(df, battery_column_name = "battery_level", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the median battery level within the specified timeframe. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    df[battery_column_name] = pd.to_numeric(df[battery_column_name]) #convert to numeric in case it is not
    
    if len(df)>0:
        result = util.group_data(df)[battery_column_name].resample(**resample_args).median()
        result = result.to_frame(name='battery_median_level')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["battery_median_level"])
    return result


def battery_std_level(df, battery_column_name = "battery_level", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the standard deviation battery level within the specified timeframe. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """    
    df[battery_column_name] = pd.to_numeric(df[battery_column_name]) #convert to numeric in case it is not
    
    if len(df)>0:
        result = util.group_data(df)[battery_column_name].resample(**resample_args).std()
        result = result.to_frame(name='battery_std_level')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["battery_std_level"])
    return result


def battery_shutdown_time(df, battery_column_name = "battery_status", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the total time the phone has been turned off within a specified time window. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """
    def calculate_shutdown(df):
        df['next'] = df[battery_column_name].astype(int).astype(str)+df[battery_column_name].shift(-1).fillna(0).astype(int).astype(str) 
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
           
        result = duration.resample(**resample_args).sum()
        result = result.to_frame(name='shutdown_time')
        return result

    result = util.group_data(df).apply(calculate_shutdown)
    result = util.reset_groups(result)
    result = util.select_columns(result, ["shutdown_time"])
    return result
    

def battery_discharge(df, battery_column_name = "battery_level", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the mean discharge rate of the battery within a specified time window. 
    If there is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    Returns
    -------
    result: dataframe
    """    
    def calculate_discharge(df):
        df.sort_index(inplace=True)
    
        df['duration'] = np.nan
        df['duration'] = df.index.to_series().diff()
        df['duration'] = df['duration'].shift(-1)
        df["duration"] = df["duration"].dt.total_seconds()
        df['discharge'] = (df[battery_column_name].shift(-1) - df[battery_column_name])/df['duration']
        df['discharge'] = df['discharge'].shift(1)
       
        result = None
        if len(df)>0:
            result = df['discharge'].resample(**resample_args).mean()
            result = result.to_frame(name='battery_discharge')
        return result
    
    result = util.group_data(df).apply(calculate_discharge)
    result = util.reset_groups(result)
    result = util.select_columns(result, ["battery_discharge"])
    return result


def format_battery_data(df, batterylevel_column = "battery_level"):
    """ Returns a DataFrame with battery data for a user.
    Parameters
    ----------
    battery: DataFrame with battery data
    """
    df[batterylevel_column] = pd.to_numeric(df[batterylevel_column])
    return df


def battery_occurrences(df, battery_status=False, battery_status_column_name="battery_status", resample_args={"rule":"30min"}, **kwargs):
    """ Returns a dataframe showing the amount of battery data points found within a specified time window.
    If there is no specified timeframe, the function sets a 30 min default time window.
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of batter
        information. Keys can be column names, other dictionaries, etc. 
    """
    assert isinstance(df, pd.DataFrame), "data is not a pandas DataFrame"

    occurrence_data = df.drop_duplicates(subset=['datetime', 'device', battery_status_column_name], keep='last')

    if ((battery_status == True) & (battery_status_column_name in occurrence_data.columns)):
        def count_alive(series):
            return ((series == '-1') | (series == '-2') | (series == '-3')).sum()
        
        occurrence_data["time"] = occurrence_data.index
        occurrences = util.group_data(occurrence_data).resample(
            **resample_args, include_groups=False
        ).agg({
            "time": "count",
            battery_status_column_name: count_alive
        }).to_frame(name='occurrences')

    else:
        occurrence_data["time"] = occurrence_data.index
        occurrences = util.group_data(occurrence_data).resample(
            **resample_args, include_groups=False
        )["time"].count()
        occurrences = occurrences.to_frame(name='occurrences')

    occurrences = util.reset_groups(occurrences)
    occurrences = util.select_columns(occurrences, ["occurrences"])
    return occurrences


def battery_gaps(df, min_duration_between = None, resample_args = {"rule":"30min"}, **kwargs):
    '''Returns a DataFrame with the mean time difference between consecutive battery
    timestamps. The mean is calculated within intervals specified in config.
    The minimum size of the considered deltas can be decided with the min_duration_between
    parameter.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of batter
        information. Keys can be column names, other dictionaries, etc. 

    Optional arguments in config:
        min_duration_between: Timedelta, for example, pd.Timedelta(minutes=5)
    '''
    assert isinstance(df, pd.core.frame.DataFrame), "df is not a pandas DataFrame"
    assert isinstance(df.index, pd.core.indexes.datetimes.DatetimeIndex), "df index is not DatetimeIndex"

    def calculate_gaps(df):
        tvalue = df.index.to_series()
        delta = (tvalue - tvalue.shift()).fillna(pd.Timedelta(seconds=0))
        if (min_duration_between is not None):
            delta[delta < min_duration_between] = None

        delta = delta.resample(**resample_args).mean()

        return pd.DataFrame({"battery_gap": delta})
    
    result = util.group_data(df).apply(calculate_gaps, include_groups=False)
    result = util.reset_groups(result)
    result = util.select_columns(result, ["battery_gap"])
    return result


def battery_charge_discharge(df, battery_level_column = "battery_level", resample_args = {"rule":"30min"}, **kwargs):
    '''Returns a DataFrame showing the mean difference in battery values and mean battery
    charge/discharge rate within specified time windows.
    If there is no specified timeframe, the function sets a 30 min default time window.
    Parameters
    ----------
    df: dataframe with date index
    '''
    assert isinstance(df, pd.core.frame.DataFrame), "df is not a pandas DataFrame"
    assert isinstance(df.index, pd.core.indexes.datetimes.DatetimeIndex), "df index is not DatetimeIndex"

    def calculate_discharge(df):
        battery_level = pd.to_numeric(df[battery_level_column])
        tvalue = battery_level.index.to_series()
        tdelta = (tvalue - tvalue.shift()).fillna(pd.Timedelta(seconds=0))
        bdelta = (battery_level - battery_level.shift()).fillna(0)
        delta = bdelta / (tdelta / pd.Timedelta(seconds=1))
        bdelta = bdelta.resample(**resample_args).mean()
        delta = delta.resample(**resample_args).mean()
        return pd.DataFrame({
            'bdelta': bdelta,
            'charge/discharge': delta
        })

    discharge = util.group_data(df).apply(calculate_discharge, include_groups=False)
    discharge = util.reset_groups(discharge)
    discharge = util.select_columns(discharge, ["bdelta", "charge/discharge"])
    return discharge


def find_real_gaps(battery_df, other_df, **kwargs):
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
    
    battery = battery_occurrences(battery_df, **kwargs)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_df, **kwargs)

    mask = (battery['battery_occurrences'] == 0) & (other['occurrences'] == 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps


def find_non_battery_gaps(battery_df, other_df, **kwargs):
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

    battery = battery_occurrences(battery_df, **kwargs)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_df, **kwargs)
    mask = (battery['battery_occurrences'] > 10) & (other['occurrences'] == 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps


def find_battery_gaps(battery_df, other_df, **kwargs):
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

    battery = battery_occurrences(battery_df, **kwargs)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace=True)
    other = battery_occurrences(other_df, **kwargs)
    mask = (battery['battery_occurrences'] == 0) & (other['occurrences'] > 0)
    gaps = pd.concat([battery[mask], other[mask]['occurrences']], axis=1, sort=False)

    return gaps

ALL_FEATURES = [globals()[name] for name in globals()
                         if name.startswith('battery_')]
ALL_FEATURES = {x: {} for x in ALL_FEATURES}


def extract_features_battery(df, features=None):
    """Calculates battery features

    Parameters
    ----------
    df : pd.DataFrame
        dataframe of battery data. It must contain these columns:
        `battery_level` and `battery_status`.
    features : map (dictionary) of functions that compute features.
        it is a map of map, where the keys to the first map is the name of
        functions that compute features and the nested map contains the keyword
        arguments to that function. If there is no arguments use an empty map.
        Default is None. If None, all the available functions are used.
        Those functions are in the dict `battery.ALL_FEATURES`.
        You can implement your own function and use it instead or add it
        to the mentioned map.

    Returns
    -------
    features : pd.DataFrame
        Dataframe of computed features where the index is users and columns
        are the the features.
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas DataFrame"

    computed_features = []
    if features is None:
        features = ALL_FEATURES
    for features, kwargs in features.items():
        print(features, kwargs)
        computed_feature = features(df, **kwargs)
        computed_feature = util.set_conserved_index(computed_feature)
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)
    computed_features = util.reset_groups(computed_features)
    return computed_features
