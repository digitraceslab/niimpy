import pandas as pd
from zipfile import ZipFile
import json


def youtube_history(filename):
    """
    Reads YouTube watch history from zip file downloaded from the Google Portability API.
    """
    with ZipFile(filename, 'r') as z:
        with z.open('Portability/My Activity/YouTube/MyActivity.json') as f:
            data = json.load(f)
    df = pd.json_normalize(data)

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
