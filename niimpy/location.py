
import pandas as pd

from geopy.distance import geodesic


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

    location_to_aggregate = location_to_aggregate. \
        groupby(['user', 'time']). \
        median(). \
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
    location = location.drop_duplicates()
    return location


def extract_total_distance(location, column_prefix=None):
    """Calculates the total distance traveled for each user

    Parameters
    ----------
    location : pd.DataFrame
        Dataframe of locations indexed by time. These columns have to exist
        in the dataframe: `user`, `double_latitude`, `double_longitude`.

    column_prefix : str
        Add a prefix to all column names.

    Returns
    -------
    total_dist : pd.DataFrame
        Dataframe of computed distances where the index is users and columns
        are the calculated features.
    """
    def compute_total_distance(df):
        """Compute total distance for a single user"""
        dist = 0
        for i in range(df.shape[0] - 2):
            loc1 = df.iloc[i][['double_latitude', 'double_longitude']]
            loc2 = df.iloc[i + 1][['double_latitude', 'double_longitude']]
            dist += geodesic(loc1, loc2).meters
        row = pd.DataFrame({
            'total_dist': [dist],
            'normalized_total_dist': [dist / df.shape[0]]
        })
        return row

    total_dist = location.groupby('user').apply(compute_total_distance)
    return total_dist
