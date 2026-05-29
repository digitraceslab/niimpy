"""Read data from TikTok data exports."""

import json
import re
import uuid

import pandas as pd

from niimpy.reading import util


MISSING_STRINGS = {"", "N/A", "NA", "n/a", "na", "None", "none", "null"}


def _load_json(filename):
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def _get_path(data, path, default=None):
    value = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def _record_list(data, path):
    records = _get_path(data, path, [])
    if records is None:
        return []
    return records


def _profile_username(data):
    return _get_path(
        data,
        ["Profile And Settings", "Profile Info", "ProfileMap", "userName"],
        None,
    )


def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() in MISSING_STRINGS
    try:
        missing = pd.isna(value)
        return bool(missing)
    except (TypeError, ValueError):
        return False


def _pseudonymize_column(df, column, user_value=None):
    """Replace values in a column with deterministic integer identifiers."""
    if column not in df.columns:
        return df

    value_map = {}
    if user_value is not None and not _is_missing(user_value):
        value_map[user_value] = 0

    def add_value(value):
        if _is_missing(value):
            return
        if value not in value_map:
            value_map[value] = len(value_map)
            if user_value is None:
                value_map[value] += 1

    for value in df[column]:
        if isinstance(value, list):
            for item in value:
                add_value(item)
        else:
            add_value(value)

    def replace_value(value):
        if isinstance(value, list):
            return [replace_value(item) for item in value]
        if _is_missing(value):
            return pd.NA
        return value_map[value]

    df[column] = df[column].apply(replace_value)
    return df


def _pseudonymize_columns(df, columns, user_values=None):
    if user_values is None:
        user_values = {}
    for column in columns:
        df = _pseudonymize_column(df, column, user_values.get(column))
    return df


def _convert_pseudonymized_ids(df):
    """Use nullable integers for pseudonymized IDs in mixed event data."""
    id_columns = [
        "conversation_id", "from", "to", "shared_video_id", "video_id",
        "target_id", "photo", "url", "video", "cover_image", "title",
        "sound", "location", "username", "ip", "device_model",
        "carrier", "shared_content", "favorite_collection", "search_term",
    ]
    for column in id_columns:
        if column in df.columns:
            df[column] = df[column].astype("Int64")
    return df


def _clean_placeholders(df, columns):
    """Convert TikTok placeholder strings to missing values."""
    for column in columns:
        if column not in df.columns:
            continue
        df[column] = df[column].apply(lambda x: pd.NA if _is_missing(x) else x)
    return df


def _filter_by_date(df, start_date=None, end_date=None):
    if start_date is not None:
        start_date = pd.to_datetime(start_date, utc=True)
        df = df[df.index >= start_date]
    if end_date is not None:
        end_date = pd.to_datetime(end_date, utc=True)
        df = df[df.index <= end_date]
    return df


def _finish_timeseries(
        df,
        date_column,
        user,
        event_type,
        source_section,
        start_date=None,
        end_date=None,
    ):
    if df.empty or date_column not in df.columns:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df[date_column], format="mixed", utc=True, errors="coerce")
    df.dropna(subset=["timestamp"], inplace=True)
    if df.empty:
        return pd.DataFrame()

    df.set_index("timestamp", inplace=True)
    df.drop(date_column, axis=1, inplace=True, errors="ignore")
    df = _filter_by_date(df, start_date, end_date)
    if df.empty:
        return pd.DataFrame()

    if user is None:
        user = uuid.uuid1()
    df["user"] = user
    df["application_name"] = "TikTok"
    df["event_type"] = event_type
    df["event_count"] = 1
    df["source_section"] = source_section
    df["datetime"] = df.index
    df.sort_index(inplace=True)
    util.format_column_names(df)
    return df


def _extract_video_id(link):
    if not isinstance(link, str):
        return pd.NA
    match = re.search(r"/video/(\d+)", link)
    if match:
        return match.group(1)
    return pd.NA


def _format_link_data(df, link_column="Link", pseudonymize=True):
    if link_column in df.columns:
        df["video_id"] = df[link_column].apply(_extract_video_id)
        if pseudonymize:
            df = _pseudonymize_column(df, "video_id")
            df.drop(link_column, axis=1, inplace=True)
    return df


def _message_counts(text):
    if not isinstance(text, str):
        return 0, 0
    return len(text), len(text.split())


def _comment_target(row):
    for column, target_type in [("video", "video"), ("url", "url"), ("photo", "photo")]:
        value = row.get(column)
        if not _is_missing(value):
            return target_type, value
    return "unknown", pd.NA


def watch_history(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read watched video events from a TikTok data export.

    TikTok exports store timestamps without timezone information. They are
    interpreted as UTC.
    """
    data = _load_json(filename)
    records = _record_list(data, ["Your Activity", "Watch History", "VideoList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df = _format_link_data(df, "Link", pseudonymize)
    return _finish_timeseries(
        df, "Date", user, "watch", "Your Activity.Watch History",
        start_date, end_date,
    )


def search_history(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read search events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Your Activity", "Searches", "SearchList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df.rename(columns={"SearchTerm": "search_term"}, inplace=True)
    df["search_term_length"] = df["search_term"].apply(lambda x: len(x) if isinstance(x, str) else 0)
    df["search_term_word_count"] = df["search_term"].apply(
        lambda x: len(x.split()) if isinstance(x, str) else 0
    )
    if pseudonymize:
        df = _pseudonymize_column(df, "search_term")

    return _finish_timeseries(
        df, "Date", user, "search", "Your Activity.Searches",
        start_date, end_date,
    )


def direct_messages(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read direct messages from a TikTok data export.

    The message text is not returned. Instead, character and word counts are
    retained, following the Google Takeout chat reader.
    """
    data = _load_json(filename)
    chat_history = _get_path(
        data,
        ["Direct Message", "Direct Messages", "ChatHistory"],
        {},
    )
    if not chat_history:
        return pd.DataFrame()

    exported_user = _profile_username(data)
    rows = []
    for conversation, messages in chat_history.items():
        if not messages:
            continue
        contact = conversation.replace("Chat History with ", "").strip(":")
        for message in messages:
            sender = message.get("From", "")
            content = message.get("Content", "")
            character_count, word_count = _message_counts(content)
            if exported_user:
                is_outgoing = sender == exported_user
            else:
                is_outgoing = sender != contact
            sender_user = exported_user or "user"
            rows.append({
                "Date": message.get("Date"),
                "conversation_id": contact,
                "from": sender_user if is_outgoing else sender,
                "to": contact if is_outgoing else sender_user,
                "message_type": "outgoing" if is_outgoing else "incoming",
                "character_count": character_count,
                "word_count": word_count,
                "has_url": bool(re.search(r"https?://", content)),
                "shared_video_id": _extract_video_id(content),
            })

    df = pd.DataFrame(rows)
    if pseudonymize:
        user_values = {
            "from": exported_user or "user",
            "to": exported_user or "user",
        }
        df = _pseudonymize_columns(
            df,
            ["conversation_id", "from", "to", "shared_video_id"],
            user_values,
        )

    return _finish_timeseries(
        df, "Date", user, "direct_message", "Direct Message.Direct Messages",
        start_date, end_date,
    )


def comments(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read comment events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Comment", "Comments", "CommentsList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    exported_user = _profile_username(data) or "user"
    df = _clean_placeholders(df, ["photo", "url", "video"])
    targets = df.apply(_comment_target, axis=1)
    df["target_type"] = targets.apply(lambda x: x[0])
    df["target_id"] = targets.apply(lambda x: x[1])
    if "url" in df.columns:
        df["video_id"] = df["url"].apply(_extract_video_id)
    else:
        df["video_id"] = pd.NA
    df["character_count"] = df["comment"].apply(lambda x: len(x) if isinstance(x, str) else 0)
    df["word_count"] = df["comment"].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)
    df["message_type"] = "outgoing"
    df["from"] = exported_user
    df["to"] = df["target_id"]
    df.drop("comment", axis=1, inplace=True)
    if pseudonymize:
        df = _pseudonymize_column(df, "from", exported_user)
        df = _pseudonymize_columns(
            df,
            ["photo", "url", "video", "target_id", "video_id"],
        )
        df["to"] = df["target_id"]

    return _finish_timeseries(
        df, "date", user, "comment", "Comment.Comments",
        start_date, end_date,
    )


def liked_videos(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read liked video events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Likes and Favorites", "Like List", "ItemFavoriteList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df = _format_link_data(df, "link", pseudonymize)
    df["interaction_type"] = "like"
    return _finish_timeseries(
        df, "date", user, "like", "Likes and Favorites.Like List",
        start_date, end_date,
    )


def favorite_videos(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read favorite video events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Likes and Favorites", "Favorite Videos", "FavoriteVideoList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df = _format_link_data(df, "Link", pseudonymize)
    df["interaction_type"] = "favorite"
    return _finish_timeseries(
        df, "Date", user, "favorite_video", "Likes and Favorites.Favorite Videos",
        start_date, end_date,
    )


def favorite_collections(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read favorite collection events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(
        data,
        ["Likes and Favorites", "Favorite Collection", "FavoriteCollectionList"],
    )
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df.rename(columns={"FavoriteCollection": "favorite_collection"}, inplace=True)
    if pseudonymize:
        df = _pseudonymize_column(df, "favorite_collection")

    return _finish_timeseries(
        df, "Date", user, "favorite_collection",
        "Likes and Favorites.Favorite Collection", start_date, end_date,
    )


def posts(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read post events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Post", "Posts", "VideoList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df = _format_link_data(df, "Link", pseudonymize)
    df.rename(columns={
        "AIGeneratedContent": "ai_generated_content",
        "AddYoursText": "add_yours_text",
        "AllowComments": "allow_comments",
        "AllowDuets": "allow_duets",
        "AllowSharingToStory": "allow_sharing_to_story",
        "AllowStickers": "allow_stickers",
        "AllowStitches": "allow_stitches",
        "AlternateText": "alternate_text",
        "ContentDisclosure": "content_disclosure",
        "CoverImage": "cover_image",
        "Likes": "likes",
        "Location": "location",
        "NumberOfCollections": "number_of_collections",
        "Sound": "sound",
        "Title": "title",
        "WhoCanView": "who_can_view",
    }, inplace=True)
    for column in ["Likes", "NumberOfCollections"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    for column in ["likes", "number_of_collections"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if pseudonymize:
        df = _pseudonymize_columns(
            df,
            ["cover_image", "title", "sound", "location"],
        )

    return _finish_timeseries(
        df, "Date", user, "post", "Post.Posts",
        start_date, end_date,
    )


def followers(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read follower events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Profile And Settings", "Follower", "FansList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df.rename(columns={"UserName": "username"}, inplace=True)
    if pseudonymize:
        df = _pseudonymize_column(df, "username")

    return _finish_timeseries(
        df, "Date", user, "follower", "Profile And Settings.Follower",
        start_date, end_date,
    )


def profile_views(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read profile view events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(
        data,
        ["Profile And Settings", "ProfileViews", "ProfileViewList"],
    )
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df.rename(columns={"Username": "username"}, inplace=True)
    if pseudonymize:
        df = _pseudonymize_column(df, "username")

    return _finish_timeseries(
        df, "Date", user, "profile_view", "Profile And Settings.ProfileViews",
        start_date, end_date,
    )


def login_history(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read login events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Your Activity", "Login History", "LoginHistoryList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df.rename(columns={
        "DeviceModel": "device_model",
        "DeviceSystem": "device_system",
        "NetworkType": "network_type",
    }, inplace=True)
    if pseudonymize:
        df = _pseudonymize_columns(df, ["IP", "device_model", "Carrier"])

    return _finish_timeseries(
        df, "Date", user, "login", "Your Activity.Login History",
        start_date, end_date,
    )


def share_history(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read share events from a TikTok data export."""
    data = _load_json(filename)
    records = _record_list(data, ["Your Activity", "Share History", "ShareHistoryList"])
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()

    df = _format_link_data(df, "Link", pseudonymize)
    df.rename(columns={"Method": "method", "SharedContent": "shared_content"}, inplace=True)
    if pseudonymize:
        df = _pseudonymize_column(df, "shared_content")

    return _finish_timeseries(
        df, "Date", user, "share", "Your Activity.Share History",
        start_date, end_date,
    )


def activity_summary(filename, user=None):
    """Read account-level TikTok activity summary counts."""
    data = _load_json(filename)
    summary = _get_path(data, ["Your Activity", "Activity Summary", "ActivitySummaryMap"], {})
    if not summary:
        return pd.DataFrame()
    df = pd.DataFrame([summary])
    if user is None:
        user = uuid.uuid1()
    df["user"] = user
    util.format_column_names(df)
    return df


def profile_info(filename, user=None, pseudonymize=True):
    """Read account profile information from a TikTok data export."""
    data = _load_json(filename)
    profile = _get_path(data, ["Profile And Settings", "Profile Info", "ProfileMap"], {})
    if not profile:
        return pd.DataFrame()
    df = pd.json_normalize([profile])
    if pseudonymize:
        df.drop("PlatformInfo", axis=1, inplace=True, errors="ignore")
        df = _pseudonymize_columns(
            df,
            [
                "userName", "displayName", "emailAddress", "telephoneNumber",
                "bioDescription", "birthDate", "profilePhoto", "profileVideo",
                "aiSelf", "instagramLink", "youtubeLink", "lemon8Link",
            ],
        )
    if user is None:
        user = uuid.uuid1()
    df["user"] = user
    util.format_column_names(df)
    return df


def settings(filename, user=None):
    """Read TikTok settings from a data export."""
    data = _load_json(filename)
    settings_map = _get_path(data, ["Profile And Settings", "Settings", "SettingsMap"], {})
    if not settings_map:
        return pd.DataFrame()
    df = pd.json_normalize([settings_map])
    if user is None:
        user = uuid.uuid1()
    df["user"] = user
    util.format_column_names(df)
    return df


def events(
        filename,
        user=None,
        pseudonymize=True,
        start_date=None,
        end_date=None,
    ):
    """Read all supported timestamped TikTok events into one DataFrame."""
    readers = [
        watch_history,
        search_history,
        direct_messages,
        comments,
        liked_videos,
        favorite_videos,
        favorite_collections,
        posts,
        followers,
        profile_views,
        login_history,
        share_history,
    ]

    dataframes = []
    for reader in readers:
        df = reader(
            filename,
            user=user,
            pseudonymize=pseudonymize,
            start_date=start_date,
            end_date=end_date,
        )
        if not df.empty:
            dataframes.append(df.dropna(axis=1, how="all"))

    if not dataframes:
        return pd.DataFrame()
    df = pd.concat(dataframes, sort=False)
    df.sort_index(inplace=True)
    if pseudonymize:
        df = _convert_pseudonymized_ids(df)
    return df
