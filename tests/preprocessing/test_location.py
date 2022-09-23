import os

import numpy as np
import pandas as pd

from geopy.distance import distance

import niimpy
import niimpy.preprocessing.location as nilo
from niimpy import config

# read sample data
data = niimpy.read_csv(config.GPS_PATH, tz='et')

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
    
    # bin data
    binned_data = niimpy.util.aggregate(data, freq="10T", method_numerical="median"). \
        reset_index(0). \
        dropna()
    
    assert data.shape[0] >= binned_data.shape[0], "Number of rows should not increase"
    
    # extract featuers
    features = nilo.extract_features_location(binned_data)
    
    assert ((features['n_sps'] > 0) & (features['n_sps'] < 100)).all(), "Number of SPs not reasonable"
    
    features_u1 = features.loc['gps_u00']
    assert features_u1['n_sps'] == 19.0
    assert features_u1['n_static'] == 4080.0
    assert features_u1['n_moving'] == 151.0
    assert features_u1['n_rare'] == 171.0
    assert features_u1['n_home'] == 2148.0
    assert np.abs(features_u1['max_dist_home'] - 6392724.065) < 0.1
    assert features_u1['n_transitions'] == 354.0
    assert features_u1['n_top1'] == 2170.0
    assert features_u1['n_top2'] == 1207.0
    assert features_u1['n_top3'] == 171.0
    assert features_u1['n_top4'] == 165.0
    assert features_u1['n_top5'] == 63.0
    assert np.abs(features_u1['entropy'] - 7.238) < 0.1
    assert np.abs(features_u1['normalized_entropy'] - 2.458) < 0.1
    assert np.abs(features_u1['dist_total'] - 18633281.869) < 0.1
    assert features_u1['n_bins'] == 4231.0
    assert np.abs(features_u1['speed_average'] - 0.287) < 0.1
    assert np.abs(features_u1['speed_variance'] - 6.311) < 0.1
    assert np.abs(features_u1['speed_max'] - 34.0) < 0.1
    assert np.abs(features_u1['variance'] - 183.829) < 0.1
    assert np.abs(features_u1['log_variance'] - 5.214) < 0.1