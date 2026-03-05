import pandas as pd
import pytest

from niimpy.reading import google_portability


START_DATE = "2024-02-01"
END_DATE = "2024-02-28"


# ── youtube_history ──────────────────────────────────────────────

class TestYoutubeHistory:

    def test_basic_read(self, google_portability_zip):
        """All records have subtitles (realistic data). Currently crashes."""
        df = google_portability.youtube_history(google_portability_zip)
        assert len(df) == 3
        assert "url" in df.columns
        assert "video_id" in df.columns
        assert "channel_name" in df.columns
        assert "channel_url" in df.columns
        assert "action" in df.columns
        assert "header" not in df.columns
        assert "products" not in df.columns
        assert (df["platform"] == "YouTube").all()
        # video_id extraction
        assert df.iloc[0]["video_id"] == "dQw4w9WgXcQ"
        assert df.iloc[1]["video_id"] == "abc123def45"
        assert pd.isna(df.iloc[2]["video_id"])  # post URL, no v= param
        # action extraction
        assert df.iloc[0]["action"] == "Watched"
        assert df.iloc[1]["action"] == "Liked"
        assert df.iloc[2]["action"] == "Viewed"
        # title after stripping action (and preposition if present)
        assert df.iloc[0]["title"] == "Test Video Alpha"
        assert df.iloc[1]["title"] == "Test Video Beta"
        assert df.iloc[2]["title"] == "Test Post Gamma"
        # channel info from subtitles
        assert df.iloc[0]["channel_name"] == "Channel Alpha"
        assert df.iloc[1]["channel_url"] == "https://www.youtube.com/channel/UC_beta"
        # activityControls flattened to string
        assert "YouTube watch history" in df.iloc[0]["activityControls"]

    def test_no_subtitles(self, google_portability_no_subtitles_zip):
        """YouTube data without subtitles field. Currently crashes."""
        df = google_portability.youtube_history(google_portability_no_subtitles_zip)
        assert len(df) == 3
        assert "url" in df.columns
        assert "video_id" in df.columns
        assert "action" in df.columns
        assert "header" not in df.columns
        assert "products" not in df.columns
        assert (df["platform"] == "YouTube").all()
        assert df.iloc[0]["video_id"] == "dQw4w9WgXcQ"
        assert df.iloc[0]["action"] == "Watched"
        assert df.iloc[0]["title"] == "Test Video Alpha"

    def test_start_date(self, google_portability_zip):
        df = google_portability.youtube_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_end_date(self, google_portability_zip):
        df = google_portability.youtube_history(google_portability_zip, end_date=END_DATE)
        assert len(df) == 2

    def test_both_dates(self, google_portability_zip):
        df = google_portability.youtube_history(
            google_portability_zip, start_date=START_DATE, end_date=END_DATE
        )
        assert len(df) == 1

    def test_start_date_no_subtitles(self, google_portability_no_subtitles_zip):
        df = google_portability.youtube_history(google_portability_no_subtitles_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_end_date_no_subtitles(self, google_portability_no_subtitles_zip):
        df = google_portability.youtube_history(google_portability_no_subtitles_zip, end_date=END_DATE)
        assert len(df) == 2

    def test_both_dates_no_subtitles(self, google_portability_no_subtitles_zip):
        df = google_portability.youtube_history(
            google_portability_no_subtitles_zip, start_date=START_DATE, end_date=END_DATE
        )
        assert len(df) == 1

    def test_missing_data(self, empty_portability_zip):
        df = google_portability.youtube_history(empty_portability_zip)
        assert df.empty


# ── discover_history ─────────────────────────────────────────────

class TestDiscoverHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.discover_history(google_portability_zip)
        assert len(df) == 3
        assert (df["platform"] == "Discover").all()
        assert (df["type"] == "history").all()
        assert "header" not in df.columns
        assert "products" not in df.columns
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_start_date(self, google_portability_zip):
        df = google_portability.discover_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_end_date(self, google_portability_zip):
        df = google_portability.discover_history(google_portability_zip, end_date=END_DATE)
        assert len(df) == 2

    def test_both_dates(self, google_portability_zip):
        df = google_portability.discover_history(
            google_portability_zip, start_date=START_DATE, end_date=END_DATE
        )
        assert len(df) == 1

    def test_missing_data(self, empty_portability_zip):
        df = google_portability.discover_history(empty_portability_zip)
        assert df.empty


# ── discover_liked_content ───────────────────────────────────────

class TestDiscoverLikedContent:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.discover_liked_content(google_portability_zip)
        assert len(df) == 3
        assert "content_url" in df.columns
        assert "liked_date" in df.columns
        assert (df["platform"] == "Discover").all()
        assert (df["subtype"] == "liked_content").all()
        assert (df["type"] == "liked").all()
        assert df.iloc[0]["content_url"] == "https://example.com/content1"

    def test_start_date(self, google_portability_zip):
        df = google_portability.discover_liked_content(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_end_date(self, google_portability_zip):
        df = google_portability.discover_liked_content(google_portability_zip, end_date=END_DATE)
        assert len(df) == 2

    def test_missing_data(self, empty_portability_zip):
        df = google_portability.discover_liked_content(empty_portability_zip)
        assert df.empty


# ── discover_follows ─────────────────────────────────────────────

class TestDiscoverFollows:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.discover_follows(google_portability_zip)
        assert len(df) == 3
        assert "followed_entity" in df.columns
        assert (df["platform"] == "Discover").all()
        assert (df["type"] == "follows").all()
        assert df.iloc[0]["followed_entity"] == "Entity Alpha"

    def test_missing_data(self, empty_portability_zip):
        df = google_portability.discover_follows(empty_portability_zip)
        assert df.empty


# ── discover_not_interested_settings ─────────────────────────────

class TestDiscoverNotInterestedSettings:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.discover_not_interested_settings(google_portability_zip)
        assert len(df) == 3
        assert "entity_name" in df.columns
        assert "setting_value" in df.columns
        assert (df["platform"] == "Discover").all()
        assert (df["type"] == "not_interested").all()
        assert df.iloc[0]["entity_name"] == "test topic one"
        assert df.iloc[1]["setting_value"] == "NOT_PREFERRED"

    def test_no_timestamp(self, google_portability_zip):
        df = google_portability.discover_not_interested_settings(google_portability_zip)
        assert df.index.isna().all()

    def test_missing_data(self, empty_portability_zip):
        df = google_portability.discover_not_interested_settings(empty_portability_zip)
        assert df.empty


# ── discover (composite) ────────────────────────────────────────

class TestDiscover:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.discover(google_portability_zip)
        # 3 history + 3 liked + follows (broken parsing but returns rows) + 3 not_interested
        assert len(df) >= 9
        assert (df["platform"] == "Discover").all()

    def test_date_filter(self, google_portability_zip):
        df = google_portability.discover(
            google_portability_zip, start_date=START_DATE, end_date=END_DATE
        )
        # Sub-functions filter their own data. Follows and not_interested have no
        # timestamps so their rows pass through unfiltered, then discover() re-converts.
        assert len(df) >= 2

    def test_empty_zip(self, empty_portability_zip):
        # All sub-functions return empty -> pd.concat([]) raises ValueError
        with pytest.raises(ValueError):
            google_portability.discover(empty_portability_zip)


# ── chrome_history ───────────────────────────────────────────────

class TestChromeHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.chrome_history(google_portability_zip)
        assert not df.empty
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_missing_data(self, empty_portability_zip):
        df = google_portability.chrome_history(empty_portability_zip)
        assert df.empty


# ── google_lens_history ──────────────────────────────────────────

class TestGoogleLensHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.google_lens_history(google_portability_zip)
        assert len(df) == 3
        assert (df["platform"] == "Google Lens").all()
        assert (df["type"] == "google_lens").all()
        assert "header" not in df.columns
        assert "products" not in df.columns

    def test_start_date(self, google_portability_zip):
        df = google_portability.google_lens_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_end_date(self, google_portability_zip):
        df = google_portability.google_lens_history(google_portability_zip, end_date=END_DATE)
        assert len(df) == 2

    def test_missing_data_raises(self, empty_portability_zip):
        with pytest.raises(KeyError):
            google_portability.google_lens_history(empty_portability_zip)


# ── google_play_games_history ────────────────────────────────────

class TestGooglePlayGamesHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.google_play_games_history(google_portability_zip)
        assert len(df) == 3
        assert (df["platform"] == "Google Play Games").all()
        assert (df["type"] == "play_games").all()

    def test_start_date(self, google_portability_zip):
        df = google_portability.google_play_games_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_end_date(self, google_portability_zip):
        df = google_portability.google_play_games_history(google_portability_zip, end_date=END_DATE)
        assert len(df) == 2

    def test_missing_data_raises(self, empty_portability_zip):
        with pytest.raises(KeyError):
            google_portability.google_play_games_history(empty_portability_zip)


# ── google_play_store_history ────────────────────────────────────

class TestGooglePlayStoreHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.google_play_store_history(google_portability_zip)
        assert len(df) == 3
        assert (df["platform"] == "Google Play Store").all()
        assert (df["type"] == "play_store").all()

    def test_start_date(self, google_portability_zip):
        df = google_portability.google_play_store_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_missing_data_raises(self, empty_portability_zip):
        with pytest.raises(KeyError):
            google_portability.google_play_store_history(empty_portability_zip)


# ── image_search_history ─────────────────────────────────────────

class TestImageSearchHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.image_search_history(google_portability_zip)
        assert len(df) == 3
        assert (df["platform"] == "Image Search").all()
        assert (df["type"] == "image_search").all()
        assert "header" not in df.columns
        assert "products" not in df.columns

    def test_start_date(self, google_portability_zip):
        df = google_portability.image_search_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_missing_data_raises(self, empty_portability_zip):
        with pytest.raises(KeyError):
            google_portability.image_search_history(empty_portability_zip)


# ── video_search_history ─────────────────────────────────────────

class TestVideoSearchHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.video_search_history(google_portability_zip)
        assert len(df) == 3
        assert (df["platform"] == "Video Search").all()
        assert (df["type"] == "video_search").all()
        assert "url" in df.columns
        assert "video_id" in df.columns
        # YouTube URLs get video_id extracted
        assert df.iloc[0]["video_id"] == "c2myHZYqlPM"
        assert df.iloc[1]["video_id"] == "f5lfqI0mzRE"
        # Non-YouTube URL: no video_id
        assert pd.isna(df.iloc[2]["video_id"])

    def test_start_date(self, google_portability_zip):
        df = google_portability.video_search_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_missing_data_raises(self, empty_portability_zip):
        with pytest.raises(KeyError):
            google_portability.video_search_history(empty_portability_zip)


# ── search_history ───────────────────────────────────────────────

class TestSearchHistory:

    def test_basic_read(self, google_portability_zip):
        df = google_portability.search_history(google_portability_zip)
        assert len(df) == 3
        assert (df["platform"] == "Search").all()
        assert (df["type"] == "search").all()
        # search_history does NOT drop header/products
        assert "header" in df.columns
        assert "products" in df.columns

    def test_start_date(self, google_portability_zip):
        df = google_portability.search_history(google_portability_zip, start_date=START_DATE)
        assert len(df) == 2

    def test_end_date(self, google_portability_zip):
        df = google_portability.search_history(google_portability_zip, end_date=END_DATE)
        assert len(df) == 2

    def test_missing_data_raises(self, empty_portability_zip):
        with pytest.raises(KeyError):
            google_portability.search_history(empty_portability_zip)


# ── Schema compliance (xfail) ───────────────────────────────────

_READERS = [
    google_portability.discover_history,
    google_portability.chrome_history,
    google_portability.google_lens_history,
    google_portability.google_play_games_history,
    google_portability.google_play_store_history,
    google_portability.image_search_history,
    google_portability.video_search_history,
    google_portability.search_history,
]


@pytest.mark.parametrize("reader_fn", _READERS)
def test_schema_datetime_index(google_portability_zip, reader_fn):
    df = reader_fn(google_portability_zip)
    assert isinstance(df.index, pd.DatetimeIndex)


def test_schema_datetime_index_youtube(google_portability_no_subtitles_zip):
    """Separate test for youtube since main zip triggers subtitles bug."""
    df = google_portability.youtube_history(google_portability_no_subtitles_zip)
    assert isinstance(df.index, pd.DatetimeIndex)
