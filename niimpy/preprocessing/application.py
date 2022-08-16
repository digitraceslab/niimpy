import numpy as np
import pandas as pd

import niimpy
from niimpy.preprocessing import battery as b
from niimpy.preprocessing import screen as s

MAP_APP = {'CrossCycle':'sports',
             'Runtastic':'sports',
             'Polar Flow':'sports',
             'Pedometer - Step Counter':'sports',
             'STAMINA-tila':'sports',
             'Fit':'sports',
             'Modo STAMINA':'sports',
             '7 MINUTE WORKOUT':'sports',
             'Moves':'sports',
             'Six Pack in 30 Days':'sports',
             'Bodyweight':'sports',
             'Sports Tracker':'sports',
             'Fit':'sports',
             'Sports Tracker':'sports',
             'Pedometer Step Counter':'sports',
             'MyFitnessPal':'sports',

            'Mahjong':'games',
            'Solitaire':'games',
            'Solitaire Collection':'games',
            'Paradise Island 2':'games',
            'Steam':'games',
            'Hidden City':'games',
            'Dokkan Battle':'games',
            'Super Mario Run':'games',
            'Candy Crush Saga':'games',
            'Jeopardy!':'games',
            'Clash Royale':'games',
            'Calcy IV':'games',
            'QuizTaisto PREMIUM':'games',
            'PlayStation':'games',
            'Cleopatra Jewels':'games',
            'DraStic':'games',
            'XCOM':'games',
            'The Secret Society':'games',
            'Pokémon GO':'games',
            'Hearthstone':'games',
            'I Love Hue':'games',
            'Destiny':'games',
            'Castle Cats':'games',
            'Pocket Camp':'games',
            'Hatch':'games',
            '1010!':'games',
            'AirConsole':'games',
            'Sanapala':'games',
            'Head Ball 2':'games',
            'PokÃ©mon GO':'games',
            'Wordfeud FREE':'games',
            'Pyramid Solitaire Saga':'games',
            'Match and Explore':'games',
            'Twitch':'games',
            'Mahjong':'games',
            'Solitaire':'games',
            'Pokémon GO':'games',

            'Sähköposti':'comm',
            'Gmail':'comm',
            'Puhelin – puheluiden hallinta':'comm',
            'Teléfono':'comm',
            'Email':'comm',
            'Outlook':'comm',
            'Skype':'comm',
            'Romantic love messages':'comm',
            'Dialer':'comm',
            'Discord':'comm',
            'WhatsApp':'comm',
            'Telegram':'comm',
            'Phone':'comm',
            'TelÃ©fono':'comm',
            'Messages':'comm',
            'Messenger Lite':'comm',
            'Puhelin':'comm',
            'Mensajería':'comm',
            'Numerovalitsin':'comm',
            'Messenger':'comm',
            'LINE':'comm',
            'Dual Messenger':'comm',
            'Telegeram':'comm',
            'MensajerÃ­a':'comm',
            'Googlen tekstistä puheeksi -moottori':'comm',
            'LINE Camera':'comm',
            'Signal':'comm',
            'Viber':'comm',
            'Viestit':'comm',

            'Pinterest':'socialmedia',
            'Tumblr':'socialmedia',
            'Snapchat':'socialmedia',
            'Twitter':'socialmedia',
            'Hootsuite':'socialmedia',
            'We Heart It':'socialmedia',
            'Instagram':'socialmedia',
            'Jodel':'socialmedia',
            'happn':'socialmedia',
            'LinkedIn':'socialmedia',
            'Facebook':'socialmedia',
            'Tinder':'socialmedia',
            'SDP Kansalaispaneeli':'socialmedia',

            'Geo News':'news',
            'Helsingin Sanomat':'news',
            'Yle Areena':'news',
            'Uutisvahti':'news',
            'Flipboard':'news',
            'Kauppalehti':'news',
            'Ilta-Sanomat':'news',
            'Iltalehti':'news',
        
            'Booking.com Hotellit':'travel',
            'Airbnb':'travel',
            'Booking.com':'travel',
            'TripAdvisor':'travel',
            'Couchsurfing':'travel',
            'Bonusway':'travel',
            'TUI Suomi':'travel',
            'Norwegian':'travel',
            'Booking.com':'travel',

            'OPSkin':'shop',
            'Iso Omena':'shop',
            'Lunchie Market':'shop',
            'AliExpress':'shop',
            'Frank App':'shop',
            'Hesburger':'shop',
            'MobilePay':'shop',
            'Zalando':'shop',
            'WeShare':'shop',
            'Wish':'shop',
            'eBay':'shop',
            'Aktia Wallet':'shop',
            'S-mobiili':'shop',
            'Klarna':'shop',
            'PINS':'shop',
            'McDonalds':'shop',
            'K-Ruoka':'shop',
            'Wrapp':'shop',
            'Wolt':'shop',
            'Ticketmaster':'shop',
            'H&M':'shop',
            'EspressoHouse':'shop',
            'ResQ Club':'shop',
            'Momotoko':'shop',
            'Pivo':'shop',
            'Lunchie Market':'shop',
            'EspressoHouse':'shop',

            'Sheets':'work',
            'Slack':'work',
            'My Files':'work',
            'Dropbox':'work',
            'Moodle':'work',
            'Knudge.me':'work',
            'Wilma':'work',
            'Docs':'work',
            'Zoom':'work',
            'Teams':'work',

            'Uber':'transport',
            'VR Lähijunat':'transport',
            'HSL':'transport',
            'HSL Mobiililippu':'transport',
            'CityTrack':'transport',

            'Podcast Player':'leisure',
            'Samsung Music':'leisure',
            'Google Play Music':'leisure',
            'Shazam':'leisure',
            'Photos':'leisure',
            'Player FM':'leisure',
            'Crowst':'leisure',
            'Leffapeli':'leisure',
            'WEBTOON':'leisure',
            'Tarot Reading':'leisure',
            'Duolingo':'leisure',
            'Crunchyroll':'leisure',
            'SoundHound':'leisure',
            'LiveTulokset':'leisure',
            'Youtify':'leisure',
            'Kuvakaappaus':'leisure',
            'Tarot Universe':'leisure',
            'Norstat':'leisure',
            'Enkeli-tarot':'leisure',
            'Podcast Republic':'leisure',
            'Audiobooks':'leisure',
            '9GAG':'leisure',
            'Netflix':'leisure',
            'Pornhub':'leisure',
            'Musiikki':'leisure',
            'YouTube':'leisure',
            'Imgur':'leisure',
            'Google-sovellus':'leisure',
            'Chrome':'leisure',
            'YouTube Music':'leisure',
            'Peel Remote':'leisure',
            'Music Center':'leisure',
            'SoundCloud':'leisure',
            'Spotify':'leisure',
            'Google Play Musiikki':'leisure',
            'MadLipz':'leisure',
            'HAVEN KBH':'leisure',
            'Internet':'leisure',
            'Podcast Go':'leisure',
            'TuneIn Radio':'leisure',
            'pixiv':'leisure',
            'Pic Collage':'leisure',
            'Radio':'leisure',
            'myTuner Free':'leisure',
            'Audiobooks':'leisure',
            'FaceApp':'leisure',
            'Podcast Republic':'leisure',
            'Libby':'leisure',
            'Headspace':'leisure'}

def classify_app(df, feature_functions):
    """ This function is a helper function for other screen preprocessing.
    The function classifies the screen events into the groups specified by group_map. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    feature_functions: dict, optional
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "app_column_name" in feature_functions.keys():
        col_name = "application_name"
    else:
        col_name = feature_functions["app_column_name"]
    
    df['app_group'] = 'na'
    for key,value in feature_functions["group_map"].items():
        df.app_group[df[col_name] == key]=value
    return df

def app_count(df, bat, screen, feature_functions=None):
    """ This function returns the number of times each app group has been used, 
    within the specified timeframe. The app groups are defined as a dictionary 
    within the feature_functions variable. Examples of app groups are social 
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
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """    
    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(screen, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "group_map" in feature_functions.keys():
        feature_functions['group_map'] = MAP_APP
    if not "screen_column_name" in feature_functions.keys():
        screen_col_name = "screen_status"
    else:
        screen_col_name = feature_functions["screen_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    df2 = classify_app(df, feature_functions)

    #Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, feature_functions)
        if type(screen.index)==pd.MultiIndex:
            screen.reset_index(inplace=True) 
            screen.set_index("index", inplace=True)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2 = df2[['user', 'device', 'time','datetime', 'app_group']]
    
    if (screen.empty and not bat.empty):
        shutdown = b.shutdown_info(bat, feature_functions)
        shutdown = shutdown.replace([-1,-2],'off')
        if type(shutdown.index)==pd.MultiIndex:
            shutdown.reset_index(inplace=True) 
            shutdown.set_index("index", inplace=True)
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2 = df2[['user', 'device', 'time','datetime', 'app_group']]
        
    if (screen.empty and bat.empty):
        df2 = df2[['user', 'device', 'time','datetime', 'app_group']]
    
    df2.dropna(inplace=True)
    
    if len(df2)>0:
        df2['datetime'] = pd.to_datetime(df2['datetime'])
        df2.set_index('datetime', inplace=True)
        result = df2.groupby(["user","app_group"]).resample(**feature_functions["resample_args"]).count()
        result.rename(columns={"device": "count"}, inplace=True)
        result = result["count"].to_frame()
        
    return result

def app_duration(df, bat, screen, feature_functions=None):
    """ This function returns the duration of use of different app groups, within the 
    specified timeframe. The app groups are defined as a dictionary within the 
    feature_functions variable. Examples of app groups are social media, sports,
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
    feature_functions: dict, optional
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """      
    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(screen, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "group_map" in feature_functions.keys():
        feature_functions['group_map'] = MAP_APP
    if not "screen_column_name" in feature_functions.keys():
        screen_col_name = "screen_status"
    else:
        screen_col_name = feature_functions["screen_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
    
    df2 = classify_app(df, feature_functions)

    #Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, feature_functions)
        if type(screen.index)==pd.MultiIndex:
            screen.reset_index(inplace=True) 
            screen.set_index("index", inplace=True)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2 = df2[['user', 'device', 'time','datetime', 'app_group']]
    
    if (screen.empty and not bat.empty):
        shutdown = b.shutdown_info(bat, feature_functions)
        shutdown = shutdown.replace([-1,-2],'off')
        if type(shutdown.index)==pd.MultiIndex:
            shutdown.reset_index(inplace=True) 
            shutdown.set_index("index", inplace=True)
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2 = df2[['user', 'device', 'time','datetime', 'app_group']]
    
    if (screen.empty and bat.empty):
        df2 = df2[['user', 'device', 'time','datetime', 'app_group']]
    
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    #Discard any datapoints whose duration are than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~(df2.duration>thr)]
    df2 = df2[~(df2.duration>thr)]
    df2["duration"] = df2["duration"].dt.total_seconds()
    
    df2.dropna(inplace=True)
    
    if len(df2)>0:
        df2['datetime'] = pd.to_datetime(df2['datetime'])
        df2.set_index('datetime', inplace=True)
        result = df2.groupby(["user","app_group"])["duration"].resample(**feature_functions["resample_args"]).sum()
        
    return result

ALL_FEATURE_FUNCTIONS = [globals()[name] for name in globals() if name.startswith('app_')]
ALL_FEATURE_FUNCTIONS = {x: {} for x in ALL_FEATURE_FUNCTIONS}

def extract_features_app(df, bat, screen, features=None):
    """ This function computes and organizes the selected features for application
    events that have been recorded using Aware Framework. The function aggregates 
    the features by user, by app group, by time window. If no time window is 
    specified, it will automatically aggregate the features in 30 mins non-
    overlapping windows. If no group_map is provided, a default one will be used. 
    
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
        features = ALL_FEATURE_FUNCTIONS
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        print(f'computing {feature}...')
        computed_feature = feature(df, bat, screen, feature_arg)
        computed_features.append(computed_feature)
        
    computed_features = pd.concat(computed_features, axis=1)
    return computed_features