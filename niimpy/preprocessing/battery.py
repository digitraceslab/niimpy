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
    df_u.sort_values(by=["user","datetime"], inplace=True)
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
    
    df.sort_values(by=["user","datetime"], inplace=True)
    
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


ALL_FEATURE_FUNCTIONS = [globals()[name] for name in globals()
                         if name.startswith('battery_')]
ALL_FEATURE_FUNCTIONS = {x: {} for x in ALL_FEATURE_FUNCTIONS}


def extract_features_battery(df, feature_functions=None):
    """Calculates battery features

    Parameters
    ----------
    df : pd.DataFrame
        dataframe of location data. It must contain these columns:
        `battery_level` and `battery_status`.
        If not provided, it will be computed manually.
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
        computed_feature = feature_function(df, **kwargs)
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)

    if 'group' in df:
        computed_features['group'] = df.groupby('user')['group'].first()

    return computed_features
