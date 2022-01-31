
import pandas as pd

from geopy.distance import geodesic


def bin_location(location,
                 bin_width=10,
                 aggregation='median',
                 columns_to_aggregate=['double_latitude', 'double_longitude']):
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
    def compute_total_distance(df):
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
