import niimpy
import niimpy.preprocessing.application as app
from niimpy import config
import pytest

# read sample data
data = niimpy.read_csv(config.SINGLEUSER_AWARE_APP_PATH, tz="Europe/Helsinki")
screen = niimpy.read_csv(config.MULTIUSER_AWARE_SCREEN_PATH, tz="Europe/Helsinki")
battery = niimpy.read_csv(config.MULTIUSER_AWARE_BATTERY_PATH, tz="Europe/Helsinki")


def test_app_features():
    # TEST 1
    data["group"] = "group1"
    screen["group"] = "group1"
    battery["group"] = "group1"
    test = app.extract_features_app(data, battery, screen, features=None)
    data["extra_column"] = "extra"

    user_comm = test[(test["user"] == "dvWdLQesv21a") & (test["app_group"] == "comm")]
    user_work = test[(test["user"] == "dvWdLQesv21a") & (test["app_group"] == "work")]
    assert user_comm.loc["2019-08-05 14:00:00+03:00"]["count"] == 2
    assert user_work.loc["2019-08-06 04:00:00+03:00"]["count"] == 1
    assert user_comm.loc["2019-08-05 14:00:00+03:00"]["duration"] == pytest.approx(
        594.99
    )
    assert user_work.loc["2019-08-06 04:00:00+03:00"]["duration"] == pytest.approx(
        778.0
    )

    # TEST 2
    features = {
        app.app_count: {
            "app_column_name": "application_name",
            "screen_column_name": "screen_status",
            "resample_args": {"rule": "2h"},
        },
        app.app_duration: {"resample_args": {"rule": "1h"}},
    }
    test = app.extract_features_app(data, battery, screen, features=features)
    user_comm = test[(test["user"] == "dvWdLQesv21a") & (test["app_group"] == "comm")]
    user_work = test[(test["user"] == "dvWdLQesv21a") & (test["app_group"] == "work")]

    #assert user_comm.loc["2019-08-05 20:00:00+03:00"]["group"] == "group1"
    assert user_comm.loc["2019-08-05 20:00:00+03:00"]["count"] == 3
    assert user_work.loc["2019-08-06 04:00:00+03:00"]["count"] == 2
    assert user_comm.loc["2019-08-05 20:00:00+03:00"]["duration"] == 3569.00
    assert user_work.loc["2019-08-06 04:00:00+03:00"]["duration"] == 2578
    assert "extra_column" not in test.columns
