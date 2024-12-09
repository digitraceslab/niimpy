import pandas as pd

from niimpy.preprocessing import util

group_by_columns = set(["user", "device", "group"])


def audio_count_silent(df_u, audio_column_name = "is_silent", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound in the environment. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of screen
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"    
    df_u[audio_column_name] = pd.to_numeric(df_u[audio_column_name])
        
    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).sum()
        result = result.to_frame(name='audio_count_silent')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_count_silent"])
        return result
    return None

def audio_count_speech(df_u, audio_column_name = "is_silent", audio_freq_name = "frequency", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound between 65Hz and 255Hz in the environment that could
    be specified as speech. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"    
        
    df_u[audio_column_name] = pd.to_numeric(df_u[audio_column_name])
    
    if len(df_u)>0:
        df_s = df_u[df_u[audio_freq_name].between(65, 255)]
        df_s = df_s[df_s[audio_column_name]==0] #check if there was a conversation. 0 is not silent, 1 is silent
        df_s.loc[:,audio_column_name] = 1
        result = util.group_data(df_s)[audio_column_name].resample(**resample_args).sum()
        result = result.to_frame(name='audio_count_speech')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_count_speech"])
        return result
    return None

def audio_count_loud(df_u, audio_column_name = "decibels", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound louder than 70dB in the environment. If there 
    is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
        
    df_u[audio_column_name] = pd.to_numeric(df_u[audio_column_name])
    
    if len(df_u)>0:
        df_u = df_u[df_u[audio_column_name]>70] #check if environment was noisy
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).count()
        result = result.to_frame(name='audio_count_loud')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_count_loud"])
        return result
    return None

def audio_min_freq(df_u, audio_column_name = "frequency", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the minimum frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).min()
        result = result.to_frame(name='audio_min_freq')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_min_freq"])
        return result
    return None

def audio_max_freq(df_u, audio_column_name = "frequency", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the maximum frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"

    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).max()
        result = result.to_frame(name='audio_max_freq')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_max_freq"])
        return result
    return None

def audio_mean_freq(df_u, audio_column_name = "frequency", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the mean frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"

    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).mean()
        result = result.to_frame(name='audio_mean_freq')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_mean_freq"])
        return result
    return None

def audio_median_freq(df_u, audio_column_name = "frequency", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the median frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"

    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).median()
        result = result.to_frame(name='audio_median_freq')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_median_freq"])
        return result
    return None

def audio_std_freq(df_u, audio_column_name = "frequency", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the standard deviation of the frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).std()
        result = result.to_frame(name='audio_std_freq')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_std_freq"])
        return result
    return None

def audio_min_db(df_u, audio_column_name = "decibels", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the minimum decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).min()
        result = result.to_frame(name='audio_min_db')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_min_db"])
        return result
    return None

def audio_max_db(df_u, audio_column_name = "decibels", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the maximum decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).max()
        result = result.to_frame(name='audio_max_db')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_max_db"])
        return result
    return None

def audio_mean_db(df_u, audio_column_name = "decibels", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the mean decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"

    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).mean()
        result = result.to_frame(name='audio_mean_db')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_mean_db"])
        return result
    return None

def audio_median_db(df_u, audio_column_name = "decibels", resample_args = {"rule":"30min"}, **kwargs):
    """ This function returns the median decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).median()
        result = result.to_frame(name='audio_median_db')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_median_db"])
        return result
    return None

def audio_std_db(df_u, audio_column_name = "decibels", resample_args = {"rule":"30min"}, **kwargs): 
    """ This function returns the standard deviation of the decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    config: dict, optional
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
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"

    if len(df_u)>0:
        result = util.group_data(df_u)[audio_column_name].resample(**resample_args).std()
        result = result.to_frame(name='audio_std_db')
        result = util.reset_groups(result)
        result = util.select_columns(result, ["audio_std_db"])
        return result
    return None

ALL_FEATURES = [globals()[name] for name in globals() if name.startswith('audio_')]
ALL_FEATURES = {x: {} for x in ALL_FEATURES}

def extract_features_audio(df, features=None):
    """ This function computes and organizes the selected features for audio snippets 
    that have been recorded using Aware Framework. The function aggregates the features
    by user, by time window. If no time window is specified, it will automatically aggregate
    the features in 30 mins non-overlapping windows. 
    
    The complete list of features that can be calculated are: audio_count_silent, 
    audio_count_speech, audio_count_loud, audio_min_freq, audio_max_freq, audio_mean_freq, 
    audio_median_freq, audio_std_freq, audio_min_db, audio_max_db, audio_mean_db, 
    audio_median_db, audio_std_db
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    features: dict, optional
        Dictionary keys contain the names of the features to compute. 
        If none is given, all features will be computed.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    if features is None:
        features = ALL_FEATURES
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        computed_feature = feature(df, **feature_arg)
        computed_feature = util.set_conserved_index(computed_feature)
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)
    computed_features = util.reset_groups(computed_features)
    return computed_features
            