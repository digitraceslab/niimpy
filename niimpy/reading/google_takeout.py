import pandas as pd
from zipfile import ZipFile
import json
import os
import datetime
from niimpy.preprocessing import util



def format_inferred_activity(data, inferred_activity, activity_threshold):
    # Format the activity type column into activity type and
    # activity inference confidence. The data is nested a few
    # layers deep, so we first need to flatten it.
    row_index = ~data["activity"].isna()
    activities = data.loc[row_index, "activity"]
    activities = activities.str[0].str["activity"]

    if inferred_activity == "highest":
        # Get the first in the list of activity types
        activity_type = activities.str[0].str["type"]
        activity_confidence = activities.str[0].str["confidence"]
        data.loc[row_index, "activity_type"] = activity_type
        data.loc[row_index, "activity_inference_confidence"] = activity_confidence
    
    elif inferred_activity == "all" or inferred_activity == "threshold":
        # Explode the list of activity types into multiple rows
        # and get the new index
        data.loc[row_index, "activity"] = activities
        data = data.explode("activity")
        row_index = ~data["activity"].isna()
        activities = data.loc[row_index, "activity"]
        
        # Extract type and confidence into columns
        activity_type = activities.str["type"]
        activity_confidence = activities.str["confidence"]
        data.loc[row_index, "activity_type"] = activity_type
        data.loc[row_index, "activity_inference_confidence"] = activity_confidence

    if inferred_activity == "threshold":
        # remove rows with no activity type
        data.dropna(subset=["activity_type"], inplace=True)
        # remove rows with confidence below the threshold
        rows = data["activity_inference_confidence"] < activity_threshold
        data = data.loc[~rows, :]
    
    # Drop the original activity column
    data.drop(["activity"], axis=1, inplace=True)
    return data




def location_history(
        zip_filename,
        inferred_activity="highest",
        activity_threshold=0,
        drop_columns=True
    ):
    """  Read the location history from a google takeout zip file.

    The returned dataframe contains the expected latitude, longitude,
    altitude, velocity, heading, accuracy and verticalAccuracy. 
    Additionally, it contains
    an inferred location (latitude and longitude) and a placeId.
    the returned dataframe contains an inferred activity type
    and confidence in the inference. 
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.

    keep_activity : str, optional
        How to choose the inferred activity type to keep.
        - "highest": Only one activity with the highest confidence value 
          is kept. This is the default.
        - "all": All activity types with non-zero confidence values are
          kept as separate rows. Also keeps rows with no activity type.
        - "threshold": Set an confidence threshold for keeping an 
          inferred activity type. Measurements with no activity type are dropped.
    
    activity_threshold: int, optional
        Used when keep_activity is "threshold". The threshold for 
        keeping an inferred activity type.

    drop_columns: bool, optional
        Whether all raw data columns should be kept. This includes lists of
        wifi check points and mostly null device and OS data.

    Returns
    -------

    data : pandas.DataFrame
    """
    
    column_name_map = {'deviceTag': "device"}
    drop_columns = ['deviceDesignation', 'activeWifiScan.accessPoints', 'locationMetadata', 'osLevel']


    # Read json data from the zip file and convert to pandas DataFrame.
    zip_file = ZipFile(zip_filename)
    json_data  = zip_file.read("Takeout/Location History/Records.json")
    json_data = json.loads(json_data)
    data = pd.json_normalize(json_data["locations"])
    data = pd.DataFrame(data)

    # Convert timestamp to datetime
    data["timestamp"] = pd.to_datetime(data["timestamp"], format='ISO8601')

    # Format latitude and longitude as floating point numbers
    data["latitude"] = data["latitudeE7"] / 10000000
    data["longitude"] = data["longitudeE7"] / 10000000
    data.drop(["latitudeE7", "longitudeE7"], axis=1, inplace=True)

    # Extract inferred location and convert
    if "inferredLocation" in data.columns:
        row_index = ~data["inferredLocation"].isna()
        inferred_location = data.loc[row_index, "inferredLocation"].str[0]
        data.loc[row_index, "inferred_latitude"] = inferred_location.str["latitudeE7"] / 10000000
        data.loc[row_index, "inferred_longitude"] = inferred_location.str["longitudeE7"] / 10000000
        data.drop("inferredLocation", axis=1, inplace=True)

    
    if "activity" in data.columns:
        data = format_inferred_activity(data, inferred_activity, activity_threshold)
    
    data.set_index("timestamp", inplace=True)
    data.drop(drop_columns, axis=1, inplace=True,  errors='ignore')
    data.rename(columns=column_name_map, inplace=True)
    util.format_column_names(data)
    return data


def activity(zip_filename):
    """ Read activity data from a Google Takeout zip file. 
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.


    Returns
    -------

    data : pandas.DataFrame
    """

    # Read the csv files in the activity directory and concatenate
    dfs = []
    with ZipFile(zip_filename) as zip_file:
        for filename in zip_file.namelist():
            # Skip the file with daily agregated data for now.
            if filename.endswith('Daily activity metrics.csv'):
                continue

            # Read the more finegrained data for each date
            if filename.startswith("Takeout/Fit/Daily activity metrics/") and filename.endswith(".csv"):
                with zip_file.open(filename) as csv_file:
                    data = pd.read_csv(csv_file)
                    date = os.path.basename(filename).replace(".csv", "")
                    data["date"] = date
                    dfs.append(data)

    data = pd.concat(dfs)

    # Format start time and end time columns with date. Set start time as the
    # timestamp
    data["start_time"] = pd.to_datetime(data["date"] + ' ' + data["Start time"])
    data["end_time"] = pd.to_datetime(data["date"] + ' ' + data["End time"])
    data["timestamp"] = data["start_time"]
    data.set_index('timestamp', inplace=True)
    data.drop(["Start time", "End time", "date"], axis=1, inplace=True)

    # Fix date where end time is midnight
    row_index = data["end_time"].dt.time == datetime.time(0)
    data.loc[row_index, "end_time"] = data.loc[row_index, "end_time"] + datetime.timedelta(days=1)

    # Format durations as timedelta
    for col in data.columns:
        if col.endswith("duration (ms)"):
            new_name = col.replace(" (ms)", "")
            data[new_name] = pd.to_timedelta(data[col], unit="microseconds")
            data.drop(col, axis=1, inplace=True)

    # Format column names
    util.format_column_names(data)
    
    return data