import pandas as pd

import niimpy
from niimpy import config


def test_read_google_takeout_location():
    """test reading location data form a Google takeout file."""
    data = niimpy.reading.google_takeout.location_history(config.GOOGLE_TAKEOUT_PATH)
    
    assert data['latitude'][0] == 35.9974880
    assert data['longitude'][0] == -78.9221943
    assert data['source'][0] == "WIFI"
    assert data['accuracy'][0] == 25
    assert data['device'][0] == -577680260
    assert data.index[0] == pd.to_datetime("2016-08-12T19:29:43.821Z")
    
    assert len(data[data["source"] == "GPS"]) == 2

    assert data['activity_type'][1] == "STILL"
    assert data['activity_inference_confidence'][1] == 62
