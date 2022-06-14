import numpy as np
import pandas as pd

import niimpy
from niimpy.preprocessing import battery as b

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

def classify_app(df, answer_col, id_map):
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(answer_col, str), "answer_col is not a string."
    assert isinstance(id_map, dict), "id_map is not a dictionary."
    
    df['app_group'] = 'na'
    for key,value in id_map.items():
        df.app_group[df['application_name'] == key]=value
    return df

def app_count(df, bat, feature_functions=None):
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "battery_shutdown" in feature_functions.keys():
        feature_functions['battery_shutdown'] = None
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    

#Application
def app_duration(database,subject,begin=None,end=None,app_list_path=None):
    
    if(app_list_path==None):
        app_list_path = '/m/cs/scratch/networks-nima/ana/niima-code/Datastreams/Phone/apps_group.csv'


    app = app.drop(columns=['device','user','time','defaults','sound','vibrate'])
    
    #Classify the apps into groups
    app_list=pd.read_csv(app_list_path)
    app['group']=np.nan
    for index, row in app.iterrows():
        group=app_list.isin([row['application_name']]).any()
        group=group.reset_index()
        if (not any(group[0])):
            app.loc[index,'group']=10
        else:
            app.loc[index,'group']=group.index[group[0] == True].tolist()[0]

    # TODO: Split those missing data imputation methods to another function
    #Insert missing data due to phone being shut down
    shutdown = battery.shutdown_info(database,subject,begin,end)
    if not shutdown.empty:
        shutdown['group']=11
        shutdown['battery_status'] = 'off'
        app = app.merge(shutdown, how='outer', left_index=True, right_index=True)
        app['application_name'] = app['application_name'].replace(np.nan, 'off', regex=True)
        app['group_x'] = app['group_x'].replace(np.nan, 11, regex=True)
        app = app.drop(['battery_status','group_y'], axis=1)
        dates=app.datetime_x.combine_first(app.datetime_y)
        app['datetime']=dates
        app = app.drop(['datetime_x','datetime_y'], axis=1)
        app=app.rename(columns={'group_x':'group'})

    #Insert missing data due to the screen being off
    screen=screen_off(database,subject,begin,end)
    if not screen.empty:
        app = app.merge(screen, how='outer', left_index=True, right_index=True)
        app['application_name'] = app['application_name'].replace(np.nan, 'off', regex=True)
        app['group'] = app['group'].replace(np.nan, 11, regex=True)
        del app['screen_status']
        dates=app.datetime_x.combine_first(app.datetime_y)
        app['datetime']=dates
        app = app.drop(['datetime_x','datetime_y'], axis=1)


    #Calculate the app duration per group
    app['duration']=np.nan
    app['duration']=app['datetime'].diff()
    app['duration'] = app['duration'].shift(-1)

    app['datetime'] = app['datetime'].dt.floor('d')
    duration=pd.pivot_table(app,values='duration',index='datetime', columns='group', aggfunc=np.sum)
    count=pd.pivot_table(app,values='duration',index='datetime', columns='group', aggfunc='count')
    duration.columns = duration.columns.map({0.0: 'sports', 1.0: 'games', 2.0: 'communication', 3.0: 'social_media', 4.0: 'news', 5.0: 'travel', 6.0: 'shop', 7.0: 'entretainment', 8.0: 'work_study', 9.0: 'transportation', 10.0: 'other', 11.0: 'off'})
    count.columns = count.columns.map({0.0: 'sports', 1.0: 'games', 2.0: 'communication', 3.0: 'social_media', 4.0: 'news', 5.0: 'travel', 6.0: 'shop', 7.0: 'entretainment', 8.0: 'work_study', 9.0: 'transportation', 10.0: 'other', 11.0: 'off'})
    duration = duration.apply(get_seconds,axis=1)
    return duration, count
