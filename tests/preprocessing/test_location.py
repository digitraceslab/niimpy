import numpy as np

from geopy.distance import distance

import niimpy
import niimpy.preprocessing.location as nilo
from niimpy import config

# read sample data
data = niimpy.read_csv(config.GPS_PATH, tz='et')
data = data.rename(columns={"double_latitude": "latitude", "double_longitude": "longitude", "double_speed": "speed"})
data["group"] = "group1"

def test_distance_matrix():
    
    lats = [60.186914007399274, 60.167290738174195, 61.49603247041282]
    lons = [24.82159342608858, 24.941127948645796, 23.75945568751852]
    
    true_dist_matrix = np.zeros((len(lats), len(lats)))
    for i in range(len(lats)):
        for j in range(len(lats)):
            dist = distance((lats[i], lons[i]), (lats[j], lons[j])).meters
            true_dist_matrix[i, j] = dist
    computed_dist_matrix = nilo.distance_matrix(lats, lons)

    non_diag_mask = 1 - np.eye(len(lats))
    non_diag_mask = non_diag_mask.astype(bool)
    absolute_error = np.abs(computed_dist_matrix - true_dist_matrix)
    error_percentage = absolute_error[non_diag_mask] / true_dist_matrix[non_diag_mask]
    
    assert (error_percentage < 0.01).all() # error percentage must be below 1%
    

def test_location_features():
    # extract featuers
    data["extra_column"] = "extra"
    features = nilo.extract_features_location(data)
    assert "extra_column" not in features.columns
    
    sps = features['n_sps'].dropna()
    print(sps)
    assert ((sps > 0) & (sps < 100)).all(), "Number of SPs not reasonable"

    features_u1 = features[features["user"] == 'gps_u00']
    features_u1 = features_u1.dropna().iloc[1]

    assert features_u1['n_sps'] == 11.0
    assert features_u1['n_static'] == 1993.0
    assert features_u1['n_moving'] == 66.0
    assert features_u1['n_rare'] == 41.0
    assert features_u1['n_home'] == 1018.0
    assert np.abs(features_u1['max_dist_home'] - 291478.946696) < 0.1
    assert features_u1['n_transitions'] == 199.0
    assert features_u1['n_top1'] == 1024.0
    assert features_u1['n_top2'] == 673.0
    assert features_u1['n_top3'] == 146.0
    assert features_u1['n_top4'] == 41.0
    assert features_u1['n_top5'] == 38.0
    assert np.abs(features_u1['entropy'] - 7.257854) < 0.1
    assert np.abs(features_u1['normalized_entropy'] - 3.02676) < 0.1
    assert np.abs(features_u1['dist_total'] - 2223338.397681) < 0.1
    assert features_u1['n_bins'] == 2059.0
    assert np.abs(features_u1['speed_average'] - 0.266393) < 0.1
    assert np.abs(features_u1['speed_variance'] - 6.049846) < 0.1
    assert np.abs(features_u1['speed_max'] - 33.25) < 0.1
    assert np.abs(features_u1['variance'] - 0.237454) < 0.1
    assert np.abs(features_u1['log_variance'] - -1.437781) < 0.1
    assert features_u1['group'] == "group1"


