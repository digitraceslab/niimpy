import numpy as np
import pandas as pd

import niimpy
from niimpy.preprocessing import battery as b
from niimpy.preprocessing import screen as s

APP_GROUP = {'CrossCycle':'sports',
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

def classify_app(df, group_map):
    """ This function is a helper function for other screen preprocessing.
    The function classifies the screen events into the groups specified by group_map. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    group_map: dict
        Mapping to define the app groups. Keys should be the app name, values are
        the app groups (e.g. 'my_app':'my_app_group')
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(group_map, dict), "group_map is not a dictionary."
    
    df['app_group'] = 'na'
    for key,value in group_map.items():
        df.app_group[df['application_name'] == key]=value
    return df

def extract_features_screen(df, group_map=None, features=None):
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
    group_map: dict
        Mapping to define the app groups. Keys should be the app name, values are
        the app groups (e.g. 'my_app':'my_app_group')
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
        features = [key for key in globals().keys() if key.startswith('app_')]
        features = {x: {} for x in features}
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        print(f'computing {feature}...')
        command = f'{feature}(df,feature_functions=feature_arg)'
        computed_feature = eval(command)
        computed_features.append(computed_feature)
        
    computed_features = pd.concat(computed_features, axis=1)
    return computed_features


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
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
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
        feature_functions['group_map'] = APP_GROUP
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = classify_app(df, feature_functions['group_map'])
    feature_functions.pop('group_map', None) #no need for this argumetn anymore

    #Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, feature_functions)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2.drop(['sound', 'screen_status', 'vibrate'], axis=1, inplace=True)
    
    if (screen.empty and not bat.empty):
        shutdown = b.shutdown_info(bat)
        shutdown = shutdown.replace([-1,-2],'off')
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2.drop(['battery_level', 'battery_status', 'battery_health', 'battery_adaptor'], axis=1, inplace=True)
    
    if len(df2)>0:
        result = df2.groupby(["user","app_group"]).resample(**feature_functions).count()
        result = result["device"].to_frame()
        result = result.reset_index()
        result.rename(columns={"level_2": "datetime", "device": "count"}, inplace=True)
        result = result.set_index('datetime')
        
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
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
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
        feature_functions['group_map'] = APP_GROUP
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = classify_app(df, feature_functions['group_map'])
    feature_functions.pop('group_map', None) #no need for this argumetn anymore

    #Insert missing data due to the screen being off or battery depleated
    if not screen.empty:
        screen = s.screen_off(screen, bat, feature_functions)
        df2 = pd.concat([df2, screen])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2.drop(['sound', 'screen_status', 'vibrate'], axis=1, inplace=True)
    
    if (screen.empty and not bat.empty):
        shutdown = b.shutdown_info(bat)
        shutdown = shutdown.replace([-1,-2],'off')
        df2 = pd.concat([df2, shutdown])
        df2.sort_values(by=["user","device","datetime"], inplace=True)
        df2["app_group"].fillna('off', inplace=True)
        df2.drop(['battery_level', 'battery_status', 'battery_health', 'battery_adaptor'], axis=1, inplace=True)
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    #Discard any datapoints whose duration are than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~(df2.duration>thr)]
    df2 = df2[~(df2.duration>thr)]
    
    if len(df2)>0:
        result = df2.groupby(["user","app_group"])["duration"].resample(**feature_functions).sum()
        result = result.reset_index()
        result.rename(columns={"level_2": "datetime"}, inplace=True)
        result = result.set_index('datetime')
        
    return result