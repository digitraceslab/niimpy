import collections

import pandas as pd
import numpy as np
import scipy.stats
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
        aggregated bin. Default is ['double_latitude', 'double_longitude']

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


def get_speeds_totaldist(lats, lons, times):
    """Computes speed of bins with dividing distance by their time difference

    Parameters
    ----------
    lats : array-like
        Array of latitudes
    lons : array-like
        Array of longitudes
    times : array-like
        Array of times associted with bins

    Returns
    ------
    (speeds, total_distances) : tuple of speeds (array) and total distance travled (float)
    """
    assert len(lats) == len(lons) == len(times)
    n_bins = len(lats)

    dists = np.zeros(n_bins)
    time_deltas = np.zeros(n_bins)
    for i in range(1, n_bins):
        loc1 = (lats[i - 1], lons[i - 1])
        loc2 = (lats[i], lons[i])

        time_deltas[i] = (times[i] - times[i - 1]).total_seconds()
        dists[i] = geodesic(loc1, loc2).meters
    speeds = dists / time_deltas
    speeds[0] = 0
    return speeds, sum(dists)


def find_home(lats, lons, times):
    """Find coordinates of the home of a person

    Home is defined as the place most visited between
    12am - 6am. Locations within this time period first
    clustered and then the center of largest clusetr
    shows the home.

    Parameters
    ----------
    lats : array-like
        Latitudes
    lons : array-like
        Longitudes
    times : array-like
        Time of the recorderd coordinates

    Returns
    ------
    (lat_home, lon_home) : tuple of floats
        Coordinates of the home
    """
    idx_night = [True if t.hour <= 6 else False for t in times]
    if sum(idx_night) == 0:
        return np.nan, np.nan

    lats_night = lats[idx_night]
    lons_night = lons[idx_night]
    clusters = cluster_locations(lats_night, lons_night)
    counter = collections.Counter(clusters)
    home_cluster = counter.most_common()[0][0]

    lats_home = lats_night[clusters == home_cluster]
    lons_home = lons_night[clusters == home_cluster]

    lat_home = np.mean(lats_home)
    lon_home = np.mean(lons_home)

    return lat_home, lon_home


def cluster_locations(lats, lons, min_samples=5, eps=200):
    """Performs clustering on the locations

    Parameters
    ----------
    lats : pd.DataFrame
        Latitudes
    lons : pd.DataFrame
        Longitudes
    mins_samples : int
        Minimum number of samples to form a cluster. Default is 5.
    eps : float
        Epsilone parameter in DBSCAN. The maximum distance between
        two neighbour samples. Default is 200.

    Returns
    -------
    clusters : array
        Array of clusters. -1 indicates outlier.
    """
    dists_matrix = distance_matrix(lats, lons)
    dbscan = DBSCAN(min_samples=min_samples, eps=eps, metric='precomputed')
    clusters = dbscan.fit_predict(dists_matrix)
    return clusters


def number_of_significant_places(lats, lons, times):
    """Computes number of significant places

    Number of significant plcaes is computed by first clustering
    the locations in each month and then taking the median of the
    number of clusters in each month.

    It is assumed that `lats` and `lons` are the coordinates of
    static points.

    Parameters
    ----------
    lats : pd.DataFrame
        Latitudes
    lons : pd.DataFrame
        Longitudes
    times : array
        Array of times

    Returns
    """
    sps = []
    numper_of_places = []
    months = pd.date_range(min(times), max(times), freq='M')
    months = list(months)
    if len(months) == 0:
        return np.nan
    last_month = months[-1] + pd.Timedelta(weeks=4)
    months += [last_month]
    for i in range(len(months) - 1):
        start = months[i]
        end = months[i + 1]
        idx = (times >= start) & (times <= end)
        if sum(idx) < 2:
            continue

        lats_month = lats[idx]
        lons_month = lons[idx]

        clusters = cluster_locations(lats_month, lons_month)
        number_of_sps = len(set(clusters))
        if -1 in clusters:
            number_of_sps -= 1
        numper_of_places.append(sum(idx))
        sps.append(number_of_sps)

    return np.nanmedian(sps)


def compute_nbin_maxdist_home(lats, lons, latlon_home, home_radius=50):
    """Computes number of bins in home and maximum distance to home

    Parameters
    ----------
    lats : pd.DataFrame
        Latitudes
    lons : pd.DataFrame
        Longitudes
    latlon_home : array
        A tuple (lat, lon) showing the coordinate of home

    Returns
    -------
    (n_home, max_dist_home) : tuple
        `n_home`: number of bins the person has been near the home
        `max_dist_home`: maximum distance that the person has been from home
    """
    if any(np.isnan(latlon_home)):
        time_home = np.nan
        max_dist_home = np.nan
    else:
        home_idx = []
        max_dist_home = 0
        for latlon in zip(lats, lons):
            dist_home = geodesic(latlon, latlon_home).meters
            home_idx.append(dist_home <= home_radius)
            max_dist_home = max(max_dist_home, dist_home)
        time_home = sum(home_idx)
    return time_home, max_dist_home


def extract_distance_features(lats,
                              lons,
                              users,
                              groups,
                              times,
                              speeds=None,
                              speed_threshold=0.277,
                              column_prefix=None):
    """Calculates features realted distance and speed

    Parameters
    ----------
    lats : array
        Latitudes
    lons : array
        Longitudes
    users : array
        Users
    groups : array
        Groups to which users belong
    times : array
        Times when the coordinate is recorded
    speeds : array, optional
        Speeds of the users. If `None`, it computes speeds by dividing
        distance between each two consequitive bins by their time difference.
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
        times = df.index

        # Home realted featuers
        latlon_home = find_home(lats, lons, times)

        speeds, total_dist = get_speeds_totaldist(lats, lons, times)
        if 'double_speed' in df:
            speeds = df['double_speed']

        speed_average = np.nanmean(speeds)
        speed_variance = np.nanvar(speeds)
        speed_max = np.nanmax(speeds)

        static_bins = speeds < speed_threshold
        lats_static = lats[static_bins]
        lons_static = lons[static_bins]
        times_static = times[static_bins]
        clusters = cluster_locations(lats_static, lons_static)

        # n_unique_sps = len(set(non_rare_clusters))
        n_unique_sps = number_of_significant_places(lats_static,
                                                    lons_static,
                                                    times_static)
        non_rare_clusters = clusters[clusters != -1]
        entropy = scipy.stats.entropy(non_rare_clusters)
        normalized_entropy = entropy / np.log(len(set(non_rare_clusters)))

        counter = collections.Counter(clusters)
        stay_times = counter.values()
        stay_times = np.sort(list(stay_times))[::-1]

        n_static = sum(static_bins)
        n_moving = sum(~static_bins)
        n_rare = counter[-1]
        n_home, max_dist_home = compute_nbin_maxdist_home(
            lats_static, lons_static, latlon_home
        )

        n_transitions = sum(np.diff(clusters) != 0)

        n_top1 = stay_times[0] if len(stay_times) > 0 else 0
        n_top2 = stay_times[1] if len(stay_times) > 1 else 0
        n_top3 = stay_times[2] if len(stay_times) > 2 else 0
        n_top4 = stay_times[3] if len(stay_times) > 3 else 0
        n_top5 = stay_times[4] if len(stay_times) > 4 else 0

        row = pd.DataFrame({
            'dist_total': [total_dist],
            'n_bins': [n_bins],
            'speed_average': [speed_average],
            'speed_variance': [speed_variance],
            'speed_max': [speed_max],
            'n_sps': [n_unique_sps],
            'n_static': [n_static],
            'n_moving': [n_moving],
            'n_rare': [n_rare],
            'n_home': [n_home],
            'max_dist_home': [max_dist_home],
            'n_transitions': [n_transitions],
            'n_top1': [n_top1],
            'n_top2': [n_top2],
            'n_top3': [n_top3],
            'n_top4': [n_top4],
            'n_top5': [n_top5],
            'entropy': [entropy],
            'normalized_entropy': [normalized_entropy],
        })
        return row

    location = pd.DataFrame({
        'double_latitude': lats,
        'double_longitude': lons,
        'user': users,
        'group': groups},
        index=times
    )
    if speeds is not None:
        location['double_speed'] = speeds
    location = location.sort_index()
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
