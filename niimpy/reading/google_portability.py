import pandas as pd
from zipfile import ZipFile
import json


def youtube_history(filename, start_date=None, end_date=None):
    """
    Reads YouTube watch history from zip file downloaded from the Google Portability API.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/YouTube/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # Convert the known `time` column to datetime and filter if requested
    df['timestamp'] = pd.to_datetime(df['time'], errors='coerce')

    if start_date is not None:
        start = pd.to_datetime(start_date)
        df = df[df['timestamp'] >= start]
    if end_date is not None:
        end = pd.to_datetime(end_date)
        df = df[df['timestamp'] <= end]
        
    # flatten the subtitles column, a list of dicts, containing the channel name and video title
    subtitles = df['subtitles'].explode().apply(pd.Series)
    subtitles = subtitles.add_prefix('channel_')
    df = pd.concat([df.drop(columns=['subtitles']), subtitles], axis=1)
    df = df.drop(columns=['channel_0'])

    # Activity controls to a comma separated string
    df['activityControls'] = df['activityControls'].apply(
        lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
    )

    # drop products and header, instead add product = "YouTube"
    df = df.drop(columns=['header'])
    df = df.drop(columns=['products'])
    df['platform'] = 'YouTube'

    # Get the video ID from the titleUrl
    df['video_id'] = df['titleUrl'].str.extract(r'v=([a-zA-Z0-9_-]{11})')

    #rename titleUrl to url
    df = df.rename(columns={'titleUrl': 'url'})

    # The first word in title is the action
    df['action'] = df['title'].str.split(' ').str[0]

    def remove_action_and_preposition(title):
        if not isinstance(title, str):
            return title
        words = title.split()
        if len(words) > 1 and words[1] in ["to", "for"]:
            return ' '.join(words[2:])
        return ' '.join(words[1:])
    df["title"] = df["title"].apply(remove_action_and_preposition)

    return df


def discover_history(filename, start_date=None, end_date=None):
    """
    Reads Discover activity from zip file downloaded from the Google Portability API.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/Discover/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # convert time to timestamp and filter if requested
    df['timestamp'] = pd.to_datetime(df['time'], errors='coerce')
    if start_date is not None:
        start = pd.to_datetime(start_date)
        df = df[df['timestamp'] >= start]
    if end_date is not None:
        end = pd.to_datetime(end_date)
        df = df[df['timestamp'] <= end]

    # Activity controls to a comma separated string
    if 'activityControls' in df.columns:
        df['activityControls'] = df['activityControls'].apply(
            lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
        )

    # drop header/products if present, add platform
    df = df.drop(columns=['header', 'products'], errors='ignore')
    df['platform'] = 'Discover'
    df['type'] = 'history'

    return df


def _find_zip_entry(z, basename):
    """Return the full zip entry name that ends with the given basename, or None."""
    names = z.namelist()
    for name in names:
        if name.endswith('/' + basename) or name == basename:
            return name
    return None


def discover_liked_content(filename, start_date=None, end_date=None):
    """Read 'Your Liked Content.csv' from the portability zip and return a DataFrame.

    Columns normalized to: `content_url`, `liked_date` (datetime).
    """
    with ZipFile(filename, 'r') as z:
        entry = _find_zip_entry(z, 'Your Liked Content.csv')
        if entry is None:
            return pd.DataFrame()
        with z.open(entry) as f:
            df = pd.read_csv(f, sep=None, engine='python')

    # Normalize columns
    if 'Content Url' in df.columns:
        df = df.rename(columns={'Content Url': 'content_url', 'Liked Date': 'liked_date'})
    elif 'Content URL' in df.columns:
        df = df.rename(columns={'Content URL': 'content_url', 'Liked Date': 'liked_date'})

    if 'liked_date' in df.columns:
        df['liked_date'] = pd.to_datetime(df['liked_date'].astype(str).str.strip('"'), errors='coerce')

    # filter by liked_date if requested
    if start_date is not None and 'liked_date' in df.columns:
        start = pd.to_datetime(start_date)
        df = df[df['liked_date'] >= start]
    if end_date is not None and 'liked_date' in df.columns:
        end = pd.to_datetime(end_date)
        df = df[df['liked_date'] <= end]

    df['platform'] = 'Discover'
    df['subtype'] = 'liked_content'
    df['type'] = 'liked'
    # create a unified timestamp column from liked_date if present
    if 'liked_date' in df.columns:
        df['timestamp'] = pd.to_datetime(df['liked_date'], errors='coerce')

    return df


def discover_follows(filename, start_date=None, end_date=None):
    """Read 'Your Follows.csv' from the portability zip and return a DataFrame.

    Columns normalized to: `followed_entity`.
    """
    with ZipFile(filename, 'r') as z:
        entry = _find_zip_entry(z, 'Your Follows.csv')
        if entry is None:
            return pd.DataFrame()
        with z.open(entry) as f:
            df = pd.read_csv(f, sep=None, engine='python')

    # Normalize column
    if 'Followed Entity' in df.columns:
        df = df.rename(columns={'Followed Entity': 'followed_entity'})

    # attempt to find a date-like column for filtering
    timestamp_col = None
    for c in ['time', 'timestamp', 'date', 'Followed Date', 'followed_date', 'Date']:
        if c in df.columns:
            timestamp_col = c
            break
    if timestamp_col is not None:
        df['timestamp'] = pd.to_datetime(df[timestamp_col], errors='coerce')
        if start_date is not None:
            start = pd.to_datetime(start_date)
            df = df[df['timestamp'] >= start]
        if end_date is not None:
            end = pd.to_datetime(end_date)
            df = df[df['timestamp'] <= end]

    df['platform'] = 'Discover'
    df['subtype'] = 'follows'
    df['type'] = 'follows'

    return df


def discover_not_interested_settings(filename, start_date=None, end_date=None):
    """Read 'Not Interested Setting.csv' and return a DataFrame.

    Columns normalized to: `entity_name`, `setting_value`.
    """
    with ZipFile(filename, 'r') as z:
        entry = _find_zip_entry(z, 'Not Interested Setting.csv')
        if entry is None:
            return pd.DataFrame()
        with z.open(entry) as f:
            df = pd.read_csv(f, sep=None, engine='python')

    # Normalize columns
    if 'Entity Name' in df.columns or 'Entity name' in df.columns:
        src = 'Entity Name' if 'Entity Name' in df.columns else 'Entity name'
        df = df.rename(columns={src: 'entity_name', 'Setting Value': 'setting_value'})

    # attempt to find a date-like column for filtering
    timestamp_col = None
    for c in ['time', 'timestamp', 'date', 'Date']:
        if c in df.columns:
            timestamp_col = c
            break
    if timestamp_col is not None:
        df['timestamp'] = pd.to_datetime(df[timestamp_col], errors='coerce')
        if start_date is not None:
            start = pd.to_datetime(start_date)
            df = df[df['timestamp'] >= start]
        if end_date is not None:
            end = pd.to_datetime(end_date)
            df = df[df['timestamp'] <= end]

    df['platform'] = 'Discover'
    df['subtype'] = 'not_interested'
    df['type'] = 'not_interested'

    return df


def discover(filename, start_date=None, end_date=None):
    """Return all Discover-related datasets as a dict of DataFrames.

    Keys: `history`, `liked_content`, `follows`, `not_interested_settings`.
    """
    parts = [
        discover_history(filename, start_date=start_date, end_date=end_date),
        discover_liked_content(filename, start_date=start_date, end_date=end_date),
        discover_follows(filename, start_date=start_date, end_date=end_date),
        discover_not_interested_settings(filename, start_date=start_date, end_date=end_date),
    ]
    # concatenate available parts into a single DataFrame
    combined = pd.concat([p for p in parts if p is not None and not p.empty], ignore_index=True, sort=False)

    # If there's a datetime-like `timestamp` column, convert it to unix seconds
    if 'timestamp' in combined.columns:
        ts = pd.to_datetime(combined['timestamp'], errors='coerce')
        combined['timestamp'] = ts.apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')

    return combined


def chrome_history(filename, start_date=None, end_date=None):
    """Read Chrome History.json from the portability zip.

    Heuristically find a time-like column, create a `timestamp` column
    with unix seconds (nullable `Int64`), and apply optional start/end
    filtering. Other column names are kept as-is.
    """
    with ZipFile(filename, 'r') as z:
        entry = _find_zip_entry(z, 'History.json')
        if entry is None:
            return pd.DataFrame()
        with z.open(entry) as f:
            data = json.load(f)

    df = pd.json_normalize(data)

    # Try several common timestamp column names
    timestamp_col = None
    for c in ['time', 'timestamp', 'lastVisitTime', 'visitTime', 'visit_time', 'date', 'Typed Date', 'Typed Time']:
        if c in df.columns:
            timestamp_col = c
            break

    if timestamp_col is not None:
        ts = pd.to_datetime(df[timestamp_col], errors='coerce')
        df['timestamp'] = ts.apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')
    else:
        df['timestamp'] = pd.NA

    # Apply start/end filters if requested (convert to unix seconds for comparison)
    if start_date is not None:
        start_ts = int(pd.to_datetime(start_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] >= start_ts)]
    if end_date is not None:
        end_ts = int(pd.to_datetime(end_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] <= end_ts)]

    return df


def google_lens_history(filename, start_date=None, end_date=None):
    """Reads Google Lens activity from portability zip.

    Path: 'Portability/My Activity/Google Lens/MyActivity.json'
    Returns a DataFrame with a `timestamp` (unix seconds, nullable Int64),
    `platform='Google Lens'`, and `type='google_lens'`. Applies optional
    `start_date`/`end_date` filtering.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/Google Lens/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # parse time -> timestamp
    df['timestamp'] = pd.to_datetime(df.get('time'), errors='coerce')
    if 'timestamp' in df.columns:
        df['timestamp'] = df['timestamp'].apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')
    else:
        df['timestamp'] = pd.NA

    if start_date is not None:
        start_ts = int(pd.to_datetime(start_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] >= start_ts)]
    if end_date is not None:
        end_ts = int(pd.to_datetime(end_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] <= end_ts)]

    # Activity controls to a comma separated string
    if 'activityControls' in df.columns:
        df['activityControls'] = df['activityControls'].apply(
            lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
        )

    # drop header/products if present, add platform/type
    df = df.drop(columns=['header', 'products'], errors='ignore')
    df['platform'] = 'Google Lens'
    df['type'] = 'google_lens'

    return df


def google_play_games_history(filename, start_date=None, end_date=None):
    """Reads Google Play Games activity from portability zip.

    Path: 'Portability/My Activity/Google Play Games/MyActivity.json'
    Returns a DataFrame with a `timestamp` (unix seconds, nullable Int64),
    `platform='Google Play Games'`, and `type='play_games'`. Applies optional
    `start_date`/`end_date` filtering.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/Google Play Games/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # parse time -> timestamp (unix seconds)
    dt = pd.to_datetime(df.get('time'), errors='coerce')
    df['timestamp'] = dt.apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')

    # apply start/end filters (compare unix seconds)
    if start_date is not None:
        start_ts = int(pd.to_datetime(start_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] >= start_ts)]
    if end_date is not None:
        end_ts = int(pd.to_datetime(end_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] <= end_ts)]

    # Activity controls to a comma separated string
    if 'activityControls' in df.columns:
        df['activityControls'] = df['activityControls'].apply(
            lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
        )

    # drop header/products if present, add platform/type
    df = df.drop(columns=['header', 'products'], errors='ignore')
    df['platform'] = 'Google Play Games'
    df['type'] = 'play_games'

    return df


def google_play_store_history(filename, start_date=None, end_date=None):
    """Reads Google Play Store activity from portability zip.

    Path: 'Portability/My Activity/Google Play Store/MyActivity.json'
    Returns a DataFrame with a `timestamp` (unix seconds, nullable Int64),
    `platform='Google Play Store'`, and `type='play_store'`. Applies optional
    `start_date`/`end_date` filtering.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/Google Play Store/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # parse time -> timestamp (unix seconds)
    dt = pd.to_datetime(df.get('time'), errors='coerce')
    df['timestamp'] = dt.apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')

    # apply start/end filters (compare unix seconds)
    if start_date is not None:
        start_ts = int(pd.to_datetime(start_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] >= start_ts)]
    if end_date is not None:
        end_ts = int(pd.to_datetime(end_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] <= end_ts)]

    # Activity controls to a comma separated string
    if 'activityControls' in df.columns:
        df['activityControls'] = df['activityControls'].apply(
            lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
        )

    # drop header/products if present, add platform/type
    df = df.drop(columns=['header', 'products'], errors='ignore')
    df['platform'] = 'Google Play Store'
    df['type'] = 'play_store'

    return df


def image_search_history(filename, start_date=None, end_date=None):
    """Reads Image Search MyActivity.json, flattens optional locationInfos,
    converts `time` to unix-second `timestamp` (nullable `Int64`), and
    applies optional start/end filtering.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/Image Search/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # parse time into unix-second timestamp
    dt = pd.to_datetime(df.get('time'), errors='coerce')
    df['timestamp'] = dt.apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')

    # apply start/end filters (compare unix seconds)
    if start_date is not None:
        start_ts = int(pd.to_datetime(start_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] >= start_ts)]
    if end_date is not None:
        end_ts = int(pd.to_datetime(end_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] <= end_ts)]

    # handle locationInfos: json_normalize may have flattened it into
    # columns starting with 'locationInfos.' OR left a list-valued column.
    loc_cols = [c for c in df.columns if c.startswith('locationInfos.')]
    if loc_cols:
        # rename flattened columns to location_*
        rename_map = {c: 'location_' + c.split('.', 1)[1] for c in loc_cols}
        df = df.rename(columns=rename_map)

    # normalize activityControls
    if 'activityControls' in df.columns:
        df['activityControls'] = df['activityControls'].apply(
            lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
        )

    df = df.drop(columns=['header', 'products'], errors='ignore')
    df['platform'] = 'Image Search'
    df['type'] = 'image_search'

    return df


def video_search_history(filename, start_date=None, end_date=None):
    """Reads Video Search MyActivity.json and returns a flattened DataFrame.

    Converts `time` to unix-second `timestamp` (nullable `Int64`), applies
    optional `start_date`/`end_date` filters, extracts `video_id` from
    `titleUrl` when present, normalizes `activityControls`, renames
    `titleUrl` to `url`, and sets `platform='Video Search'` and
    `type='video_search'`.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/Video Search/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # parse time into unix-second timestamp
    dt = pd.to_datetime(df.get('time'), errors='coerce')
    df['timestamp'] = dt.apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')

    # apply start/end filters (compare unix seconds)
    if start_date is not None:
        start_ts = int(pd.to_datetime(start_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] >= start_ts)]
    if end_date is not None:
        end_ts = int(pd.to_datetime(end_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] <= end_ts)]

    # extract video id when titleUrl is a YouTube URL
    if 'titleUrl' in df.columns:
        df['video_id'] = df['titleUrl'].str.extract(r'v=([a-zA-Z0-9_-]{11})')
        df = df.rename(columns={'titleUrl': 'url'})

    # normalize activityControls
    if 'activityControls' in df.columns:
        df['activityControls'] = df['activityControls'].apply(
            lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
        )

    df = df.drop(columns=['header', 'products'], errors='ignore')
    df['platform'] = 'Video Search'
    df['type'] = 'video_search'

    return df


def search_history(filename, start_date=None, end_date=None):
    """Reads Search MyActivity.json and returns a flattened DataFrame.

    This function keeps columns as produced by `pd.json_normalize` (no
    assumptions about column types), converts the required `time` column
    to a unix-second `timestamp` (nullable `Int64`), applies optional
    `start_date`/`end_date` filtering, and preserves other columns.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/Search/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

    # Convert required `time` column to unix-second timestamp
    dt = pd.to_datetime(df.get('time'), errors='coerce')
    df['timestamp'] = dt.apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')

    # Apply start/end filters (compare unix seconds)
    if start_date is not None:
        start_ts = int(pd.to_datetime(start_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] >= start_ts)]
    if end_date is not None:
        end_ts = int(pd.to_datetime(end_date).timestamp())
        df = df[df['timestamp'].notna() & (df['timestamp'] <= end_ts)]

    # Normalize activityControls if present
    if 'activityControls' in df.columns:
        df['activityControls'] = df['activityControls'].apply(
            lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else str(x)
        )

    df['platform'] = 'Search'
    df['type'] = 'search'

    return df


