import re

def format_column_names(df):
    # Replace special characters, including space and ., with _
    # (keeping parenthesis and /, which are used in units, e.g. "temperature (C)")
    # Convert to lower case
    column_map = {}
    for column in df.columns:
        formatted_name = column.replace(" ", "_").lower()
        formatted_name = re.sub(r'[^a-zA-Z0-9_()/]+', '_', formatted_name)
        column_map[column] = formatted_name
    df.rename(columns=column_map, inplace=True)

def set_timezone(df, tz = 'Europe/Helsinki'):
    """ Set the timezone of the datetime object in the index column """
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(tz)
    return df

