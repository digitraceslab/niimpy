import pandas as pd

ALL_FEATURE_FUNCTIONS = [key for key in globals().keys() if key.startswith('audio_')]
ALL_FEATURE_FUNCTIONS = {x: {} for x in features}

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
        features = ALL_FEATURE_FUNCTIONS
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        print(f'computing {feature}...')
        command = f'{feature}(df,feature_functions=feature_arg)'
        computed_feature = eval(command)
        computed_features.append(computed_feature)
        
    computed_features = pd.concat(computed_features, axis=1)
    return computed_features
            
def audio_count_silent(df_u, feature_functions=None): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound in the environment. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "is_silent"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    df_u[col_name] = pd.to_numeric(df_u[col_name])
        
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).sum()
        result = result.to_frame(name='audio_count_silent')
    return result

def audio_count_speech(df_u, feature_functions=None): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound between 65Hz and 255Hz in the environment that could
    be specified as speech. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "is_silent"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "audio_freq_name" in feature_functions:
        freq_name = "double_frequency"
    else:
        freq_name = feature_functions["audio_freq_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df_u[col_name] = pd.to_numeric(df_u[col_name])
    
    if len(df_u)>0:
        df_s = df_u[df_u[freq_name].between(65, 255)]
        df_s = df_s[df_s[col_name]==0] #check if there was a conversation. 0 is not silent, 1 is silent
        df_s.loc[:,col_name] = 1
        result = df_s.groupby('user')[col_name].resample(**feature_functions["resample_args"]).sum()
        result = result.to_frame(name='audio_count_speech')
    return result

def audio_count_loud(df_u, feature_functions=None): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound louder than 70dB in the environment. If there 
    is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_decibels"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df_u[col_name] = pd.to_numeric(df_u[col_name])
    
    if len(df_u)>0:
        df_s = df_u[df_u[col_name]>70] #check if environment was noisy
        result = df_s.groupby('user')[col_name].resample(**feature_functions["resample_args"]).count()
        result = result.to_frame(name='audio_count_loud')
    return result

def audio_min_freq(df_u, feature_functions=None): 
    """ This function returns the minimum frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_frequency"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).min()
        result = result.to_frame(name='audio_min_freq')
    return result

def audio_max_freq(df_u, feature_functions=None): 
    """ This function returns the maximum frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_frequency"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).max()
        result = result.to_frame(name='audio_max_freq')
    return result

def audio_mean_freq(df_u, feature_functions=None): 
    """ This function returns the mean frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_frequency"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).mean()
        result = result.to_frame(name='audio_mean_freq')
    return result

def audio_median_freq(df_u, feature_functions=None):
    """ This function returns the median frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_frequency"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).median()
        result = result.to_frame(name='audio_median_freq')
    return result

def audio_std_freq(df_u, feature_functions=None): 
    """ This function returns the standard deviation of the frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_frequency"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).std()
        result = result.to_frame(name='audio_std_freq')
    return result

def audio_min_db(df_u, feature_functions=None): 
    """ This function returns the minimum decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_decibels"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).min()
        result = result.to_frame(name='audio_min_db')
    return result

def audio_max_db(df_u, feature_functions=None): 
    """ This function returns the maximum decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_decibels"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).max()
        result = result.to_frame(name='audio_max_db')
    return result

def audio_mean_db(df_u, feature_functions=None): 
    """ This function returns the mean decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_decibels"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).mean()
        result = result.to_frame(name='audio_mean_db')
    return result

def audio_median_db(df_u, feature_functions=None): 
    """ This function returns the median decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_decibels"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).median()
        result = result.to_frame(name='audio_median_db')
    return result

def audio_std_db(df_u, feature_functions=None): 
    """ This function returns the standard deviation of the decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "audio_column_name" in feature_functions:
        col_name = "double_decibels"
    else:
        col_name = feature_functions["audio_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    if len(df_u)>0:
        result = df_u.groupby('user')[col_name].resample(**feature_functions["resample_args"]).std()
        result = result.to_frame(name='audio_std_db')
    return result