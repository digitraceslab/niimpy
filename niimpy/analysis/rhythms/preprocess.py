import pandas as pd
import niimpy 
import niimpy.preprocessing.communication as comm
import niimpy.preprocessing.battery as batt
import niimpy.preprocessing.screen as screen
import plotly
from config import PATHS
import matplotlib.pyplot as plt
import sys
import datetime


import hydra
from omegaconf import DictConfig, OmegaConf

def load_data(path: str, table: str) -> pd.DataFrame:
    data = niimpy.read_sqlite(path, table=table, tz='Europe/Helsinki')
    return data

def convert_cols_dtypes(data: pd.DataFrame, cols: list) -> pd.DataFrame:

    data[cols] = data[cols].astype(float)

    return data

def align_data(data: pd.DataFrame, hours_slice: int, freq: str):
    
    results = []
    for user in data['user'].unique():
        user_data = data[data['user'] == user].copy()
        user_data.sort_index(inplace=True)
        
        start_time = user_data.index[0]
        
        # Find the first index that starts with hour 0
        for i in user_data.index:
            if i.hour == 0:
                start_time = i
                break
        
        end_time = start_time + datetime.timedelta(hours=hours_slice)
        # Skip users if data does not span over max hours_slice
        if end_time > user_data.index.max():
            continue
            
        
        filtered_data = user_data[(user_data.index >= start_time)&(user_data.index < end_time)].copy()
                    
        results.append(filtered_data)

    results = pd.concat(results)
    return results
    
def extract_feature(data: pd.DataFrame, feature: str, time_window: str, 
                    optional_data: pd.DataFrame = None, 
                    freeday: bool = None) -> pd.DataFrame:
    '''
    Extract total call count per time_window
    '''
    
    if feature == 'comm':
        wrapper_features1 = {comm.call_count:{"communication_column_name":"call_duration",
                                              "resample_args":{"rule":time_window}},
                            comm.call_duration_total:{"communication_column_name":"call_duration",
                                                      "resample_args":{"rule":time_window}}
                            }
        results = comm.extract_features_comms(data, features=wrapper_features1)
        
        # Reset index and extract date
        results = results.reset_index().rename(columns={'level_1': 'time'}).set_index('time')
        
    elif feature == 'sms':
        
        wrapper_features1 = {comm.sms_count:{"resample_args":{"rule":time_window}}}
        results = comm.extract_features_comms(data, features=wrapper_features1)
        
        # Reset index and extract date
        results = results.reset_index().rename(columns={'level_1': 'time'}).set_index('time')
        
    elif feature == 'screen':
        
        batt_data = optional_data.copy()
        results = screen.extract_features_screen(data, batt_data, 
                                                 features={screen.screen_count:{"screen_column_name":"screen_status",
                                                                                      "resample_args":{"rule":time_window}},
                                                           screen.screen_duration:{"screen_column_name":"screen_status",
                                                                                   "resample_args":{"rule":time_window}}})
        
        # Reset index and extract date
        results = results.reset_index().rename(columns={'level_1': 'time'}).set_index('time')
        
    # Exclude freeday or weekday. If freeday = None, include both
    if freeday == True:

        final_results = results.copy()[results.index.weekday >= 5]
    elif freeday == False:

        final_results = results.copy()[results.index.weekday < 5]
    else:

        final_results = results.copy()
        
    return final_results

def aggregate(data: pd.DataFrame, hours_slice: int, freq: str, log_print=False) -> pd.DataFrame:
    """
    
    """

    agg_data = []
    for user in data['user'].unique():
        user_data = data[data['user'] == user]
        
        if freq == 'daily':
    
            agg_features = user_data.groupby([user_data.index.hour]).sum(numeric_only=True)
        elif freq == 'weekly':
                        
            user_data['hour_dayofweek'] = user_data.index.strftime('%A %H')
            
            agg_features = user_data.groupby(['hour_dayofweek']).sum(numeric_only=True)

            # Rename cols
            agg_features.index.names = ['time']
        else:
            print("ERROR: Cant recognize freq.")
            
        agg_features['user'] = user
        agg_data.append(agg_features)

    agg_data = pd.concat(agg_data)
    
    return agg_data

def compute_daily_rhythm(data: pd.DataFrame, cols=list, agg=False, weekend_separation=False) -> pd.DataFrame:
    """
    Computes the count distribution for each unique value in a specified column.

    Args:
        data (pd.DataFrame): The input dataframe containing the data. Timestamp index.
        cols (list, optional): The name(s) of the column(s) to compute distribution. Defaults to an empty list.

    Returns:
        pd.DataFrame: A dataframe containing the call count distribution for the specified column(s).

    Raises:
        ValueError: If the specified column does not exist in the input dataframe.
    """  
    
    for col in cols:
        
        if col not in data.columns:
            raise ValueError(f"The specified column '{col}' does not exist in the input dataframe.")
        
        sumcol = col + '_daily_sum'
        
        if agg == False:
            data = data.assign(date=data.index.date)
            data[sumcol] = data.groupby(by=['user'])[col].transform('sum')  # stores sum of daily values
        else:
            
            # If data is already aggregated, index should be hour bin (e.g., 0 1 2 3 ... 23)
            data = data.assign(hour=data.index)
            
            data[sumcol] = data.groupby(by=['user'])[col].transform('sum')  # stores sum of daily values
            
        distrcol = col +'_distr'
        data[distrcol] = data[col] / data[sumcol]
    
    return data

def compute_weekly_rhythm(data: pd.DataFrame, agg_freq = None, cols=list) -> pd.DataFrame:
    """
    Computes the count distribution for each unique value in a specified column.

    Args:
        data (pd.DataFrame): The input dataframe containing the data. Timestamp index.
        cols (list, optional): The name(s) of the column(s) to compute distribution. Defaults to an empty list.

    Returns:
        pd.DataFrame: A dataframe containing the call count distribution for the specified column(s).

    Raises:
        ValueError: If the specified column does not exist in the input dataframe.
    """ 
    
    
    for col in cols:
        
        if col not in data.columns:
            raise ValueError(f"The specified column '{col}' does not exist in the input dataframe.")
        
        sumcol = col + '_weekly_sum'
        
        data[sumcol] = data.groupby(by=['user'])[col].transform('sum')  # stores sum of daily values

        distrcol = col +'_distr'
        data[distrcol] = data[col] / data[sumcol]
    
    return data

def compute_rhythms_for_one_group(path: str,
                                  table: str,
                                  feature: str,
                                  group_name: str, 
                                  time_window: str, 
                                  cols: list,
                                  freq: str,
                                  freeday: bool = None) -> pd.DataFrame:
    
    """
    Compute call count distribution rhythms for a single group.

    Parameters:
    -----------
    path: str
        Path to the input data file.
    feature: str
        Name of feature. Possible values: "screen", "comm", "sms".
    group_name: str
        Name of the group to compute call count distribution rhythms for.
    time_window: str
        Time window to group calls by, in pandas frequency string format.
    cols: list
        List of column names to compute the count distribution for.
    freq: str
        Frequency to sample. Can be 'daily' or 'weekly'.
    Returns:
    --------
    pd.DataFrame
        Dataframe containing the computed call count distribution rhythms for the specified group.
    """
    
    # Basic procedures
    data = load_data(path, table)
    data = remove_timezone_info(data)
    
    if feature == "comm":
        data = drop_duplicates_and_sort(data)
        
        data = align_data(data, hours_slice = 8*7*24, freq=freq)
           
        # Extract features
        features = extract_feature(data, feature = feature, time_window = time_window)
        
         # Combine call count
        features['total_call_count'] = features['outgoing_count'] + features['incoming_count']
        features['total_duration'] = features['outgoing_duration_total'] + features['incoming_duration_total']
       
    elif feature == 'sms':
        
        data = align_data(data, hours_slice = 8*7*24, freq=freq)
           
        # Extract features
        features = extract_feature(data, feature = feature, time_window = time_window)
        
        # Combine call
        features['total_count'] = features['outgoing_count'] + features['incoming_count']
        
    elif feature == 'screen':
        
        data = align_data(data, hours_slice = 8*7*24, freq=freq)
           
        # Extract features
        features = extract_feature(data, feature = feature, time_window = time_window)
  
    # Check freq
    if freq == 'daily':
        
        agg_data = aggregate(features, hours_slice = 8*7*24, freq=freq) # 8 weeks * 7 days * 24 hours

        features_distr = compute_daily_rhythm(agg_data, cols=cols, agg=True)
    else:
        
        agg_data = aggregate(features, hours_slice = 8*7*24, freq=freq)

        # Daily distribution
        features_distr = compute_weekly_rhythm(agg_data, cols=cols)

    # Assign group name
    features_distr['group'] = group_name
        
    return features_distr


def compute_rhythms_for_all_groups(paths: list, 
                                   table: str,
                                   feature: str,
                                   time_window: str,
                                   cols: list,
                                   freq: str,
                                   freeday: bool = None) -> pd.DataFrame:
    
    data = pd.DataFrame()
    group_names = ['mmm-bd', 'mmm-bpd', 'mmm-control', 'mmm-mdd']
    
    df = compute_rhythms_for_one_group(path, 
                                           table=table,
                                           feature=feature,
                                           group_name=group_names[i], 
                                           time_window=time_window, 
                                           cols=cols,
                                           freq=freq,
                                           freeday=freeday)
            
        
    data = pd.concat([data, df])
    
    return data

def save_data(df, path, file_format='csv'):
    """
    Save DataFrame to specified format.
    
    Args:
        df (pd.DataFrame): DataFrame to save.
        path (str): Name of the file without extension.
        file_format (str): Format to save the DataFrame as ('csv', 'parquet', 'pickle', 'feather'). Default is 'csv'.
    """
    if file_format.lower() == 'csv':
        df.to_csv(f"{path}")
    elif file_format.lower() == 'parquet':
        df.to_parquet(f"{path}.parquet")
    elif file_format.lower() == 'pickle':
        df.to_pickle(f"{path}.pkl")
    elif file_format.lower() == 'feather':
        df.to_feather(f"{path}.feather")
    else:
        raise ValueError("Invalid file format. Choose from 'csv', 'parquet', 'pickle', or 'feather'.")

@hydra.main(version_base=None, config_path="../../config/preprocess", config_name="config")
def main(cfg : DictConfig) -> None:
    
    print(OmegaConf.to_yaml(cfg.rhythm))
    
    sensor_type = cfg.rhythm.sensor
    freq = cfg.rhythm.freq
    time_window = cfg.rhythm.time_window
    output_path = cfg.rhythm.output
    freeday = cfg.rhythm.freeday
    
    if sensor_type == 'comm':
        paths = [PATHS['mmm-bd']['awarecalls'], PATHS['mmm-bpd']['awarecalls'],
                 PATHS['mmm-control']['awarecalls'], PATHS['mmm-mdd']['awarecalls']]
        batt_paths = [PATHS['mmm-bd']['awarebattery'], PATHS['mmm-bpd']['awarebattery'],
                      PATHS['mmm-control']['awarebattery'], PATHS['mmm-mdd']['awarebattery']]
        
        data = compute_rhythms_for_all_groups(paths,
                                              table = "AwareCalls",
                                              feature = "comm",
                                              time_window = time_window, 
                                              cols = ['outgoing_count', 'incoming_count', 'total_call_count',
                                                     'outgoing_duration_total', 'incoming_duration_total', 'total_duration' ],
                                              freq=freq,
                                              optional_paths = batt_paths,
                                              optional_table = "AwareBattery",
                                              freeday = freeday)

    elif sensor_type == 'sms':
        paths = [PATHS['mmm-bd']['awaresms'], PATHS['mmm-bpd']['awaresms'],
                 PATHS['mmm-control']['awaresms'], PATHS['mmm-mdd']['awaresms']]
        batt_paths = [PATHS['mmm-bd']['awarebattery'], PATHS['mmm-bpd']['awarebattery'],
                      PATHS['mmm-control']['awarebattery'], PATHS['mmm-mdd']['awarebattery']]
        
        data = compute_rhythms_for_all_groups(paths,
                                              table = "AwareMessages",
                                              feature = "sms",
                                              time_window = time_window, 
                                              cols = ['outgoing_count', 'incoming_count', 'total_count'],
                                              freq=freq,
                                              optional_paths = batt_paths,
                                              optional_table = "AwareBattery",
                                              freeday = freeday)
        
    elif sensor_type == 'screen':

        screen_paths = [PATHS['mmm-bd']['awarescreen'], PATHS['mmm-bpd']['awarescreen'],
                        PATHS['mmm-control']['awarescreen'], PATHS['mmm-mdd']['awarescreen']]
        batt_paths = [PATHS['mmm-bd']['awarebattery'], PATHS['mmm-bpd']['awarebattery'],
                      PATHS['mmm-control']['awarebattery'], PATHS['mmm-mdd']['awarebattery']]
        
        data = compute_rhythms_for_all_groups(screen_paths,
                                              table = "AwareScreen",
                                              feature = "screen",
                                              time_window = time_window, 
                                              cols = ['screen_on_count', 'screen_off_count', 'screen_use_count',
                                                     'screen_on_durationtotal', 'screen_off_durationtotal',
                                                      'screen_use_durationtotal'],
                                              freq=freq,
                                              optional_paths = batt_paths,
                                              optional_table = "AwareBattery",
      
    else:
        print("Invalid value for 'type'.")
        
    save_data(data, output_path)
    
if __name__ == "__main__":
    main()