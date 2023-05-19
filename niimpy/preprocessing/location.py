import collections

import pandas as pd
import numpy as np
import scipy.stats
from sklearn.cluster import DBSCAN

from geopy.distance import geodesic

import niimpy

default_freq = "1M"

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
    dists = np.minimum(1, sin_matrix + cos_matrix * lons_diff)
    dists = R * np.arccos(dists)
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

    if n_bins == 0:
        return ([], [])

    dists = np.zeros(n_bins)
    time_deltas = np.ones(n_bins)
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
    if lats.shape[0] == 0 or lons.shape[0] == 0:
        return np.array([])
    dists_matrix = distance_matrix(lats, lons)
    dbscan = DBSCAN(min_samples=min_samples, eps=eps, metric='precomputed')
    clusters = dbscan.fit_predict(dists_matrix)
    return clusters


def number_of_significant_places(lats, lons, times):
    """Computes number of significant places.

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

    Returns : the number of significant places discovered
    """
    sps = []
    number_of_places = []
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
        number_of_places.append(sum(idx))
        sps.append(number_of_sps)

    return np.nanmedian(sps)


def location_number_of_significant_places(df, feature_functions={}):
    """Computes number of significant places """
    latitude_column = feature_functions.get("latitude_column", "double_latitude")
    longitude_column = feature_functions.get("longitude_column", "double_longitude")
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":default_freq}

    def compute_features(df):
        df = df.sort_index()  # sort based on time

        lats = df[latitude_column]
        lons = df[longitude_column]

        clusters = cluster_locations(lats, lons)
        number_of_sps = len(set(clusters))
        if -1 in clusters:
            number_of_sps -= 1
        
        row = pd.Series({
            'n_significant_places': number_of_sps,
        })
        return row
    
    result = df.groupby('user').resample(**feature_functions["resample_args"]).apply(compute_features)
    return result


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


def location_significant_place_features(df, feature_functions={}):
    """Calculates features related to Significant Places.
    
    Parameters
    ----------
    df: dataframe with date index
    feature_functions: A dictionary of optional arguments

    Optional arguments in feature_functions:
        longitude_column: The name of the column with longitude data in a floating point format. Defaults to 'double_longitude'. 
        latitude_column: The name of the column with latitude data in a floating point format. Defaults to 'double_latitude'.
        speed_column: The name of the column with speed data in a floating point format. Defaults to 'double_speed'.
        resample_args: a dictionary of arguments for the Pandas resample function. For example to resample by hour, you would pass {"rule": "1H"}.
    """

    latitude_column = feature_functions.get("latitude_column", "double_latitude")
    longitude_column = feature_functions.get("longitude_column", "double_latitude")
    speed_column = feature_functions.get("speed_column", "double_speed")
    speed_threshold = feature_functions.get("speed_threshold", 0.277)
    
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule": default_freq}

    def compute_features(df):
        """Compute features for a single user"""
        df = df.sort_index()  # sort based on time

        if df.shape[0] == 0:
            return None

        lats = df[latitude_column]
        lons = df[longitude_column]
        times = df.index

        # Home realted featuers
        latlon_home = find_home(lats, lons, times)

        if speed_column in df:
            speeds = df[speed_column]
        else:
            speeds, _ = get_speeds_totaldist(lats, lons, times)

        static_bins = speeds < speed_threshold
        lats_static = lats[static_bins]
        lons_static = lons[static_bins]
        clusters = cluster_locations(lats_static, lons_static)

        non_rare_clusters = clusters[clusters != -1]
        n_unique_sps = len(set(non_rare_clusters))
        if n_unique_sps > 1:
            entropy = scipy.stats.entropy(non_rare_clusters)
            normalized_entropy = entropy / np.log(len(set(non_rare_clusters)))
        else:
            entropy = 0
            normalized_entropy = 0

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

        row = pd.Series({
            'n_sps': n_unique_sps,
            'n_static': n_static,
            'n_moving': n_moving,
            'n_rare': n_rare,
            'n_home': n_home,
            'max_dist_home': max_dist_home,
            'n_transitions': n_transitions,
            'n_top1': n_top1,
            'n_top2': n_top2,
            'n_top3': n_top3,
            'n_top4': n_top4,
            'n_top5': n_top5,
            'entropy': entropy,
            'normalized_entropy': normalized_entropy,
        })
        return row

    result = df.groupby('user').resample(**feature_functions["resample_args"]).apply(compute_features)
    return result


def location_distance_features(df, feature_functions={}):
    """Calculates features related to distance and speed.
    
    Parameters
    ----------
    df: dataframe with date index
    feature_functions: A dictionary of optional arguments

    Optional arguments in feature_functions:
        longitude_column: The name of the column with longitude data in a floating point format. Defaults to 'double_longitude'. 
        latitude_column: The name of the column with latitude data in a floating point format. Defaults to 'double_latitude'.
        speed_column: The name of the column with speed data in a floating point format. Defaults to 'double_speed'.
        resample_args: a dictionary of arguments for the Pandas resample function. For example to resample by hour, you would pass {"rule": "1H"}.
    """
    latitude_column = feature_functions.get("latitude_column", "double_latitude")
    longitude_column = feature_functions.get("longitude_column", "double_latitude")
    speed_column = feature_functions.get("speed_column", "double_speed")
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":default_freq}

    def compute_features(df):
        """Compute features for a single user and given time interval"""
        df = df.sort_index()  # sort based on time
        n_bins = df.shape[0]

        if n_bins == 0:
            return None

        lats = df[latitude_column]
        lons = df[longitude_column]
        times = df.index

        speeds, total_dist = get_speeds_totaldist(lats, lons, times)
        if speed_column in df:
            speeds = df[speed_column]

        speed_average = np.nanmean(speeds)
        speed_variance = np.nanvar(speeds)
        speed_max = np.nanmax(speeds)

        variance = np.var(lats) + np.var(lons)
        if variance > 0:
            log_variance = np.log(variance)
        else:
            log_variance = -np.inf

        row = pd.Series({
            'dist_total': total_dist,
            'n_bins': n_bins,
            'speed_average': speed_average,
            'speed_variance': speed_variance,
            'speed_max': speed_max,
            'variance': variance,
            'log_variance': log_variance,
        })
        return row

    result = df.groupby('user').resample(**feature_functions["resample_args"]).apply(compute_features)
    return result

ALL_FEATURE_FUNCTIONS = [globals()[name] for name in globals()
                         if name.startswith('location_')]
ALL_FEATURE_FUNCTIONS = {x: {} for x in ALL_FEATURE_FUNCTIONS}


def extract_features_location(df,
                              feature_functions=None):
    """Calculates location features

    Parameters
    ----------
    df : pd.DataFrame
        dataframe of location data. It must contain these columns:
        `double_latitude`, `double_longitude`, `user`, `group`.
        `double_speed` is optional. If not provided, it will be
        computed manually.
    speed_threshold : float
        Bins whose speed is lower than `speed_threshold` are considred
        `static` and the rest are `moving`.
    feature_functions : map (dictionary) of functions that compute features.
        it is a map of map, where the keys to the first map is the name of
        functions that compute features and the nested map contains the keyword
        arguments to that function. If there is no arguments use an empty map.
        Default is None. If None, all the available functions are used.
        Those functions are in the dict `location.ALL_FEATURE_FUNCTIONS`.
        You can implement your own function and use it instead or add it
        to the mentioned map.

    Returns
    -------
    features : pd.DataFrame
        Dataframe of computed features where the index is users and columns
        are the the features.
    """
    if feature_functions is None:
        feature_functions = ALL_FEATURE_FUNCTIONS
    else:
        assert isinstance(feature_functions, dict), "Please input the feature_functions as a dictionary"

    computed_features = []
    for feature_function, feature_arg in feature_functions.items():
        computed_feature = feature_function(df, feature_arg)
        computed_features.append(computed_feature)
    
    computed_features = pd.concat(computed_features, axis=1)
    computed_features = computed_features.loc[:,~computed_features.columns.duplicated()]

    if 'group' in df:
        computed_features['group'] = df.groupby('user')['group'].first()

    return computed_features
