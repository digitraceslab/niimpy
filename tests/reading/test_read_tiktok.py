import pandas as pd

import niimpy
from niimpy import config
from niimpy.preprocessing import communication as comms


def test_read_tiktok_watch_history():
    data = niimpy.reading.tiktok.watch_history(
        config.TIKTOK_USER_DATA_2_PATH,
        user="user1",
    )

    assert data.shape == (3, 7)
    assert isinstance(data.index, pd.DatetimeIndex)
    assert data.index[0] == pd.to_datetime("2024-02-02 11:00:00+00:00")
    assert data.iloc[0]["video_id"] == data.iloc[2]["video_id"]
    assert data.iloc[0]["video_id"] != data.iloc[1]["video_id"]
    assert data.iloc[0]["type"] == "watch"
    assert data.iloc[0]["user"] == "user1"
    assert "link" not in data.columns


def test_read_tiktok_search_history():
    data = niimpy.reading.tiktok.search_history(
        config.TIKTOK_USER_DATA_2_PATH,
        user="user1",
    )

    assert data.shape == (1, 9)
    assert data.index[0] == pd.to_datetime("2024-02-02 10:00:00+00:00")
    assert data.iloc[0]["search_term"] == 1
    assert data.iloc[0]["search_term_length"] == 6
    assert data.iloc[0]["search_term_word_count"] == 1


def test_read_tiktok_direct_messages():
    data = niimpy.reading.tiktok.direct_messages(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
    )

    assert data.shape == (5, 14)
    assert data.index[0] == pd.to_datetime("2024-01-02 11:00:00+00:00")
    assert data.iloc[0]["message_type"] == "outgoing"
    assert data.iloc[1]["message_type"] == "incoming"
    assert data.iloc[0]["from"] == 0
    assert data.iloc[1]["to"] == 0
    assert data.iloc[2]["has_url"]
    assert "content" not in data.columns


def test_read_tiktok_comments():
    data = niimpy.reading.tiktok.comments(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
        pseudonymize=False,
    )
    pseudonymized = niimpy.reading.tiktok.comments(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
    )

    assert data.shape == (2, 17)
    assert data.index[0] == pd.to_datetime("2024-01-02 10:00:00+00:00")
    assert data.iloc[0]["message_type"] == "outgoing"
    assert data.iloc[0]["from"] == "sample_user"
    assert data.iloc[0]["target_type"] == "video"
    assert data.iloc[0]["target_id"] == "video-alpha"
    assert data.iloc[0]["to"] == "video-alpha"
    assert data.iloc[0]["character_count"] == 10
    assert data.iloc[0]["word_count"] == 2
    assert data.iloc[1]["target_type"] == "unknown"
    assert pd.isna(data.iloc[1]["target_id"])
    assert pd.isna(data.iloc[1]["to"])
    assert pseudonymized.iloc[0]["from"] == 0
    assert pseudonymized.iloc[0]["target_id"] == pseudonymized.iloc[0]["to"]
    assert pd.isna(pseudonymized.iloc[1]["to"])
    assert "comment" not in data.columns


def test_read_tiktok_likes_favorites_and_posts():
    liked = niimpy.reading.tiktok.liked_videos(config.TIKTOK_USER_DATA_PATH)
    favorites = niimpy.reading.tiktok.favorite_videos(config.TIKTOK_USER_DATA_PATH)
    collections = niimpy.reading.tiktok.favorite_collections(config.TIKTOK_USER_DATA_PATH)
    posts = niimpy.reading.tiktok.posts(config.TIKTOK_USER_DATA_PATH)

    assert liked.shape == (3, 8)
    assert liked.iloc[0]["video_id"] == liked.iloc[2]["video_id"]
    assert liked.iloc[0]["interaction_type"] == "like"
    assert favorites.shape == (2, 8)
    assert favorites.iloc[0]["interaction_type"] == "favorite"
    assert collections.shape == (1, 7)
    assert posts.shape == (1, 23)
    assert posts.iloc[0]["likes"] == 7
    assert posts.iloc[0]["number_of_collections"] == 2
    assert "link" not in posts.columns


def test_read_tiktok_profile_login_and_share_events():
    followers = niimpy.reading.tiktok.followers(config.TIKTOK_USER_DATA_PATH)
    profile_views = niimpy.reading.tiktok.profile_views(config.TIKTOK_USER_DATA_PATH)
    logins = niimpy.reading.tiktok.login_history(config.TIKTOK_USER_DATA_PATH)
    shares = niimpy.reading.tiktok.share_history(config.TIKTOK_USER_DATA_PATH)

    assert followers.shape == (1, 7)
    assert followers.iloc[0]["type"] == "follower"
    assert profile_views.shape == (1, 7)
    assert profile_views.index[0] == pd.to_datetime("2024-01-08 15:00:00+00:00")
    assert logins.shape == (2, 11)
    assert logins.iloc[0]["ip"] == 1
    assert logins.iloc[0]["device_model"] == 1
    assert shares.shape == (2, 9)
    assert shares.iloc[0]["shared_content"] == shares.iloc[1]["shared_content"]
    assert "link" not in shares.columns


def test_read_tiktok_empty_sections():
    assert niimpy.reading.tiktok.watch_history(config.TIKTOK_USER_DATA_PATH).empty
    assert niimpy.reading.tiktok.direct_messages(config.TIKTOK_USER_DATA_2_PATH).empty
    assert niimpy.reading.tiktok.favorite_videos(config.TIKTOK_USER_DATA_2_PATH).empty


def test_read_tiktok_date_filters():
    data = niimpy.reading.tiktok.watch_history(
        config.TIKTOK_USER_DATA_2_PATH,
        start_date=pd.to_datetime("2024-02-02 11:05:00+00:00"),
        end_date=pd.to_datetime("2024-02-02 11:05:00+00:00"),
    )
    assert data.shape[0] == 1
    assert data.index[0] == pd.to_datetime("2024-02-02 11:05:00+00:00")


def test_read_tiktok_metadata():
    summary = niimpy.reading.tiktok.activity_summary(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
    )
    profile = niimpy.reading.tiktok.profile_info(
        config.TIKTOK_USER_DATA_2_PATH,
        user="user1",
    )
    settings = niimpy.reading.tiktok.settings(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
    )

    assert summary.iloc[0]["videoswatchedtotheendsinceaccountregistration"] == 3
    assert profile.iloc[0]["username"] == 1
    assert "platforminfo" not in profile.columns
    assert settings.iloc[0]["app_language"] == "English"


def test_read_tiktok_events():
    data = niimpy.reading.tiktok.events(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
    )

    assert data.shape[0] == 20
    assert data.iloc[0]["type"] == "comment"
    assert set(data["type"]) == {
        "comment", "direct_message", "favorite_collection",
        "favorite_video", "follower", "like", "login", "post",
        "profile_view", "share",
    }
    assert str(data["from"].dtype) == "Int64"
    assert str(data["video_id"].dtype) == "Int64"
    assert str(data["ip"].dtype) == "Int64"
    assert data.loc[pd.Timestamp("2024-01-02 11:00:00", tz="UTC")]["from"] == 0
    assert pd.isna(data.loc[pd.Timestamp("2024-01-02 10:30:00", tz="UTC")]["to"])


def test_read_tiktok_events_raw_ids_are_not_converted():
    data = niimpy.reading.tiktok.events(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
        pseudonymize=False,
    )

    assert data.loc[pd.Timestamp("2024-01-02 11:00:00", tz="UTC")]["from"] == "sample_user"
    assert data.loc[pd.Timestamp("2024-01-02 10:00:00", tz="UTC")]["target_id"] == "video-alpha"


def test_tiktok_direct_messages_with_communication_features():
    data = niimpy.reading.tiktok.direct_messages(
        config.TIKTOK_USER_DATA_PATH,
        user="user1",
    )
    features = {
        comms.message_count: {"resample_args": {"rule": "1D"}},
        comms.message_outgoing_incoming_ratio: {"resample_args": {"rule": "1D"}},
    }
    result = comms.extract_features_comms(data, features=features)

    assert result.loc[pd.Timestamp("2024-01-02", tz="UTC")]["outgoing_count"] == 2
    assert result.loc[pd.Timestamp("2024-01-02", tz="UTC")]["incoming_count"] == 1
    assert result.loc[pd.Timestamp("2024-01-02", tz="UTC")]["outgoing_incoming_ratio"] == 2
