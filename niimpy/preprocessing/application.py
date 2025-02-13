import numpy as np
import pandas as pd

from niimpy.preprocessing import battery as b
from niimpy.preprocessing import screen as s
from niimpy.preprocessing import util


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


def classify_app(df, app_column_name = "application_name", group_map = MAP_APP, **kwargs):
    """This function is a helper function for other screen preprocessing.
    The function classifies the screen events into the groups specified by group_map.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of screen
        information. The following arguments are used:

        app_column_name: Column containing the app name. Defaults to 'application_name'.
        group_map: A dictionary mapping the app names to app groups. (required)
                   (e.g. 'my_app':'my_app_group')

    Returns
    -------
    df: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."

    df["app_group"] = "na"
    for key, value in group_map.items():
        df.loc[df[app_column_name] == key, "app_group"] = value
    return df


def app_count(df, bat=None, screen=None, group_map = MAP_APP, resample_args = {"rule":"30min"}, **kwargs):
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
    bat: pandas.DataFrame, optional
        Dataframe with the battery information. If no data is available, an empty
        dataframe should be passed.
    screen: pandas.DataFrame, optional
        Dataframe with the screen information. If no data is available, an empty
        dataframe should be passed.
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of screen
        information. The following arguments are used:

        app_column_name: Column containing the app name. Defaults to 'application_name'.
        group_map: A dictionary mapping the app names to app groups.
                   Defaults to niimpy.preprocesing.application.MAP_APP, which maps
                   several common apps.
        screen_column_name: Column containing the screen status. Defaults to 'screen_status'.
        resample_args: parameteres passed to pandas.DataFrame.resample. Defaults to {'rule':'30min'}.
        
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """

    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    bat = util.ensure_dataframe(bat)
    screen = util.ensure_dataframe(screen)
    
    df2 = classify_app(df, group_map = group_map, **kwargs)

    # Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, **kwargs)
        if type(screen.index) == pd.MultiIndex:
            screen.reset_index(inplace=True)
            screen.set_index("index", inplace=True)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=["user", "device", "datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    if screen.empty and not bat.empty:
        shutdown = b.shutdown_info(bat, **kwargs)
        shutdown = shutdown.replace([-1, -2], "off")
        if type(shutdown.index) == pd.MultiIndex:
            shutdown.reset_index(inplace=True)
            shutdown.set_index("index", inplace=True)
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=["user", "device", "datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    keep_columns = list(set(["user", "device", "group"]) & set(df.columns))
    df2 = df2[keep_columns+["datetime", "app_group", "application_name"]]

    df2.dropna(inplace=True)

    if len(df2) > 0:
        df2["datetime"] = pd.to_datetime(df2["datetime"])
        df2.set_index("datetime", inplace=True)
        result = util.group_data(df2, "app_group")["app_group"].resample(**resample_args, include_groups=False).count()
        result = pd.DataFrame(result).rename(columns={"app_group": "count"})
        result = util.reset_groups(result, "app_group")
        result = util.select_columns(result, ["app_group", "count"])
        return result
    
    return None


def app_duration(df, bat=None, screen=None, group_map = MAP_APP, resample_args = {"rule":"30min"}, outlier_threshold = "10h", **kwargs):
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
    bat: pandas.DataFrame, optional
        Dataframe with the battery information. If no data is available, an empty
        dataframe should be passed.
    screen: pandas.DataFrame, optional
        Dataframe with the screen information. If no data is available, an empty
        dataframe should be passed.
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. The following arguments are used:

        app_column_name: Column containing the app name. Defaults to 'application_name'.
        group_map: A dictionary mapping the app names to app groups.
                   Defaults to niimpy.preprocesing.application.MAP_APP, which maps
                   several common apps.
        outlier_threshold: Threshold for filtering out outliers. Defaults to '10h'.

    Returns
    -------
    result: dataframe
        Resulting dataframe
    """

    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    bat = util.ensure_dataframe(bat)
    screen = util.ensure_dataframe(screen)
    niimpy_cols = list(set(["group", "user", "device"]) & set(df.columns))

    df2 = classify_app(df, group_map = group_map, **kwargs)

    # Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, **kwargs)
        if type(screen.index) == pd.MultiIndex:
            screen.reset_index(inplace=True)
            screen.set_index("index", inplace=True)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=niimpy_cols + ["datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    if screen.empty and not bat.empty:
        shutdown = b.shutdown_info(bat, **kwargs)
        shutdown = shutdown.replace([-1, -2], "off")
        if type(shutdown.index) == pd.MultiIndex:
            shutdown.reset_index(inplace=True)
            shutdown.set_index("index", inplace=True)
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=niimpy_cols + ["datetime"], inplace=True)
        df2.fillna({"app_group": "off"}, inplace=True)

    keep_columns = list(set(["group", "user", "device"]) & set(df.columns))
    df2 = df2[keep_columns+["time", "datetime", "app_group"]]

    # Fill in time gap between app foreground session
    def resample_group(group):
        rule = resample_args["rule"]

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
    df2 = util.group_data(df2).apply(resample_group, include_groups=False)
    df2 = util.reset_groups(df2)
    print(df2.shape)

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
        result = util.group_data(df2, "app_group")["duration"].resample(**resample_args, include_groups=False).sum()
        result = pd.DataFrame(result).rename(columns={"app_group": "count"})
        df2 = util.reset_groups(result, "app_group")
        df2 = util.select_columns(df2, ["app_group", "duration"])
        return df2

    return None


ALL_FEATURES = [globals()[name] for name in globals() if name.startswith("app_")]
ALL_FEATURES = {x: {} for x in ALL_FEATURES}


def extract_features_app(df, bat=None, screen=None, features=None):
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
    bat = util.ensure_dataframe(bat)
    screen = util.ensure_dataframe(screen)

    if features is None:
        features = ALL_FEATURES
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"

    computed_features = []
    for feature, feature_arg in features.items():
        computed_feature = feature(df, bat, screen, **feature_arg)
        computed_feature = util.set_conserved_index(computed_feature, "app_group")
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)
    # index the result only by the original index (datetime)
    computed_features = util.reset_groups(computed_features, "app_group")
    return computed_features
