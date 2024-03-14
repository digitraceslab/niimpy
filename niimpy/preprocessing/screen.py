import numpy as np
import pandas as pd

import niimpy
from niimpy.preprocessing import battery as b

group_by_columns = set(["user", "device"])

def group_data(df):
    """ Group the dataframe by a standard set of columns listed in
    group_by_columns."""
    columns = list(group_by_columns & set(df.columns))
    return df.groupby(columns)

def reset_groups(df):
    """ Group the dataframe by a standard set of columns listed in
    group_by_columns."""
    columns = list(group_by_columns & set(df.index.names))
    return df.reset_index(columns)

def util_screen(df, bat, config):
    """ This function is a helper function for all other screen preprocessing.
    The function has the option to merge information from the battery sensors to
    include data when the phone is shut down. The function also detects the missing 
    datapoints (i.e. not allowed transitions like ON to ON). 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
        
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("screen_column_name", "screen_status")
    
    df[col_name]=pd.to_numeric(df[col_name]) #convert to numeric in case it is not

    #Include the missing points that are due to shutting down the phone
    if not bat.empty:
        shutdown = b.shutdown_info(bat, config)
        shutdown = shutdown.replace([-1,-2],0)
        
        if not shutdown.empty:
            df = pd.concat([df, shutdown])
            df.fillna(0, inplace=True)
            df = df[["user","device","time",col_name]]

    #Sort the dataframe
    df.sort_index(inplace=True)
    df.sort_values(by=["user","device"], inplace=True)
    
    #Detect missing data points
    df['missing']=0
    df['next']=df[col_name].shift(-1)
    df['dummy']=df[col_name]-df['next']
    df['missing'] = np.where(df['dummy']==0, 1, 0) #Check the missing points and label them as 1
    df['missing'] = df['missing'].shift(1)
    df.drop(['dummy','next'], axis=1, inplace=True)
    df.fillna(0, inplace=True)
   
    df = df[df.missing == 0] #Discard missing values
    df.drop(["missing"], axis=1, inplace=True)
    return df

def event_classification_screen(df, config):
    """ This function is a helper function for other screen preprocessing.
    The function classifies the screen events into four transition types: on, 
    off, in use, and undefined, based on the screen events recorded. For example,
    if two consecutive events are 0 and 3, there has been a transition from off
    to unlocked, i.e. the phone has been unlocked and the events will be 
    classified into the "use" transition. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    
    #Classify the event 
    df.sort_index(inplace=True)
    df.sort_values(by=["user","device"], inplace=True)
    df['next'] = df[col_name].shift(-1)
    df['next'] = df[col_name].astype(int).astype(str)+df[col_name].shift(-1).fillna(0).astype(int).astype(str)   
    df = df.groupby("user").apply(lambda x: x.iloc[:-1], include_groups=False) #Discard transitions between subjects
    df = df.reset_index().set_index("level_1")
    df["use"] =  df["on"] = df["na"] = df["off"] = 0
    
    df.loc[(df.next=='30') | (df.next=='31') | (df.next=='32'), "use"]=1 #in use
    df.loc[(df.next=='10') | (df.next=='12') | (df.next=='13') | (df.next=='20'), "on"]=1 #on
    df.loc[(df.next=='21') | (df.next=='23'), "na"]=1 #irrelevant. It seems like from 2 to 1 is from off to on (i.e. the screen goes to off and then it locks)
    df.loc[(df.next=='01') | (df.next=='02') | (df.next=='03'), "off"]=1 #off
    
    df.drop(columns=["next",col_name], inplace=True)   
    
    #Discard the first and last row because they do not have all info. We do not
    #know what happened before or after these points.
    df.index = df.index.set_names(['level_1'])
    df = df.groupby("user").apply(lambda x: x.iloc[1:], include_groups=False)
    df = df.reset_index().set_index("level_1")
    df = df.groupby("user").apply(lambda x: x.iloc[:-1], include_groups=False)
    df = df.reset_index().set_index("level_1")
    return df

def duration_util_screen(df):
    """ This function is a helper function for other screen preprocessing.
    The function computes the duration of an event, based on the classification
    function event_classification_screen. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
            
    df.sort_index(inplace=True)
    df.sort_values(by=["user","device"], inplace=True)
    df['duration']=np.nan
    df['duration']=df.index.to_series().diff()
    df['duration'] = df['duration'].shift(-1)
    
    #Discard transitions between subjects
    df = df.groupby("user").apply(lambda x: x.iloc[:-1], include_groups=False)
    df = df.reset_index().set_index("level_1")
    
    #Discard any datapoints whose duration in “ON” and "IN USE" states are 
    #longer than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df = df[~((df.on==1) & (df.duration>thr))]
    df = df[~((df.use==1) & (df.duration>thr))]
    df["duration"] = df["duration"].dt.total_seconds()
    
    return df

def screen_off(df, bat, config):
    """ This function returns the timestamps, within the specified timeframe, 
    when the screen has turned off. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. 
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]        
    
    df = util_screen(df, bat, config)
    df = df[df.screen_status == 0] #Select only those OFF events when no missing data is present
    df["screen_status"] = 1
    df = df[["user","device","screen_status"]]
    df.rename(columns={"screen_status":"screen_off"}, inplace=True)
    df = reset_groups(df)
    return df

def screen_count(df, bat, config=None):
    """ This function returns the number of times, within the specified timeframe, 
    when the screen has turned off, turned on, and been in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
        
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)
    
    if len(df2)>0:
        on = group_data(df2)["on"].resample(**config["resample_args"]).sum()
        on = on.to_frame(name='screen_on_count')
        off = group_data(df2)["off"].resample(**config["resample_args"]).sum()
        off = off.to_frame(name='screen_off_count')
        use = group_data(df2)["use"].resample(**config["resample_args"]).sum()
        use = use.to_frame(name='screen_use_count')
        result = pd.concat([on, off, use], axis=1)
        result = reset_groups(result)
    return result

def screen_duration(df, bat, config=None):
    """ This function returns the duration (in seconds) of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """      
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)           
    df2 = duration_util_screen(df2)
    
    if len(df2)>0:
        on = group_data(df2[df2.on==1])["duration"].resample(**config["resample_args"]).sum()
        on = on.to_frame(name='screen_on_durationtotal')
        off = group_data(df2[df2.off==1])["duration"].resample(**config["resample_args"]).sum()
        off = off.to_frame(name='screen_off_durationtotal')
        use = group_data(df2[df2.use==1])["duration"].resample(**config["resample_args"]).sum()
        use = use.to_frame(name='screen_use_durationtotal')
        result = pd.concat([on, off, use], axis=1)
        result = reset_groups(result)
    return result

def screen_duration_min(df, bat, config=None):
    """ This function returns the duration (in seconds) of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """      
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)           
    df2 = duration_util_screen(df2)
    
    if len(df2)>0:
        on = group_data(df2[df2.on==1])["duration"].resample(**config["resample_args"]).min()
        on = on.to_frame(name='screen_on_durationminimum')
        off = group_data(df2[df2.off==1])["duration"].resample(**config["resample_args"]).min()
        off = off.to_frame(name='screen_off_durationminimum')
        use = group_data(df2[df2.use==1])["duration"].resample(**config["resample_args"]).min()
        use = use.to_frame(name='screen_use_durationminimum')
        result = pd.concat([on, off, use], axis=1)
        result = reset_groups(result)
    return result

def screen_duration_max(df, bat, config=None):
    """ This function returns the duration (in seconds) of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """      
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)           
    df2 = duration_util_screen(df2)
    
    if len(df2)>0:
        on = group_data(df2[df2.on==1])["duration"].resample(**config["resample_args"]).max()
        on = on.to_frame(name='screen_on_durationmaximum')
        off = group_data(df2[df2.off==1])["duration"].resample(**config["resample_args"]).max()
        off = off.to_frame(name='screen_off_durationmaximum')
        use = group_data(df2[df2.use==1])["duration"].resample(**config["resample_args"]).max()
        use = use.to_frame(name='screen_use_durationmaximum')
        result = pd.concat([on, off, use], axis=1)
        result = reset_groups(result)
    return result

def screen_duration_mean(df, bat, config=None):
    """ This function returns the duration (in seconds) of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """      
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)           
    df2 = duration_util_screen(df2)
    
    if len(df2)>0:
        on = group_data(df2[df2.on==1])["duration"].resample(**config["resample_args"]).mean()
        on = on.to_frame(name='screen_on_durationmean')
        off = group_data(df2[df2.off==1])["duration"].resample(**config["resample_args"]).mean()
        off = off.to_frame(name='screen_off_durationmean')
        use = group_data(df2[df2.use==1])["duration"].resample(**config["resample_args"]).mean()
        use = use.to_frame(name='screen_use_durationmean')
        result = pd.concat([on, off, use], axis=1)
        result = reset_groups(result)
    return result

def screen_duration_median(df, bat, config=None):
    """ This function returns the duration (in seconds) of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """      
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)           
    df2 = duration_util_screen(df2)
    
    if len(df2)>0:
        on = group_data(df2[df2.on==1])["duration"].resample(**config["resample_args"]).median()
        on = on.to_frame(name='screen_on_durationmedian')
        off = group_data(df2[df2.off==1])["duration"].resample(**config["resample_args"]).median()
        off = off.to_frame(name='screen_off_durationmedian')
        use = group_data(df2[df2.use==1])["duration"].resample(**config["resample_args"]).median()
        use = use.to_frame(name='screen_use_durationmedian')
        result = pd.concat([on, off, use], axis=1)
        result = reset_groups(result)
    return result

def screen_duration_std(df, bat, config=None):
    """ This function returns the duration (in seconds) of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """      
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)           
    df2 = duration_util_screen(df2)
    
    if len(df2)>0:
        on = group_data(df2[df2.on==1])["duration"].resample(**config["resample_args"]).std()
        on = on.to_frame(name='screen_on_durationstd')
        off = group_data(df2[df2.off==1])["duration"].resample(**config["resample_args"]).std()
        off = off.to_frame(name='screen_off_durationstd')
        use = group_data(df2[df2.use==1])["duration"].resample(**config["resample_args"]).std()
        use = use.to_frame(name='screen_use_durationstd')
        result = pd.concat([on, off, use], axis=1)
        result = reset_groups(result)
    return result

def screen_first_unlock(df, bat, config):
    """ This function returns the first time the phone was unlocked each day. 
    The data is aggregated by user, by day.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """ 
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"
    
    if not "screen_column_name" in config:
        col_name = "screen_status"
    else:
        col_name = config["screen_column_name"]
    if not "resample_args" in config:
        config["resample_args"] = {"rule":"30min"}
    
    df2 = util_screen(df, bat, config)
    df2 = event_classification_screen(df2, config)

    df2["time"] = df2.index
    result = group_data(df2[df2.on==1])["time"].resample(rule='1D').min()
    result = result.to_frame(name="first_unlock")
    result = reset_groups(result)
    return result

ALL_FEATURES = [globals()[name] for name in globals() if name.startswith('screen_')]
ALL_FEATURES = {x: {} for x in ALL_FEATURES}

def extract_features_screen(df, bat, features=None):
    """ This function computes and organizes the selected features for screen events
    that have been recorded using Aware Framework. The function aggregates the features
    by user, by time window. If no time window is specified, it will automatically aggregate
    the features in 30 mins non-overlapping windows. 
    
    The complete list of features that can be calculated are: screen_off, screen_count,
    screen_duration, screen_duration_min, screen_duration_max, screen_duration_median,
    screen_duration_mean, screen_duration_std, and screen_first_unlock.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    features: dict
        Dictionary keys contain the names of the features to compute. 
        If none is given, all features will be computed.
    
    Returns
    -------
    computed_features: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    if features is None:
        features = ALL_FEATURES
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        computed_feature = feature(df, bat, feature_arg)
        index_by = list(group_by_columns & set(computed_feature.columns))
        computed_feature = computed_feature.set_index(index_by, append=True)
        computed_features.append(computed_feature)
    
    computed_features = pd.concat(computed_features, axis=1)
    computed_features = reset_groups(computed_features)
    return computed_features