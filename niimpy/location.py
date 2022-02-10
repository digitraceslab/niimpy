import pandas as pd
import numpy as np

from geopy.distance import geodesic


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
                 columns_to_aggregate=['double_latitude', 'double_longitude']):
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


def extract_distance_features(location, column_prefix=None):
    """Calculates features realted distance and speed

    Parameters
    ----------
    location : pd.DataFrame
        Dataframe of locations indexed by time. These columns have to exist
        in the dataframe: `user`, `double_latitude`, `double_longitude`.

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
        total_dist = 0
        speeds = []
        for i in range(df.shape[0] - 2):
            loc1 = df.iloc[i][['double_latitude', 'double_longitude']]
            loc2 = df.iloc[i + 1][['double_latitude', 'double_longitude']]
            dist = geodesic(loc1, loc2).meters
            total_dist += dist

            time_delta = (df.index[i + 1] - df.index[i]).seconds
            if time_delta > 0:
                speeds.append(dist / time_delta)
        speed_average = np.mean(speeds)
        speed_variance = np.var(speeds)
        row = pd.DataFrame({
            'dist_total': [total_dist],
            'n_bins': [df.shape[0]],
            'speed_average': [speed_average],
            'speed_variance': [speed_variance]
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
