import pandas as pd
from zipfile import ZipFile
import json

from niimpy.preprocessing import util


def location_history(
        zip_filename,
        inferred_activity="highest",
    ):
    """  Read the location history from a google takeout zip file.
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.
    keep_activity : str, optional
        How to choose the inferred activity type to keep. If "highest",
        only one activity with the highest confidence value is kept.
        If "all", all activity types with non-zero confidence values are
        kept as separate rows.
        IF an integer is provided, it is used as a threshold for the confidence.
        If "none" or any other value, no activity is kept.

    
    Returns
    -------

    data : pandas.DataFrame
    """
    
    column_map = {

    }

    # Read json data from the zip file and convert to pandas DataFrame.
    zip_file = ZipFile(zip_filename)
    json_data  = zip_file.read("Takeout/Location History/Records.json")
    json_data = json.loads(json_data)
    data = pd.json_normalize(json_data["locations"])
    data = pd.DataFrame(data)

    # Format latitude and longitude as floating point numbers
    data["latitude"] = data["latitudeE7"] / 10000000
    data["longitude"] = data["longitudeE7"] / 10000000
    data.drop(["latitudeE7", "longitudeE7"], axis=1, inplace=True)

    # Convert timestamp to datetime
    data["timestamp"] = pd.to_datetime(data["timestamp"], format='ISO8601')

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
    
    elif inferred_activity == "all" or type(inferred_activity) == int:
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

    if type(inferred_activity) == int:
        # remove rows with confidence below the threshold
        rows = data["activity_inference_confidence"] < inferred_activity
        data = data.loc[~rows, :]
        

    data.set_index("timestamp", inplace=True)
    data.drop(["activity"], axis=1, inplace=True)
    return data

