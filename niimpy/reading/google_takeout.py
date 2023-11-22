import pandas as pd
from zipfile import ZipFile
import json

from niimpy.preprocessing import util


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
    
    column_name_map = {
        'deviceTag': "device",
        'platformType': "platform_type",
        'formFactor': "form_factor",
        'serverTimestamp': "server_timestamp",
        'deviceTimestamp': "device_timestamp",
        'batteryCharging': "battery_charging",
        'placeId': "place_id"
    }
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
    row_index = ~data["inferredLocation"].isna()
    inferred_location = data.loc[row_index, "inferredLocation"].str[0]
    data.loc[row_index, "inferred_latitude"] = inferred_location.str["latitudeE7"] / 10000000
    data.loc[row_index, "inferred_longitude"] = inferred_location.str["longitudeE7"] / 10000000
    data.drop("inferredLocation", axis=1, inplace=True)

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

    data.set_index("timestamp", inplace=True)
    data.drop(drop_columns, axis=1, inplace=True)
    data.rename(columns=column_name_map, inplace=True)
    return data

