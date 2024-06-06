import numpy as np
import pandas as pd

import niimpy
from niimpy.preprocessing import battery as b
from niimpy.preprocessing import screen as s

group_by_columns = set(["user", "device", "app_group"])


def group_data(df):
    """Group the dataframe by a standard set of columns listed in
    group_by_columns."""
    columns = list(group_by_columns & set(df.columns))
    return df.groupby(columns)


def reset_groups(df):
    """Group the dataframe by a standard set of columns listed in
    group_by_columns."""
    columns = list(group_by_columns & set(df.index.names))
    return df.reset_index(columns)


MAP_APP = {
    "CrossCycle": "sports",
    "Runtastic": "sports",
    "Polar Flow": "sports",
    "Pedometer - Step Counter": "sports",
    "STAMINA-tila": "sports",
    "Fit": "sports",
    "Modo STAMINA": "sports",
    "7 MINUTE WORKOUT": "sports",
    "Moves": "sports",
    "Six Pack in 30 Days": "sports",
    "Bodyweight": "sports",
    "Sports Tracker": "sports",
    "Fit": "sports",
    "Sports Tracker": "sports",
    "Pedometer Step Counter": "sports",
    "MyFitnessPal": "sports",
    "Endomondo": "sports",
    "Health Mate": "sports",
    "Upsi": "sports",
    "Mahjong": "games",
    "Solitaire": "games",
    "Solitaire Collection": "games",
    "Paradise Island 2": "games",
    "Steam": "games",
    "Hidden City": "games",
    "Dokkan Battle": "games",
    "Super Mario Run": "games",
    "Candy Crush Saga": "games",
    "Jeopardy!": "games",
    "Clash Royale": "games",
    "Calcy IV": "games",
    "QuizTaisto PREMIUM": "games",
    "PlayStation": "games",
    "Cleopatra Jewels": "games",
    "DraStic": "games",
    "XCOM": "games",
    "The Secret Society": "games",
    "Pokémon GO": "games",
    "Hearthstone": "games",
    "I Love Hue": "games",
    "Destiny": "games",
    "Castle Cats": "games",
    "Pocket Camp": "games",
    "Hatch": "games",
    "1010!": "games",
    "AirConsole": "games",
    "Sanapala": "games",
    "Head Ball 2": "games",
    "PokÃ©mon GO": "games",
    "Wordfeud FREE": "games",
    "Pyramid Solitaire Saga": "games",
    "Match and Explore": "games",
    "Twitch": "games",
    "Mahjong": "games",
    "Solitaire": "games",
    "Pokémon GO": "games",
    "Game Launcher": "games",
    "Hay Day": "games",
    "State of Survival": "games",
    "Wordfeud Free": "games",
    "Sähköposti": "comm",
    "Gmail": "comm",
    "Puhelin – puheluiden hallinta": "comm",
    "Teléfono": "comm",
    "Email": "comm",
    "Outlook": "comm",
    "Skype": "comm",
    "Romantic love messages": "comm",
    "Dialer": "comm",
    "Discord": "comm",
    "WhatsApp": "comm",
    "Telegram": "comm",
    "Phone": "comm",
    "TelÃ©fono": "comm",
    "Messages": "comm",
    "Messenger Lite": "comm",
    "Puhelin": "comm",
    "Mensajería": "comm",
    "Numerovalitsin": "comm",
    "Messenger": "comm",
    "LINE": "comm",
    "Dual Messenger": "comm",
    "Telegeram": "comm",
    "MensajerÃ­a": "comm",
    "Googlen tekstistä puheeksi -moottori": "comm",
    "LINE Camera": "comm",
    "Signal": "comm",
    "Viber": "comm",
    "Viestit": "comm",
    "Amino": "comm",
    "Fonecta Caller": "comm",
    "ICE - In Case of Emergency": "comm",
    "Orbot": "comm",
    "Puhelu": "comm",
    "Puhelutallennin": "comm",
    "Kuvat": "utility",
    "TikTok": "comm",
    "SÃ¤hkÃ¶posti": "comm",
    "MysticMessenger": "comm",
    "Pinterest": "socialmedia",
    "Tumblr": "socialmedia",
    "Snapchat": "socialmedia",
    "Twitter": "socialmedia",
    "Hootsuite": "socialmedia",
    "We Heart It": "socialmedia",
    "Instagram": "socialmedia",
    "Jodel": "socialmedia",
    "happn": "socialmedia",
    "LinkedIn": "socialmedia",
    "Facebook": "socialmedia",
    "Tinder": "socialmedia",
    "SDP Kansalaispaneeli": "socialmedia",
    "Grindr": "socialmedia",
    "ROMEO UNCUT": "socialmedia",
    "Geo News": "news",
    "Helsingin Sanomat": "news",
    "Yle Areena": "news",
    "Uutisvahti": "news",
    "Flipboard": "news",
    "Kauppalehti": "news",
    "Ilta-Sanomat": "news",
    "Iltalehti": "news",
    "mtv": "news",
    "upday": "news",
    "MTV Uutiset": "news",
    "SÃ¤Ã¤": "news",
    "Weather": "news",
    "Booking.com Hotellit": "travel",
    "Airbnb": "travel",
    "Booking.com": "travel",
    "TripAdvisor": "travel",
    "Couchsurfing": "travel",
    "Bonusway": "travel",
    "TUI Suomi": "travel",
    "Norwegian": "travel",
    "Booking.com": "travel",
    "OPSkin": "shop",
    "Iso Omena": "shop",
    "Lunchie Market": "shop",
    "AliExpress": "shop",
    "Frank App": "shop",
    "Hesburger": "shop",
    "MobilePay": "shop",
    "Zalando": "shop",
    "WeShare": "shop",
    "Wish": "shop",
    "eBay": "shop",
    "Aktia Wallet": "shop",
    "S-mobiili": "shop",
    "Klarna": "shop",
    "PINS": "shop",
    "McDonalds": "shop",
    "K-Ruoka": "shop",
    "Wrapp": "shop",
    "Wolt": "shop",
    "Ticketmaster": "shop",
    "H&M": "shop",
    "EspressoHouse": "shop",
    "ResQ Club": "shop",
    "Momotoko": "shop",
    "Pivo": "shop",
    "Lunchie Market": "shop",
    "EspressoHouse": "shop",
    "Sheets": "work",
    "Slack": "work",
    "My Files": "work",
    "Dropbox": "work",
    "Moodle": "work",
    "Knudge.me": "work",
    "Wilma": "work",
    "Docs": "work",
    "Zoom": "work",
    "Teams": "work",
    "KDE Connect": "work",
    "Linkity Pro": "work",
    "Timely": "work",
    "OneDrive": "work",
    "Uber": "transport",
    "VR Lähijunat": "transport",
    "HSL": "transport",
    "HSL Mobiililippu": "transport",
    "CityTrack": "transport",
    "Podcast Player": "leisure",
    "Samsung Music": "leisure",
    "Google Play Music": "leisure",
    "Shazam": "leisure",
    "Photos": "leisure",
    "Player FM": "leisure",
    "Crowst": "leisure",
    "Leffapeli": "leisure",
    "WEBTOON": "leisure",
    "Tarot Reading": "leisure",
    "Duolingo": "leisure",
    "Crunchyroll": "leisure",
    "SoundHound": "leisure",
    "LiveTulokset": "leisure",
    "Youtify": "leisure",
    "Kuvakaappaus": "leisure",
    "Tarot Universe": "leisure",
    "Norstat": "leisure",
    "Enkeli-tarot": "leisure",
    "Podcast Republic": "leisure",
    "Audiobooks": "leisure",
    "9GAG": "leisure",
    "Netflix": "leisure",
    "Pornhub": "leisure",
    "Musiikki": "leisure",
    "YouTube": "leisure",
    "Imgur": "leisure",
    "Google-sovellus": "leisure",
    "Chrome": "leisure",
    "YouTube Music": "leisure",
    "Peel Remote": "leisure",
    "Music Center": "leisure",
    "SoundCloud": "leisure",
    "Spotify": "leisure",
    "Google Play Musiikki": "leisure",
    "MadLipz": "leisure",
    "HAVEN KBH": "leisure",
    "Internet": "leisure",
    "Podcast Go": "leisure",
    "TuneIn Radio": "leisure",
    "pixiv": "leisure",
    "Pic Collage": "leisure",
    "Radio": "leisure",
    "myTuner Free": "leisure",
    "Audiobooks": "leisure",
    "FaceApp": "leisure",
    "Podcast Republic": "leisure",
    "Libby": "leisure",
    "Headspace": "leisure",
    "BookBeat": "leisure",
    "Edge": "leisure",
    "Google": "leisure",
    "Nextory": "leisure",
    "Android System": "system",
    "Android system": "system",
    "Android-jÃ¤rjestelmÃ¤": "system",
    "Android-sÃ¼steem": "system",
    "Download Manager": "system",
    "JÃ¤rj. UI": "system",
    "KÃ¤yttÃ¶liitt.": "system",
    "Latauksen hallinta": "system",
    "Lataustenhallinta": "system",
    "System UI": "system",
    "OhjelmistopÃ¤ivitys": "system",
    "Optimoija": "system",
    "Avast Mobile Security": "security",
    "Elisa Turvapaketti": "security",
    "F-Secure SAFE": "security",
    "Freedome": "security",
    "Telia Turvapaketti": "security",
    "McAfee Security": "security",
    "Camera": "utility",
    "Clock": "utility",
    "Galleria": "utility",
    "Google Play Kauppa": "utility",
    "Google Play Palvelut": "utility",
    "Google Play Store": "utility",
    "Galaxy Store": "utility",
    "Kalenteri": "utility",
    "Kamera": "utility",
    "Kello": "utility",
    "Kuvat": "utility",
    "Smartâ\\x80\\x8bThings": "utility",
    "Maps": "utility",
    "Samsung capture": "utility",
    "Daylio": "wellbeing",
    "MoMoMood": "wellbeing",
}


def classify_app(df, config):
    """This function is a helper function for other screen preprocessing.
    The function classifies the screen events into the groups specified by group_map.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of screen
        information. Keys can be column names, other dictionaries, etc. It can
        contain a dictionary called group_map, which has the mapping to define
        the app groups. Keys should be the app name, values are the app groups
        (e.g. 'my_app':'my_app_group')

    Returns
    -------
    df: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(config, dict), "config is not a dictionary"

    if not "app_column_name" in config.keys():
        col_name = "application_name"
    else:
        col_name = config["app_column_name"]

    df["app_group"] = "na"
    for key, value in config["group_map"].items():
        df.loc[df[col_name] == key, "app_group"] = value
    return df


def app_count(df, bat, screen, config={}):
    """This function returns the number of times each app group has been used,
    within the specified timeframe. The app groups are defined as a dictionary
    within the config variable. Examples of app groups are social
    media, sports, games, etc. If no mapping is given, a default one will be used.
    If no resampling window is given, the function sets a 30 min default time window. The
    function aggregates the duration by user, by app group, by timewindow.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information. If no data is available, an empty
        dataframe should be passed.
    screen: pandas.DataFrame
        Dataframe with the screen information. If no data is available, an empty
        dataframe should be passed.
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name "" will be used. To include information about
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.

    Returns
    -------
    result: dataframe
        Resulting dataframe
    """

    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(
        screen, pd.DataFrame
    ), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"

    if not "group_map" in config.keys():
        config["group_map"] = MAP_APP
    if not "screen_column_name" in config.keys():
        screen_col_name = "screen_status"
    else:
        screen_col_name = config["screen_column_name"]
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    df2 = classify_app(df, config)

    # Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, config)
        if type(screen.index) == pd.MultiIndex:
            screen.reset_index(inplace=True)
            screen.set_index("index", inplace=True)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=["user", "device", "datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    if screen.empty and not bat.empty:
        shutdown = b.shutdown_info(bat, config)
        shutdown = shutdown.replace([-1, -2], "off")
        if type(shutdown.index) == pd.MultiIndex:
            shutdown.reset_index(inplace=True)
            shutdown.set_index("index", inplace=True)
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=["user", "device", "datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    df2 = df2[["user", "device", "datetime", "app_group", "application_name"]]

    df2.dropna(inplace=True)

    if len(df2) > 0:
        df2["datetime"] = pd.to_datetime(df2["datetime"])
        df2.set_index("datetime", inplace=True)
        result = group_data(df2)["app_group"].resample(**config["resample_args"], include_groups=False).count()
        result = pd.DataFrame(result).rename(columns={"app_group": "count"})
        result = reset_groups(result)

        return result
    return None


def app_duration(df, bat, screen, config=None):
    """This function returns the duration of use of different app groups, within the
    specified timeframe. The app groups are defined as a dictionary within the
    config variable. Examples of app groups are social media, sports,
    games, etc. If no mapping is given, a default one will be used.
    If no resampling window is given, the function sets a 30 min default time window. The
    function aggregates the duration by user, by app group, by timewindow.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information. If no data is available, an empty
        dataframe should be passed.
    screen: pandas.DataFrame
        Dataframe with the screen information. If no data is available, an empty
        dataframe should be passed.
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name "application_name" will be used. To include information about
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.

    Returns
    -------
    result: dataframe
        Resulting dataframe
    """

    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(
        screen, pd.DataFrame
    ), "Please input data as a pandas DataFrame type"
    assert isinstance(config, dict), "config is not a dictionary"

    if not "group_map" in config.keys():
        config["group_map"] = MAP_APP
    if not "resample_args" in config.keys():
        config["resample_args"] = {"rule":"30min"}
    
    outlier_threshold = config.get("outlier_threshold", "10h")

    df2 = classify_app(df, config)

    # Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, config)
        if type(screen.index) == pd.MultiIndex:
            screen.reset_index(inplace=True)
            screen.set_index("index", inplace=True)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=["user", "device", "datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    if screen.empty and not bat.empty:
        shutdown = b.shutdown_info(bat, config)
        shutdown = shutdown.replace([-1, -2], "off")
        if type(shutdown.index) == pd.MultiIndex:
            shutdown.reset_index(inplace=True)
            shutdown.set_index("index", inplace=True)
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=["user", "device", "datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    df2 = df2[["user", "device", "time", "datetime", "app_group"]]

    # Fill in time gap between app foreground session
    def resample_group(group):
        rule = config["resample_args"]["rule"]

        all_times = pd.date_range(
            start=group.index.min().round(rule),
            end=group.index.max().ceil(rule),
            freq=rule,
        )

        new_df = pd.DataFrame(index=all_times)
        resampled_group = group.join(new_df, how="outer").ffill()
        resampled_group["datetime"] = resampled_group.index
        return resampled_group

    # Apply resampling to each group
    df2 = df2.groupby(["user", "device"]).apply(resample_group, include_groups=False).reset_index(["user", "device"])

    df2["duration"] = np.nan
    df2["duration"] = df2["datetime"].diff()
    df2["duration"] = df2["duration"].shift(-1)

    # Filter outliers by duration. Default threshold is 10 hours.
    outlier_threshold = pd.Timedelta(outlier_threshold)
    df2 = df2[~(df2.duration > outlier_threshold)]
    df2["duration"] = df2["duration"].dt.total_seconds()
    df2 = df2[~(df2.duration <= 0)]
    
    df2.dropna(inplace=True)

    if len(df2) > 0:
        df2["datetime"] = pd.to_datetime(df2["datetime"])
        df2.set_index("datetime", inplace=True)
        result = group_data(df2)["duration"].resample(**config["resample_args"], include_groups=False).sum()
        result = pd.DataFrame(result).rename(columns={"app_group": "count"})
        return reset_groups(result)

    return None


ALL_FEATURES = [globals()[name] for name in globals() if name.startswith("app_")]
ALL_FEATURES = {x: {} for x in ALL_FEATURES}


def extract_features_app(df, bat, screen, features=None):
    """This function computes and organizes the selected features for application
    events. The function aggregates the features by user, by app group,
    by time window. If no time window is specified, it will automatically aggregate
    the features in 30 mins non-overlapping windows. If no group_map is provided,
    a default one will be used.

    The complete list of features that can be calculated are: app_count, and
    app_duration.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    features: dict, optional
        Dictionary keys contain the names of the features to compute.
        If none is given, all features will be computed.

    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"

    if features is None:
        features = ALL_FEATURES
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"

    computed_features = []
    for feature, feature_arg in features.items():
        print(f"computing {feature}...")
        computed_feature = feature(df, bat, screen, feature_arg)
        index_by = list(group_by_columns & set(computed_feature.columns))
        computed_feature = computed_feature.set_index(index_by, append=True)
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)
    # index the result only by the original index (datetime)
    computed_features = reset_groups(computed_features)
    return computed_features
