import collections

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

from geopy.distance import geodesic


def distance_matrix(lats, lons):
    """Compute distance matrix using great-circle distance formula

    https://en.wikipedia.org/wiki/Great-circle_distance#Formulae

    Parameters
    ----------
    lats : array
        Latitudes

    lons : array
        Longitudes

    Returns
    -------
    dists : matrix
        Entry `(i, j)` shows the great-circle distance between
        point `i` and `j`, i.e. distance between `(lats[i], lons[i])`
        and `(lats[j], lons[j])`.
    """
    R = 6372795.477598

    lats = np.array(lats)
    lons = np.array(lons)

    assert len(lats) == len(lons), "lats and lons should be of the same size"
    assert not any(np.isnan(lats)), "nan in lats"
    assert not any(np.isnan(lons)), "nan in lons"

    # convert degree to radian
    lats = lats * np.pi / 180.0
    lons = lons * np.pi / 180.0

    sins = np.sin(lats)
    sin_matrix = sins.reshape(-1, 1) @ sins.reshape(1, -1)

    coss = np.cos(lats)
    cos_matrix = coss.reshape(-1, 1) @ coss.reshape(1, -1)

    lons_matrix = lons * np.ones((len(lons), len(lons)))
    lons_diff = lons_matrix - lons_matrix.T
    lons_diff = np.cos(lons_diff)

    # TODO: make this function more efficient
    dists = R * np.arccos(sin_matrix + cos_matrix * lons_diff)
    dists[np.isnan(dists)] = 0
    return dists


def filter_location(location,
                    remove_disabled=True,
                    remove_zeros=True,
                    remove_network=True):
    """Remove low-quality or weird location samples

    Parameters
    ----------

    location : pd.DataFrame
        DataFrame of locations

    remove_disabled : bool
        Remove locations whose `label` is disabled

    remove_zerso : bool
        Remove locations which their latitude and longitueds are close to 0

    remove_network : bool
        Keep only locations whose `provider` is `gps`

    Returns
    -------
    location : pd.DataFrame
    """

    if remove_disabled:
        assert 'label' in location
        location = location[location['label'] != 'disabled']

    if remove_zeros:
        index = (location["double_latitude"] ** 2 +
                 location["double_longitude"] ** 2) > 0.001
        location = location[index]

    if remove_network:
        assert 'provider' in location
        location = location[location['provider'] == 'gps']

    return location


def bin_location(location,
                 bin_width=10,
                 aggregation='median',
                 columns_to_aggregate=None):
    """Downsample location data and aggregate points in bins

    Parameters
    ----------

    location : pd.DataFrame
        DataFrame of locations. Index should be timestamp of samples.
        `user` has to exist in columns.

    bin_width : int
        Length of bin in minutes. Default is 10 minutes.

    aggregation : str
        Specifies how datapoints in a bin should be aggregated. Options:
        'median', 'mean'.

    columns_to_aggregate : list of str
        Specifies which columns to aggregate according to `aggregation`
        parameter. For other columns, the first value is picked for the
        aggregated bin.

    Returns
    -------
    location : pd.DataFrame
        Binned location. This dataframe is indexed by rounded times.
    """
    if columns_to_aggregate is None:
        columns_to_aggregate = ['double_latitude', 'double_longitude']

    freq = '{}T'.format(bin_width)
    location['time'] = location.index
    location['time'] = location['time'].apply(
        lambda x: x.floor(freq=freq, ambiguous=False)
    )

    original_columns = location.columns
    columns_others = location.columns.drop(columns_to_aggregate)
    columns_to_aggregate.extend(['user', 'time'])

    location_to_aggregate = location[columns_to_aggregate]
    location_others = location[columns_others]

    grouped = location_to_aggregate.groupby(['user', 'time'])
    if aggregation == 'median':
        location_to_aggregate = grouped.median()
    elif aggregation == 'mean':
        location_to_aggregate = grouped.mean()
    location_to_aggregate = location_to_aggregate. \
        reset_index(level=[0, 1]). \
        set_index('time')

    location_others = location_others. \
        groupby(['user', 'time']). \
        first(). \
        reset_index(level=[0, 1]). \
        set_index('time'). \
        drop('user', axis=1)

    location = pd.concat([location_to_aggregate, location_others], axis=1)
    location = location[original_columns.drop('time')]
    return location


def extract_distance_features(location, bin_width=10.0,
                              speed_threshold=0.277, column_prefix=None):
    """Calculates features realted distance and speed

    Parameters
    ----------
    location : pd.DataFrame
        Dataframe of locations indexed by time. These columns have to exist
        in the dataframe: `user`, `double_latitude`, `double_longitude`.

    bin_width : float
        Lenght of bins in minutes

    speed_threshold : float
        Bins whose speed is lower than `speed_threshold` are considred
        `static` and the rest are `moving`.

    column_prefix : str
        Add a prefix to all column names.

    Returns
    -------
    features : pd.DataFrame
        Dataframe of computed features where the index is users and columns
        are the the features. Featerus
            - `dist_total`: total distance traveled
            - `n_bins`: number of bins with which other features are calculated
            - `speed_average`: average speed
            - `speed_variance`: variance in speed
    """
    def compute_distance_features(df):
        """Compute features for a single user"""
        df = df.sort_index()  # sort based on time
        n_bins = df.shape[0]

        lats = df['double_latitude']
        lons = df['double_longitude']

        dists = np.zeros(n_bins)
        time_deltas = np.zeros(n_bins)

        for i in range(1, n_bins):
            loc1 = (lats[i - 1], lons[i - 1])
            loc2 = (lats[i], lons[i])

            time_deltas[i] = (df.index[i] - df.index[i - 1]).total_seconds()
            dists[i] = geodesic(loc1, loc2).meters

        speeds = dists / time_deltas
        speeds[0] = 0
        speed_average = np.nanmean(speeds)
        speed_variance = np.nanvar(speeds)
        speed_max = np.nanmax(speeds)
        total_dist = sum(dists)

        static_bins = speeds < speed_threshold
        lats_static = lats[static_bins]
        lons_static = lons[static_bins]
        dists_matrix = distance_matrix(lats_static, lons_static)

        dbscan = DBSCAN(min_samples=5, eps=20, metric='precomputed')
        clusters = dbscan.fit_predict(dists_matrix)
        non_rare_clusters = clusters[clusters != -1]
        n_unique_sps = len(set(non_rare_clusters))

        counter = collections.Counter(clusters)
        stay_times = counter.values()
        stay_times = np.sort(list(stay_times))[::-1]

        time_static = bin_width * sum(static_bins)
        time_moving = bin_width * sum(~static_bins)
        time_rare = bin_width * counter[-1]

        n_transitions = sum(np.diff(clusters) != 0)

        stay_top1 = stay_times[0] * bin_width if len(stay_times) > 0 else 0
        stay_top2 = stay_times[1] * bin_width if len(stay_times) > 1 else 0
        stay_top3 = stay_times[2] * bin_width if len(stay_times) > 2 else 0
        stay_top4 = stay_times[3] * bin_width if len(stay_times) > 3 else 0
        stay_top5 = stay_times[4] * bin_width if len(stay_times) > 4 else 0

        row = pd.DataFrame({
            'dist_total': [total_dist],
            'n_bins': [n_bins],
            'speed_average': [speed_average],
            'speed_variance': [speed_variance],
            'speed_max': [speed_max],
            'n_sps': [n_unique_sps],
            'time_static': [time_static],
            'time_moving': [time_moving],
            'time_rare': [time_rare],
            'n_transitions': [n_transitions],
            'stay_top1': [stay_top1],
            'stay_top2': [stay_top2],
            'stay_top3': [stay_top3],
            'stay_top4': [stay_top4],
            'stay_top5': [stay_top5],
        })
        return row

    location = location.sort_index()

    features = pd.DataFrame(index=location.user.unique())
    grouped = location.groupby('user')
    var = grouped.var()

    features = grouped.apply(compute_distance_features)
    features = features.reset_index(level=[1], drop=True)
    features['variance'] = var['double_latitude'] + var['double_longitude']
    features['log_variance'] = np.log(features['variance'])

    if column_prefix:
        new_columns = [
            '{}_{}'.format(column_prefix, col) for col in features.columns
        ]
        features.columns = new_columns

    if 'group' in location:
        features['group'] = location.groupby('user')['group'].first()

    return features
