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
    
    sps = features['n_sps'].dropna()
    assert ((sps > 0) & (sps < 100)).all(), "Number of SPs not reasonable"

    features_u1 = features[features['user'] == 'gps_u00']
    features_u1 = features_u1.dropna().iloc[1]
    assert features_u1['n_significant_places'] == 4.0
    assert features_u1['n_sps'] == 2.0
    assert features_u1['n_static'] == 309.0
    assert features_u1['n_moving'] == 18.0
    assert features_u1['n_rare'] == 0.0
    assert features_u1['n_home'] == 261.0
    assert np.abs(features_u1['max_dist_home'] - 697.447877) < 0.1
    assert features_u1['n_transitions'] == 8.0
    assert features_u1['n_top1'] == 287.0
    assert features_u1['n_top2'] == 22.0
    assert features_u1['n_top3'] == 0.0
    assert features_u1['n_top4'] == 0.0
    assert features_u1['n_top5'] == 0.0
    assert np.abs(features_u1['entropy'] - 3.091042) < 0.1
    assert np.abs(features_u1['normalized_entropy'] - 4.459432) < 0.1
    assert np.abs(features_u1['dist_total'] - 9806714.819275) < 0.1
    assert features_u1['n_bins'] == 4247.0
    assert np.abs(features_u1['speed_average'] - 0.289073) < 0.1
    assert np.abs(features_u1['speed_variance'] - 6.34365) < 0.1
    assert np.abs(features_u1['speed_max'] - 34.0) < 0.1
    assert np.abs(features_u1['variance'] - 3.865936) < 0.1
    assert np.abs(features_u1['log_variance'] - 1.352204) < 0.1
