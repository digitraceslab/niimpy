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

    assert data.shape[0] >= data.shape[0], "Number of rows should not increase"
    
    # extract featuers
    features = nilo.extract_features_location(data)
    
    assert ((features['n_sps'] > 0) & (features['n_sps'] < 100)).all(), "Number of SPs not reasonable"

    features_u1 = features[features['user'] == 'gps_u00']
    assert features_u1['n_sps'][0] == 22.0
    assert features_u1['n_static'][0] == 4095.0
    assert features_u1['n_moving'][0] == 152.0
    assert features_u1['n_rare'][0] == 114.0
    assert features_u1['n_home'][0] == 2147.0
    assert np.abs(features_u1['max_dist_home'][0] - 1041741.829247) < 0.1
    assert features_u1['n_transitions'][0] == 370.0
    assert features_u1['n_top1'][0] == 2155.0
    assert features_u1['n_top2'][0] == 1291.0
    assert features_u1['n_top3'][0] == 174.0
    assert features_u1['n_top4'][0] == 114.0
    assert features_u1['n_top5'][0] == 65.0
    assert np.abs(features_u1['entropy'][0] - 7.193024) < 0.1
    assert np.abs(features_u1['normalized_entropy'][0] - 2.327054) < 0.1
    assert np.abs(features_u1['dist_total'][0] - 9806714.819275) < 0.1
    assert features_u1['n_bins'][0] == 4247.0
    assert np.abs(features_u1['speed_average'][0] - 0.289073) < 0.1
    assert np.abs(features_u1['speed_variance'][0] - 6.34365) < 0.1
    assert np.abs(features_u1['speed_max'][0] - 34.0) < 0.1
    assert np.abs(features_u1['variance'][0] - 3.865936) < 0.1
    assert np.abs(features_u1['log_variance'][0] - 1.352204) < 0.1
