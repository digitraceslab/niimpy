################################################################################
# This is the main file for preprocessing smartphone sensor data               #
#                                                                              #
# Contributors: Anna Hakala & Ana Triana                                       #
################################################################################

import niimpy
import numpy as np
import pandas as pd
from pandas import Series
import matplotlib.pyplot as plt
import seaborn as sns
import time
import datetime
import pytz
import niimpy.aalto

# backwards compatibility aliases
from .screen import screen_off, screen_duration


def date_range(df, begin, end):
    """Extract out a certain date range from a DataFrame.

    Extract out a certain data range from a dataframe.  The index must be the
    dates, and the index must be sorted.
    """
    # TODO: is this needed?  Do normal pandas operation, timestamp
    # checking is not really needed (and limits the formats that can
    # be used, pandas can take more than pd.Timestamp)
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = df.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = df.index[-1]

    df_new = df.loc[begin:end]
    return df_new


# Above this point is function that should *stay* in preprocess.py
# Below this is functions that may or may not be moved.


def get_subjects(database):
    """ Returns a list of the subjects in the database

        Parameters
        ----------
        database: database

    """
    # TODO: deprecate, user should do ['user'].unique() on dataframe themselves
    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"

    questions = database.raw(table='AwareHyksConverter', user=niimpy.ALL)
    subjects=list(questions.user.unique())
    return subjects

def get_phq9(database,subject):
    """ Returns the phq9 scores from the databases per subject

    Parameters
    ----------
    database: database
    user: string

    Returns
    -------
    phq9: Dataframe with the phq9 score

    """
    # TODO: Most of this logic can be moved to sum_survey_cores
    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    phq9 = niimpy.aalto.phq9_raw(database)
    phq9 = phq9[phq9['user']==subject]
    phq9 = phq9.drop(['user','source'],axis=1)
    phq9 = phq9.sort_index()
    phq9 = phq9.reset_index().drop_duplicates(subset=['index','id'],keep='first').set_index('index')
    phq9 = phq9.groupby(phq9.index)['answer'].sum()
    phq9 = phq9.to_frame()

    return phq9

#surveys
def daily_affect_variability(questions, subject=None):
    """ Returns two DataFrames corresponding to the daily affect variability and
    mean daily affect, both measures defined in the OLO paper available in
    10.1371/journal.pone.0110907. In brief, the mean daily affect computes the
    mean of each of the 7 questions (e.g. sad, cheerful, tired) asked in a
    likert scale from 0 to 7. Conversely, the daily affect viariability computes
    the standard deviation of each of the 7 questions.

    NOTE: This function aggregates data by day.

    Parameters
    ----------
    questions: DataFrame with subject data (or database for backwards compatibility)
    subject: string, optional (backwards compatibility only, in the future do filtering before).

    Returns
    -------
    DLA_mean: mean of the daily affect
    DLA_std: standard deviation of the daily affect
    """
    # TODO: The daily summary (mean/std) seems useful, can we generalize?
    # Backwards compatibilty if a database was passed
    if isinstance(questions, niimpy.database.Data1):
        questions = questions.raw(table='AwareHyksConverter', user=subject)
    # Maintain backwards compatibility in the case subject was passed and
    # questions was *not* a dataframe.
    elif isinstance(subject, string):
        questions = questions[questions['user'] == subject]

    questions=questions[(questions['id']=='olo_1_1') | (questions['id']=='olo_1_2') | (questions['id']=='olo_1_3') | (questions['id']=='olo_1_4') | (questions['id']=='olo_1_5') | (questions['id']=='olo_1_6') | (questions['id']=='olo_1_7') | (questions['id']=='olo_1_8')]
    questions['answer']=pd.to_numeric(questions['answer'])
    questions = questions.drop(['device', 'time', 'user'], axis=1)

    if (pd.Timestamp.tzname(questions.index[0]) != 'EET'):
        if pd.Timestamp.tzname(questions.index[0]) != 'EEST':
            questions.index = pd.to_datetime(questions.index).tz_localize('Europe/Helsinki')

    questions=questions.drop_duplicates(subset=['datetime','id'],keep='first')
    questions=questions.pivot_table(index='datetime', columns='id', values='answer')
    questions=questions.rename(columns={'olo_1_1': 'cheerful', 'olo_1_2': 'tired','olo_1_3': 'content', 'olo_1_4': 'nervous','olo_1_5': 'tranquil', 'olo_1_6': 'sad', 'olo_1_7': 'excited', 'olo_1_8': 'active'})
    questions = questions.reset_index()

    DLA = questions.copy()
    questions['date_minus_time'] = questions['datetime'].apply( lambda questions : datetime.datetime(year=questions.year, month=questions.month, day=questions.day))
    questions.set_index(questions["date_minus_time"],inplace=True)
    DLA_std = questions.resample('D').std()#), how='std')
    DLA_std=DLA_std.rename(columns={'date_minus_time': 'datetime'})
    DLA_std.index = pd.to_datetime(DLA_std.index).tz_localize('Europe/Helsinki')

    DLA_mean = questions.resample('D').mean()
    DLA_mean=DLA_mean.rename(columns={'date_minus_time': 'datetime'})
    DLA_mean.index = pd.to_datetime(DLA_mean.index).tz_localize('Europe/Helsinki')
    return DLA_std, DLA_mean

#Ambient Noise
def ambient_noise(noise, subject, begin=None, end=None):
    """ Returns a Dataframe with 5 possible computations regarding the noise
    ambient plug-in: average decibels, average frequency, number of times when
    there was noise in the day, number of times when there was a loud noise in
    the day (>70dB), and number of times when the noise matched the speech noise
    level and frequency (65Hz < freq < 255Hz and dB>50 )



    NOTE: This function aggregates data by day.

    Parameters
    ----------
    noise: DataFrame with subject data (or database for backwards compatibility)
    subject: string, optional (backwards compatibility only, in the future do filtering before).
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    avg_noise: Dataframe

    """
    # TODO: move to niimpy.noise
    # TODO: add arguments for frequency/decibels/silence columns
    # Backwards compatibilty if a database was passed
    if isinstance(noise, niimpy.database.Data1):
        noise = noise.raw(table='AwareAmbientNoise', user=subject)
    # Maintain backwards compatibility in the case subject was passed and
    # questions was *not* a dataframe.
    elif isinstance(subject, string):
        noise = noise[noise['user'] == subject]

    # Shrink the dataframe down to only what we need
    noise = noise[['double_frequency', 'is_silent', 'double_decibels', 'datetime']]

    # Extract the data range (In the future should be done before this function
    # is called.)
    if begin is not None or end is not None:
        noise = date_range(noise, begin, end)

    noise['is_silent']=pd.to_numeric(noise['is_silent'])

    loud = noise[noise.double_decibels>70] #check if environment was noisy
    speech = noise[noise['double_frequency'].between(65, 255)]
    speech = speech[speech.is_silent==0] #check if there was a conversation
    silent=noise[noise.is_silent==0] #This is more what moments there are noise in the environment.
    avg_noise=noise.resample('D', on='datetime').mean() #average noise
    avg_noise=avg_noise.drop(['is_silent'],axis=1)

    if not silent.empty:
        silent=silent.resample('D', on='datetime').count()
        silent = silent.drop(['double_decibels','double_frequency','datetime'],axis=1)
        silent=silent.rename(columns={'is_silent':'noise'})
        avg_noise = avg_noise.merge(silent, how='outer', left_index=True, right_index=True)

    if not loud.empty:
        loud=loud.resample('D', on='datetime').count()
        loud = loud.drop(['double_decibels','double_frequency','datetime'],axis=1)
        loud=loud.rename(columns={'is_silent':'loud'})
        avg_noise = avg_noise.merge(loud, how='outer', left_index=True, right_index=True)

    if not speech.empty:
        speech=speech.resample('D', on='datetime').count()
        speech = speech.drop(['double_decibels','double_frequency','datetime'],axis=1)
        speech=speech.rename(columns={'is_silent':'speech'})
        avg_noise = avg_noise.merge(speech, how='outer', left_index=True, right_index=True)

    return avg_noise

#Application
def shutdown_info(database,subject,begin=None,end=None):
    """ Returns a DataFrame with the timestamps of when the phone has shutdown.


    NOTE: This is a helper function created originally to preprocess the application
    info data

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    shutdown: Dataframe

    """
    bat = niimpy.read._get_dataframe(database, table='AwareBattery', user=subject)
    bat = niimpy.filter_dataframe(bat, begin=begin, end=end)
    # TODO: move to niimpy.battery

    if 'datetime' in bat.columns:
        bat = bat[['battery_status', 'datetime']]
    else:
        bat = bat[['battery_status']]
    bat=bat.loc[begin:end]
    bat['battery_status']=pd.to_numeric(bat['battery_status'])
    shutdown = bat[bat['battery_status'].between(-3, 0, inclusive=False)]
    return shutdown


def get_seconds(time_delta):
    """ Converts the timedelta to seconds


    NOTE: This is a helper function

    Parameters
    ----------
    time_delta: Timedelta

    """

    return time_delta.dt.seconds

def app_duration(database,subject,begin=None,end=None,app_list_path=None):
    """ Returns two DataFrames contanining the duration and number of events per
    group of apps, e.g. number of times a person used communication apps like
    WhatsApp, Telegram, Messenger, sms, etc. and for how long these apps were
    used in a day (in seconds).

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional
    app_list_path: path to the csv file where the apps are classified into groups


    Returns
    -------
    duration: Dataframe
    count: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    app = database.raw(table='AwareApplicationNotifications', user=subject)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = app.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = app.iloc[len(app)-1]['datetime']
    if(app_list_path==None):
        app_list_path = '/m/cs/scratch/networks-nima/ana/niima-code/Datastreams/Phone/apps_group.csv'


    app = app.drop(columns=['device','user','time','defaults','sound','vibrate'])
    app=app.loc[begin:end]

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

    #Insert missing data due to phone being shut down
    shutdown = shutdown_info(database,subject,begin,end)
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

    #Insert missing data caught by sms but unknown cause
    sms = database.raw(table='AwareMessages', user=subject)
    sms = sms.drop(columns=['device','user','time','trace'])
    sms = sms.drop_duplicates(subset=['datetime','message_type'],keep='first')
    sms = sms[sms.message_type=='outgoing']
    sms = sms.loc[begin:end]
    if not sms.empty:
        app = app.merge(sms, how='outer', left_index=True, right_index=True)
        app['application_name'] = app['application_name'].replace(np.nan, 'sms', regex=True)
        app['group'] = app['group'].replace(np.nan, 2, regex=True)
        del app['message_type']
        dates=app.datetime_x.combine_first(app.datetime_y)
        app['datetime']=dates
        app = app.drop(['datetime_x','datetime_y'], axis=1)

    #Insert missing data caught by calls but unknown cause
    call = database.raw(table='AwareCalls', user=subject)
    if not call.empty:
        call = call.drop(columns=['device','user','time','trace'])
        call = call.drop_duplicates(subset=['datetime','call_type'],keep='first')
        call['call_duration'] = pd.to_timedelta(call.call_duration.astype(int), unit='s')
        call = call.loc[begin:end]
        dummy = call.datetime+call.call_duration
        dummy = pd.Series.to_frame(dummy)
        dummy['finish'] = dummy[0]
        dummy = dummy.set_index(0)
        call = call.merge(dummy, how='outer', left_index=True, right_index=True)
        dates=call.datetime.combine_first(call.finish)
        call['datetime']=dates
        call = call.drop(columns=['call_duration','finish'])
        app = app.merge(call, how='outer', left_index=True, right_index=True)
        app.group = app.group.fillna(2)
        app.application_name = app.application_name.fillna('call')
        dates=app.datetime_x.combine_first(app.datetime_y)
        app['datetime']=dates
        app = app.drop(columns=['datetime_x','datetime_y','call_type'])

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

#Communication
def call_info(database,subject,begin=None,end=None):
    """ Returns a DataFrame contanining the duration and number of events per
    type of calls (outgoing, incoming, missed). The Dataframe summarizes the
    duration of the incoming/outgoing calls in seconds, number of those events,
    and how long (in seconds) the person has spoken to the top 5 contacts (most
    frequent)

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    duration: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    call = database.raw(table='AwareCalls', user=subject)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = call.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = call.iloc[len(call)-1]['datetime']

    call = call.drop(columns=['device','user','time'])
    call = call.loc[begin:end]
    call['datetime'] = call['datetime'].dt.floor('d')
    call['call_duration']=pd.to_numeric(call['call_duration'])
    duration = call.groupby(['datetime']).sum()

    missed_calls = call.loc[(call['call_type'] == 'missed')].groupby(['datetime']).count()
    outgoing_calls = call.loc[(call['call_type'] == 'outgoing')].groupby(['datetime']).count()
    incoming_calls = call.loc[(call['call_type'] == 'incoming')].groupby(['datetime']).count()
    duration['call_missed'] = missed_calls['call_type']
    duration['call_outgoing'] = outgoing_calls['call_type']
    duration['call_incoming'] = incoming_calls['call_type']
    duration2 = call.pivot_table(index='datetime', columns='call_type', values='call_duration',aggfunc='sum')
    if ('incoming' in duration2.columns):
        duration2 = duration2.rename(columns={'incoming': 'call_incoming_duration'})
    if ('outgoing' in duration2.columns):
        duration2 = duration2.rename(columns={'outgoing': 'call_outgoing_duration'})
    if ('missed' in duration2.columns):
        duration2 = duration2.drop(columns=['missed'])
    duration = duration.merge(duration2, how='outer', left_index=True, right_index=True)
    duration = duration.fillna(0)
    if ('missed_y' in duration.columns):
        duration =  duration.drop(columns=['missed_y'])
    #duration.columns = ['total_call_duration', 'call_missed', 'call_outgoing', 'call_incoming', 'call_incoming_duration', 'call_outgoing_duration']

    #Now let's calculate something more sophisticated... Let's see
    trace = call.groupby(['trace']).count()
    trace = trace.sort_values(by=['call_type'], ascending=False)
    top5 = trace.index.values.tolist()[:5]
    call['frequent']=0
    call = call.reset_index()
    call = call.rename(columns={'index': 'date'})
    for index, row in call.iterrows():
        if (call.loc[index,'trace'] in top5):
            call.loc[index,'frequent']=1
    call['frequent'] = call['frequent'].astype(str)
    duration2 = call.pivot_table(index='date', columns=['call_type','frequent'], values='call_duration',aggfunc='sum')
    duration2.columns = ['_'.join(col) for col in duration2.columns]
    duration2 = duration2.reset_index()

    #duration2.columns = ['datetime','incoming_0','incoming_1','missed_0','missed_1','outgoing_0','outgoing_1']
    duration2['datetime'] = duration2['date'].dt.floor('d')
    duration2 = duration2.groupby(['datetime']).sum()
    if ('incoming_0' in duration2.columns):
        duration2 = duration2.drop(columns=['incoming_0'])
    if ('missed_0' in duration2.columns):
        duration2 = duration2.drop(columns=['missed_0'])
    if ('missed_1' in duration2.columns):
        duration2 = duration2.drop(columns=['missed_1'])
    if ('outgoing_0' in duration2.columns):
        duration2 = duration2.drop(columns=['outgoing_0'])
    duration = duration.merge(duration2, how='outer', left_index=True, right_index=True)
    duration = duration.rename(columns={'incoming_1': 'incoming_duration_top5', 'outgoing_1': 'outgoing_duration_top5'})
    return duration

def sms_info(database,subject,begin=None,end=None):
    """ Returns a DataFrame contanining the number of events per type of messages
    SMS (outgoing, incoming). The Dataframe summarizes the number of the
    incoming/outgoing sms and how many of those correspond to the top 5 contacts
    (most frequent with whom the subject exchanges texts)

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    sms_stats: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    sms = database.raw(table='AwareMessages', user=subject)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = sms.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = sms.iloc[len(sms)-1]['datetime']


    sms = sms.drop(columns=['device','user','time'])
    sms['datetime'] = sms['datetime'].dt.floor('d')
    sms = sms.loc[begin:end]
    if (len(sms)>0):
        sms_stats = sms.copy()
        sms_stats['dummy'] = 1
        sms_stats = sms_stats.pivot_table(index='datetime', columns='message_type', values='dummy',aggfunc='sum')

        #Now let's move to somethign more sophisticated
        trace = sms.groupby(['trace']).count()
        trace = trace.sort_values(by=['message_type'], ascending=False)
        top5 = trace.index.values.tolist()[:5]
        sms['frequent']=0
        sms = sms.reset_index()
        sms = sms.rename(columns={'index': 'date'})
        for index, row in sms.iterrows():
            if (sms.loc[index,'trace'] in top5):
                sms.loc[index,'frequent']=1
                sms['frequent'] = sms['frequent'].astype(str)
                sms['dummy']=1
        dummy = sms.pivot_table(index='date', columns=['message_type','frequent'], values='dummy',aggfunc='sum')
        dummy.columns = ['_'.join(col) for col in dummy.columns]
        dummy = dummy.reset_index()
        dummy['datetime'] = dummy['date'].dt.floor('d')
        dummy = dummy.groupby(['datetime']).sum()
        if ('incoming_0' in dummy.columns):
            dummy = dummy.drop(columns=['incoming_0'])
        if ('outgoing_0' in dummy.columns):
            dummy = dummy.drop(columns=['outgoing_0'])
        sms_stats = sms_stats.merge(dummy, how='outer', left_index=True, right_index=True)
        sms_stats = sms_stats.rename(columns={'incoming_1': 'sms_incoming_top5', 'outgoing_1': 'sms_outgoing_top5'})
        sms_stats = sms_stats.fillna(0)
        if ('incoming' in sms_stats.columns):
            sms_stats = sms_stats.rename(columns={'incoming': 'sms_incoming'})
        if ('outgoing' in sms_stats.columns):
            sms_stats = sms_stats.rename(columns={'outgoing': 'sms_outgoing'})
        return sms_stats
    else:
        sms_stats = pd.DataFrame()
        return sms_stats

def sms_duration(database,subject,begin,end):
    """ Returns a DataFrame contanining the duration per type of messages SMS
    (outgoing, incoming). The Dataframe summarizes the calculated duration of
    the incoming/outgoing sms and the lags (i.e. the period between receiving a
    message and reading/writing a reply).


    NOTE: The foundation of this function is still weak and needs discussion

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    reading: Dataframe
    writing: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    app = database.raw(table='AwareApplicationNotifications', user=subject)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = app.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = app.iloc[len(app)-1]['datetime']

    app = app.drop(columns=['device','user','time','defaults','sound','vibrate'])

    #Insert missing data due to phone being shut down
    shutdown = shutdown_info(database,subject,begin,end)
    shutdown=shutdown.rename(columns={'battery_status':'application_name'})
    shutdown['application_name'] = 'off'
    app = app.merge(shutdown, how='outer', left_index=True, right_index=True)
    app['application_name_x'] = app['application_name_x'].replace(np.nan, 'off', regex=True)
    del app['application_name_y']
    dates=app.datetime_x.combine_first(app.datetime_y)
    app['datetime']=dates
    app = app.drop(['datetime_x','datetime_y'],axis=1)
    app=app.rename(columns={'application_name_x':'application_name'})

    #Insert missing data due to the screen being off
    screen=screen_off(database,subject,begin,end)
    app = app.merge(screen, how='outer', left_index=True, right_index=True)
    app['application_name'] = app['application_name'].replace(np.nan, 'off', regex=True)
    del app['screen_status']
    dates=app.datetime_x.combine_first(app.datetime_y)
    app['datetime']=dates
    app = app.drop(['datetime_x','datetime_y'],axis=1)
    app = app.drop_duplicates(subset=['datetime','application_name'],keep='first')

    #Insert missing data caught by sms but unknown cause
    sms = database.raw(table='AwareMessages', user=subject)
    sms = sms.drop(columns=['device','user','time','trace'])
    sms = sms.drop_duplicates(subset=['datetime','message_type'],keep='first')
    #sms = sms[sms.message_type=='outgoing']
    app = app.merge(sms, how='outer', left_index=True, right_index=True)
    app.loc[app['application_name'].isnull(),'application_name'] = app['message_type']
    del app['message_type']
    dates=app.datetime_x.combine_first(app.datetime_y)
    app['datetime']=dates
    app = app.drop(['datetime_x','datetime_y'],axis=1)

    #Calculate the app duration
    app['duration']=np.nan
    app['duration']=app['datetime'].diff()
    app['duration'] = app['duration'].shift(-1)
    #Select the text applications only
    sms_app_name = ['Messages','Mensajería','MensajerÃ­a','Viestit','incoming','outgoing']
    app = app[app['application_name'].isin(sms_app_name)]
    sms_app_name = ['Messages','Mensajería','MensajerÃ­a','Viestit']
    app['application_name'].loc[(app['application_name'].isin(sms_app_name))] = 'messages'
    app['group']=np.nan
    for i in range(len(app)-1):
        if (app.application_name[i]=='incoming' and app.application_name[i+1]=='messages'):
            app.group[i+1]=1
        elif (app.application_name[i]=='messages' and app.application_name[i+1]=='outgoing'):
            app.group[i+1]=2
        else:
            app.group[i+1]=0
    app['lags'] = app['datetime'].diff()
    app['datetime'] = app['datetime'].dt.floor('d')
    app=app.loc[begin:end]
    reading = app.loc[(app['group']==1)]
    if (len(reading)>0):
        reading = pd.pivot_table(reading,values=['duration','lags'],index='datetime', columns='application_name', aggfunc=np.sum)
        reading.columns = ['reading_duration','reading_lags']
        reading = reading.apply(get_seconds,axis=1)
    writing = app.loc[(app['group']==2)]
    if (len(writing)>0):
        for i in range(len(writing)-1):
            if (writing.lags[i].seconds<15 or writing.lags[i].seconds>120):
                writing.lags[i] = datetime.datetime.strptime('00:05', "%M:%S") - datetime.datetime.strptime("00:00", "%M:%S")
        del writing['duration']
        writing = writing.rename(columns={'lags':'writing_duration'})
        writing = pd.pivot_table(writing,values='writing_duration',index='datetime', columns='application_name', aggfunc=np.sum)
        writing = writing.apply(get_seconds,axis=1)
    return reading, writing

def communication_info(database,subject,begin=None,end=None):
    """ Returns a DataFrame contanining all the information extracted from
    communication's events (calls, sms, and communication apps like WhatsApp,
    Telegram, Messenger, etc.). Regarding calls, this function contains the
    duration of the incoming/outgoing calls in seconds, number of those events,
    and how long (in seconds) the person has spoken to the top 5 contacts (most
    frequent). Regarding the SMSs, this function contains the number of incoming
    /outgoing events, and the top 5 contacts (most frequent). Aditionally, we
    also include the calculated duration of the incoming/outgoing sms and the
    lags (i.e. the period between receiving a message and reading/writing a
    reply). Regarding the app, the duration of communication events is summarized.

    This function also sums all the different durations (calls, SMSs, apps) and
    provides the duration (in seconds) that a person spent communicating during
    the day.

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    call_summary: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    app = database.raw(table='AwareApplicationNotifications', user=subject)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = app.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = app.iloc[len(app)-1]['datetime']

    duration_app, count_app = app_duration(database,subject,begin,end)
    call_summary = call_info(database,subject,begin,end)
    sms_summary = sms_info(database,subject,begin,end)
    #reading, writing = sms_duration(database,subject,begin,end)

    if (not sms_summary.empty):
        call_summary = call_summary.merge(sms_summary, how='outer', left_index=True, right_index=True)
        call_summary = call_summary.fillna(0)

    #Now let's see if there is any info from the apps worth bringin back
    if ('communication' in duration_app.columns): #2 is the number for communication apps
        comm_app = duration_app['communication']#.dt.seconds
        comm_app = comm_app.fillna(0)
        comm_app = comm_app.to_frame()
    if ('social_media' in duration_app.columns): #2 is the number for communication apps
        social_app = duration_app['social_media']#.dt.seconds
        social_app = social_app.fillna(0)
        social_app = social_app.to_frame()
    try:
        social_app
        try:
            comm_app
            comm_app = comm_app.merge(social_app, how='outer', left_index=True, right_index=True)
        except NameError:
            comm_app = social_app
    except NameError:
        pass
    try:
        comm_app
        call_summary = call_summary.merge(comm_app, how='outer', left_index=True, right_index=True)
    except NameError:
        pass
    call_summary = call_summary.fillna(0)

    if ('communication' in call_summary.columns):
        call_summary['total_comm_duration'] = call_summary['call_duration']+call_summary['communication']
    if (('social_media' in call_summary.columns) and ('communication' in call_summary.columns)):
        call_summary['total_comm_duration'] = call_summary['call_duration']+call_summary['social_media']+call_summary['communication']
    if ('communication' in call_summary.columns):
        call_summary=call_summary.rename(columns={'communication':'comm_apps_duration'})
    if ('social_media' in call_summary.columns):
        call_summary=call_summary.rename(columns={'social_media':'social_apps_duration'})

    #Now let's see if there is any info from the sms duration
    '''if (len(reading)>0):
        reading['reading_duration'] = reading['reading_duration']#.dt.seconds
        reading['reading_lags'] = reading['reading_lags']#.dt.seconds
        call_summary = call_summary.merge(reading, how='outer', left_index=True, right_index=True)
        call_summary = call_summary.fillna(0)
        call_summary['total_comm_duration'] = call_summary['total_comm_duration']+call_summary['reading_duration']
    if (len(writing)>0):
        writing=writing.rename(columns={'outgoing':'writing_duration'})
        writing['writing_duration'] = writing['writing_duration']#.dt.seconds
        call_summary = call_summary.merge(writing, how='outer', left_index=True, right_index=True)
        call_summary = call_summary.fillna(0)
        call_summary['total_comm_duration'] = call_summary['total_comm_duration']+call_summary['writing_duration']'''
    return call_summary

#Occurrences
def occurrence_call_sms(database,subject,begin=None,end=None):
    """ Returns a DataFrame contanining the number of events that occur in a
    day for call and sms. The events are binned in 12-minutes, i.e. if there is
    an event at 11:05 and another one at 11:45, 2 occurences happened in one
    hour. Then, the sum of these occurences yield the number per day.

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    event: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    call = database.raw(table='AwareCalls', user=subject)
    if not call.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = call.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = call.iloc[len(call)-1]['datetime']
        call = call.drop(columns=['device','user','time'])
        call = call.loc[begin:end]

    sms = database.raw(table='AwareMessages', user=subject)
    if not sms.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = call.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = call.iloc[len(call)-1]['datetime']
        sms = sms.drop(columns=['device','user','time'])
        sms = sms.loc[begin:end]

    if not call.empty:
        if not sms.empty:
            call_sms = call.merge(sms, how='outer', left_index=True, right_index=True)
            times = pd.DatetimeIndex.to_series(call_sms.index,keep_tz=True)
        else:
            times = pd.DatetimeIndex.to_series(call.index,keep_tz=True)
    if not sms.empty:
        if not call.empty:
            call_sms = sms.merge(call, how='outer', left_index=True, right_index=True)
            times = pd.DatetimeIndex.to_series(call_sms.index,keep_tz=True)
        else:
            times = pd.DatetimeIndex.to_series(sms.index,keep_tz=True)

    event=niimpy.util.occurrence(times)
    event = event.groupby(['day']).sum()
    event = event.drop(columns=['hour'])
    return event

def occurrence_call_sms_apps(database,subject,begin=None,end=None,app_list_path=None,comm_app_list_path=None):
    """ Returns a DataFrame contanining the number of events that occur in a
    day for calls, sms, and communication apps. The events are binned in
    12-minutes, i.e. if there is an event at 11:05 and another one at 11:45, 2
    occurences happened in one hour. Then, the sum of these occurences yield the
    number per day.

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional
    app_list_path: path to the file where the apps are classified into groups
    comm_app_list_path:path to the file where the communication apps are listed


    Returns
    -------
    event: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    call = database.raw(table='AwareCalls', user=subject)
    if not call.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = call.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = call.iloc[len(call)-1]['datetime']
        call = call.drop(columns=['device','user','time'])
        call = call.loc[begin:end]

    sms = database.raw(table='AwareMessages', user=subject)
    if not sms.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = sms.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = sms.iloc[len(sms)-1]['datetime']
        sms = sms.drop(columns=['device','user','time'])
        sms = sms.loc[begin:end]

    app = database.raw(table='AwareApplicationNotifications', user=subject)
    if (app_list_path==None):
        app_list_path='/m/cs/scratch/networks-nima/ana/niima-code/Datastreams/Phone/apps_group.csv'
    if (comm_app_list_path==None):
        comm_app_list_path='/m/cs/scratch/networks-nima/ana/niima-code/Datastreams/Phone/comm_apps.csv'

    if not app.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = app.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = app.iloc[len(app)-1]['datetime']
        app = app.drop(columns=['device','user','time','defaults','sound','vibrate'])
        app = app.loc[begin:end]

        app_list=pd.read_csv(app_list_path)
        app['group']=np.nan
        for index, row in app.iterrows():
            group=app_list.isin([row['application_name']]).any()
            group=group.reset_index()
            if (not any(group[0])):
                app.loc[index,'group']=10
            else:
                app.loc[index,'group']=group.index[group[0] == True].tolist()[0]
        app = app.loc[app['group'] == 2]

        comm_app_list = pd.read_csv(comm_app_list_path)
        comm_app_list = comm_app_list['Communication'].tolist()
        app = app[~app.application_name.isin(comm_app_list)]

    if not call.empty:
        if not sms.empty:
            event = call.merge(sms, how='outer', left_index=True, right_index=True)
        else:
            event = call
    else:
        if not sms.empty:
            event = sms
        else:
            event= pd.DataFrame()

    if not app.empty:
        if not event.empty:
            event = event.merge(app, how='outer', left_index=True, right_index=True)
        else:
            event=app

    if not event.empty:
        times = pd.DatetimeIndex.to_series(event.index,keep_tz=True)
        event=niimpy.util.occurrence(times)
        event = event.groupby(['day']).sum()
        event = event.drop(columns=['hour'])
    return event

def occurrence_call_sms_social(database,subject,begin=None,end=None,app_list_path=None,comm_app_list_path=None):
    """ Returns a DataFrame contanining the number of events that occur in a
    day for calls, sms, and social and communication apps. The events are binned
    in 12-minutes, i.e. if there is an event at 11:05 and another one at 11:45,
    2 occurences happened in one hour. Then, the sum of these occurences yield
    the number per day.

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional
    app_list_path: path to the file where the apps are classified into groups
    comm_app_list_path:path to the file where the communication apps are listed


    Returns
    -------
    event: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    call = database.raw(table='AwareCalls', user=subject)
    if not call.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = call.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = call.iloc[len(call)-1]['datetime']
        call = call.drop(columns=['device','user','time'])
        call = call.loc[begin:end]

    sms = database.raw(table='AwareMessages', user=subject)
    if not sms.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = sms.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = sms.iloc[len(sms)-1]['datetime']
        sms = sms.drop(columns=['device','user','time'])
        sms = sms.loc[begin:end]

    app = database.raw(table='AwareApplicationNotifications', user=subject)
    if(app_list_path==None):
        app_list_path='/m/cs/scratch/networks-nima/ana/niima-code/Datastreams/Phone/apps_group.csv'
    if (comm_app_list_path==None):
        comm_app_list_path='/m/cs/scratch/networks-nima/ana/niima-code/Datastreams/Phone/comm_apps.csv'

    if not app.empty:
        if(begin!=None):
            assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
        else:
            begin = app.iloc[0]['datetime']
        if(end!= None):
            assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
        else:
            end = app.iloc[len(app)-1]['datetime']

        app = app.drop(columns=['device','user','time','defaults','sound','vibrate'])
        app = app.loc[begin:end]
        app_list=pd.read_csv(app_list_path)
        app['group']=np.nan
        for index, row in app.iterrows():
            group=app_list.isin([row['application_name']]).any()
            group=group.reset_index()
            if (not any(group[0])):
                app.loc[index,'group']=10
            else:
                app.loc[index,'group']=group.index[group[0] == True].tolist()[0]
        app = app.loc[(app['group'] == 2) | (app['group'] == 3)]
        comm_app_list = pd.read_csv(comm_app_list_path)
        comm_app_list = comm_app_list['Communication'].tolist()
        app = app[~app.application_name.isin(comm_app_list)]

    if not call.empty:
        if not sms.empty:
            event = call.merge(sms, how='outer', left_index=True, right_index=True)
        else:
            event = call
    else:
        if not sms.empty:
            event = sms
        else:
            event= pd.DataFrame()

    if not app.empty:
        if not event.empty:
            event = event.merge(app, how='outer', left_index=True, right_index=True)
        else:
            event=app

    if not event.empty:
        times = pd.DatetimeIndex.to_series(event.index,keep_tz=True)
        event=niimpy.util.occurrence(times)
        event = event.groupby(['day']).sum()
        event = event.drop(columns=['hour'])
        event.index = pd.to_datetime(event.index).tz_localize('Europe/Helsinki')
    return event

#Location
def location_data(database,subject,begin=None,end=None):
    """ Reads the readily, preprocessed location data from the right database.
    The data already contains the aggregation of the GPS data (more info here:
    https://github.com/digitraceslab/koota-server/blob/master/kdata/converter.py).

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    location: Dataframe
    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    location = database.raw(table='AwareLocationDay', user=subject)
    location = location.drop(['device','user'],axis=1)
    location=location.drop_duplicates(subset=['day'],keep='first')
    location['day']=pd.to_datetime(location['day'], format='%Y-%m-%d')
    location=location.set_index('day')
    location.index = pd.to_datetime(location.index).tz_localize('Europe/Helsinki')

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = location.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = location.index[-1]

    location=location.loc[begin:end]
    return location

#Screen

def get_battery_data(database, user, start = None, end = None):
    """ Returns a DataFrame with battery data for a user.

    Parameters
    ----------
    database: Niimpy database
    user: string
    start: datetime, optional
    end: datetime, optional
    """
    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(user, str),"user not given in string format"

    battery_data = database.raw(table='AwareBattery',user=user)

    if(start!=None):
        start = pd.to_datetime(start)
    else:
        start = battery_data.iloc[0]['datetime']
    if(end!= None):
        end = pd.to_datetime(end)
    else:
        end = battery_data.iloc[len(battery_data)-1]['datetime']

    battery_data = battery_data[(battery_data['datetime']>=start) & (battery_data['datetime']<=end)]

    battery_data['battery_level'] = pd.to_numeric(battery_data['battery_level'])

    #df['column'].fillna(pd.Timedelta(seconds=0))
    #df.dropna()

    battery_data = battery_data.drop_duplicates(subset=['datetime','user','device'],keep='last')
    battery_data = battery_data.drop(['user','device','time','datetime'],axis=1)

    return battery_data


def battery_occurrences(battery_data, user=None, start=None, end=None, battery_status = False, days= 0, hours=6, minutes=0, seconds=0,milli=0, micro=0, nano=0):
    """ Returns a dataframe showing the amount of battery data points found between a given interval and steps.
    The default interval is 6 hours.

    Parameters
    ----------
    battery_data: Dataframe
    user: string, optional
    start: datetime, optional
    end: datetime, optional
    battery_status: boolean, optional
    """

    assert isinstance(battery_data, pd.core.frame.DataFrame), "data is not a pandas DataFrame"
    assert isinstance(user, (type(None), str)),"user not given in string format"

    if(user!= None):
        ocurrence_data = battery_data[(battery_data['user']==user)]
    else:
        occurrence_data = battery_data

    occurrence_data = occurrence_data.drop_duplicates(subset=['datetime','device'],keep='last')

    if(start==None):
        start = occurrence_data.iloc[0]['datetime']
        start = pd.to_datetime(start)

    td = pd.Timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds,milliseconds=milli,microseconds=micro,nanoseconds=nano)

    delta = start+td

    if(end==None):
        end = occurrence_data.iloc[len(occurrence_data)-1]['datetime']
        end = pd.to_datetime(end)

    idx_range = np.floor((end-start)/td).astype(int)
    idx = pd.date_range(start, periods = idx_range, freq=td)

    if ((battery_status == True) & ('battery_status' in occurrence_data.columns)):
        occurrences = pd.DataFrame(np.nan, index = idx,columns=list(['start','end','occurrences','battery_status']))
        for i in range(idx_range):
            idx_dat = occurrence_data.loc[(occurrence_data['datetime']>start) & (occurrence_data['datetime']<=delta)]
            battery_status = occurrence_data.loc[(occurrence_data['datetime']>start) & (occurrence_data['datetime']<=delta) & ((occurrence_data['battery_status']=='-1')|(occurrence_data['battery_status']=='-2')|(occurrence_data['battery_status']=='-3'))]
            occurrences.iloc[i] = [start, delta,len(idx_dat), len(battery_status)]
            start = start + td
            delta = start + td


    else:
        occurrences = pd.DataFrame(np.nan, index = idx,columns=list(['start','end','occurrences']))
        for i in range(idx_range):
            idx_dat = occurrence_data.loc[(occurrence_data['datetime']>start) & (occurrence_data['datetime']<=delta)]
            occurrences.iloc[i] = [start, delta,len(idx_dat)]
            start = start + td
            delta = start + td
    return occurrences


def battery_gaps(data, min_duration_between = None):
    '''Returns a DataFrame including all battery data and showing the delta between
    consecutive battery timestamps. The minimum size of the considered deltas can be decided
    with the min_duration_between parameter.

    Parameters
    ----------
    data: dataframe with date index
    min_duration_between: Timedelta, for example, pd.Timedelta(hours=6)
    '''
    assert isinstance(data, pd.core.frame.DataFrame), "data is not a pandas DataFrame"
    assert isinstance(data.index, pd.core.indexes.datetimes.DatetimeIndex), "data index is not DatetimeIndex"

    gaps = data.copy()
    gaps['tvalue'] = gaps.index
    gaps['delta'] = (gaps['tvalue']-gaps['tvalue'].shift()).fillna(pd.Timedelta(seconds=0))
    if(min_duration_between!=None):
        gaps = gaps[gaps['delta']>=min_duration_between]

    return gaps


def battery_charge_discharge(data):
    '''Returns a DataFrame including all battery data and showing the charge/discharge between each timestamp.

    Parameters
    ----------
    data: dataframe with date index
    '''
    assert isinstance(data, pd.core.frame.DataFrame), "data is not a pandas DataFrame"
    assert isinstance(data.index, pd.core.indexes.datetimes.DatetimeIndex), "data index is not DatetimeIndex"

    charge = data.copy()
    charge['battery_level'] = pd.to_numeric(charge['battery_level'])
    charge['tvalue'] = charge.index
    charge['tdelta'] = (charge['tvalue']-charge['tvalue'].shift()).fillna(pd.Timedelta(seconds=0))
    charge['bdelta'] = (charge['battery_level']-charge['battery_level'].shift()).fillna(0)
    charge['charge/discharge']= ((charge['bdelta'])/((charge['tdelta']/ pd.Timedelta(seconds=1))))

    return charge

def find_real_gaps(battery_data,other_data,start=None, end=None, days= 0, hours=6, minutes=0, seconds=0,milli=0, micro=0, nano=0):
    """ Returns a dataframe showing the gaps found both in the battery data and the other data.
    The default interval is 6 hours.

    Parameters
    ----------
    battery_data: Dataframe
    other_data: Dataframe
                The data you want to compare with
    start: datetime, optional
    end: datetime, optional
    """
    assert isinstance(battery_data, pd.core.frame.DataFrame), "battery_data is not a pandas DataFrame"
    assert isinstance(other_data, pd.core.frame.DataFrame), "other_data is not a pandas DataFrame"
    assert isinstance(battery_data.index, pd.core.indexes.datetimes.DatetimeIndex), "battery_data index is not DatetimeIndex"
    assert isinstance(other_data.index, pd.core.indexes.datetimes.DatetimeIndex), "other_data index is not DatetimeIndex"

    if(start!=None):
        start = pd.to_datetime(start)
    else:
        start = battery_data.index[0] if (battery_data.index[0]<= other_data.index[0]) else other_data.index[0]
    if(end!=None):
        end = pd.to_datetime(end)
    else:
        end = battery_data.index[-1] if (battery_data.index[-1]>= other_data.index[-1]) else other_data.index[-1]

    battery = battery_occurrences(battery_data, start=start,end=end,days=days,hours=hours,minutes=minutes,seconds=seconds,milli=milli,micro=micro,nano=nano)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace = True)
    other = battery_occurrences(other_data, start=start,days=days,hours=hours,minutes=minutes,seconds=seconds,milli=milli,micro=micro,nano=nano)

    mask = (battery['battery_occurrences']==0)&(other['occurrences']==0)
    gaps = pd.concat([battery[mask],other[mask]['occurrences']],axis=1, sort=False)

    return gaps

def find_non_battery_gaps(battery_data,other_data,start=None, end=None, days= 0, hours=6, minutes=0, seconds=0,milli=0, micro=0, nano=0):
    """ Returns a dataframe showing the gaps found only in the other data.
    The default interval is 6 hours.

    Parameters
    ----------
    battery_data: Dataframe
    other_data: Dataframe
                The data you want to compare with
    start: datetime, optional
    end: datetime, optional

    """
    assert isinstance(battery_data, pd.core.frame.DataFrame), "battery_data is not a pandas DataFrame"
    assert isinstance(other_data, pd.core.frame.DataFrame), "other_data is not a pandas DataFrame"
    assert isinstance(battery_data.index, pd.core.indexes.datetimes.DatetimeIndex), "battery_data index is not DatetimeIndex"
    assert isinstance(other_data.index, pd.core.indexes.datetimes.DatetimeIndex), "other_data index is not DatetimeIndex"

    if(start!=None):
        start = pd.to_datetime(start)
    else:
        start = battery_data.index[0] if (battery_data.index[0]<= other_data.index[0]) else other_data.index[0]
    if(end!=None):
        end = pd.to_datetime(end)
    else:
        end = battery_data.index[-1] if (battery_data.index[-1]>= other_data.index[-1]) else other_data.index[-1]

    battery = battery_occurrences(battery_data, start=start,end=end,days=days,hours=hours,minutes=minutes,seconds=seconds,milli=milli,micro=micro,nano=nano)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace = True)
    other = battery_occurrences(other_data, start=start,days=days,hours=hours,minutes=minutes,seconds=seconds,milli=milli,micro=micro,nano=nano)
    mask = (battery['battery_occurrences']>10)&(other['occurrences']==0)
    gaps = pd.concat([battery[mask],other[mask]['occurrences']],axis=1, sort=False)

    return gaps

def find_battery_gaps(battery_data,other_data,start=None, end=None, days= 0, hours=6, minutes=0, seconds=0,milli=0, micro=0, nano=0):
    """ Returns a dataframe showing the gaps found only in the battery data.
    The default interval is 6 hours.

    Parameters
    ----------
    battery_data: Dataframe
    other_data: Dataframe
                The data you want to compare with
    start: datetime, optional
    end: datetime, optional
    """
    assert isinstance(battery_data, pd.core.frame.DataFrame), "battery_data is not a pandas DataFrame"
    assert isinstance(other_data, pd.core.frame.DataFrame), "other_data is not a pandas DataFrame"
    assert isinstance(battery_data.index, pd.core.indexes.datetimes.DatetimeIndex), "battery_data index is not DatetimeIndex"
    assert isinstance(other_data.index, pd.core.indexes.datetimes.DatetimeIndex), "other_data index is not DatetimeIndex"

    if(start!=None):
        start = pd.to_datetime(start)
    else:
        start = battery_data.index[0] if (battery_data.index[0]<= other_data.index[0]) else other_data.index[0]
    if(end!=None):
        end = pd.to_datetime(end)
    else:
        end = battery_data.index[-1] if (battery_data.index[-1]>= other_data.index[-1]) else other_data.index[-1]

    battery = battery_occurrences(battery_data, start=start,end=end,days=days,hours=hours,minutes=minutes,seconds=seconds,milli=milli,micro=micro,nano=nano)
    battery.rename({'occurrences': 'battery_occurrences'}, axis=1, inplace = True)
    other = battery_occurrences(other_data, start=start,end=end,days=days,hours=hours,minutes=minutes,seconds=seconds,milli=milli,micro=micro,nano=nano)
    mask = (battery['battery_occurrences']==0)&(other['occurrences']>0)
    gaps = pd.concat([battery[mask],other[mask]['occurrences']],axis=1, sort=False)

    return gaps

def missing_data_format(question,keep_values=False):
    """ Returns a series of timestamps in the right format to allow missing data visualization
    .

    Parameters
    ----------
    question: Dataframe

    """
    question['date'] = question.index
    question['date'] = question['date'].apply( lambda question : datetime.datetime(year=question.year, month=question.month, day=question.day))
    question = question.drop_duplicates(subset=['date'],keep='first')

    question =  question.set_index(['date'])
    if (keep_values == False):
        question['answer'] = 1
    question = question.T.squeeze()
    return question

def screen_missing_data(database,subject,begin=None,end=None):
    """ Returns a DataFrame contanining the percentage (range [0,1]) of loss data
    calculated based on the transitions of screen status. In general, if
    screen_status(t) == screen_status(t+1), we declared we have at least one
    missing point.

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    count: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"usr not given in string format"

    screen = database.raw(table='AwareScreen', user=subject)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = screen.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = screen.iloc[len(screen)-1]['datetime']

    screen=screen.drop_duplicates(subset=['datetime'],keep='first')
    screen = screen.drop(['device','user','time'],axis=1)
    screen=screen.loc[begin:end]
    screen['screen_status']=pd.to_numeric(screen['screen_status'])

    #Include the missing points that are due to shutting down the phone
    shutdown = shutdown_info(database,subject,begin,end)
    shutdown=shutdown.rename(columns={'battery_status':'screen_status'})
    shutdown['screen_status']=0
    screen = screen.merge(shutdown, how='outer', left_index=True, right_index=True)
    screen['screen_status'] = screen.fillna(0)['screen_status_x'] + screen.fillna(0)['screen_status_y']
    screen = screen.drop(['screen_status_x','screen_status_y'],axis=1)
    dates=screen.datetime_x.combine_first(screen.datetime_y)
    screen['datetime']=dates
    screen = screen.drop(['datetime_x','datetime_y'],axis=1)

    #Detect missing data points
    screen['missing']=0
    screen['next']=screen['screen_status'].shift(-1)
    screen['dummy']=screen['screen_status']-screen['next']
    screen['missing'] = np.where(screen['dummy']==0, 1, 0)
    screen['missing'] = screen['missing'].shift(1)
    screen = screen.drop(['dummy','next'], axis=1)
    screen = screen.fillna(0)

    screen['datetime'] = screen['datetime'].apply( lambda screen : datetime.datetime(year=screen.year, month=screen.month, day=screen.day))
    screen = screen.drop(['screen_status'], axis=1)
    count=pd.pivot_table(screen,values='missing',index='datetime', aggfunc='count')
    count = screen.groupby(['datetime','missing'])['missing'].count().unstack(fill_value=0)
    count['missing'] = count[1.0]/(count[0.0]+count[1.0])
    count = count.drop([0.0,1.0], axis=1)
    if (pd.Timestamp.tzname(count.index[0]) != 'EET'):
        if pd.Timestamp.tzname(count.index[0]) != 'EEST':
            count.index = pd.to_datetime(count.index).tz_localize('Europe/Helsinki')

    return count

def missing_noise(database,subject,begin=None,end=None):
    """ Returns a Dataframe with the estimated missing data from the ambient
    noise sensor.



    NOTE: This function aggregates data by day.

    Parameters
    ----------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    avg_noise: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    noise = database.raw(table='AwareAmbientNoise', user=subject)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = noise.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = noise.iloc[len(noise)-1]['datetime']

    noise = noise.drop(['device','user','time','double_silence_threshold','double_rms','blob_raw','is_silent','double_frequency'],axis=1)
    noise = noise.loc[begin:end]
    noise['duration'] = noise['datetime'].diff()
    noise['duration'] = get_seconds(noise['duration'])
    noise = noise.iloc[1:]
    shutdown = shutdown_info(database,subject,begin,end)
    shutdown=shutdown.rename(columns={'battery_status':'duration'})
    noise = noise.merge(shutdown, how='outer', left_index=True, right_index=True)
    noise['duration_x'] = noise.fillna(0)['duration_x'] + noise.fillna(0)['duration_y']
    noise=noise.rename(columns={'duration_x':'duration'})
    dates=noise.datetime_x.combine_first(noise.datetime_y)
    noise['datetime']=dates
    noise = noise.drop(['datetime_x','datetime_y'],axis=1)
    noise=noise.drop(['double_decibels', 'duration_y'],axis=1)
    noise['missing'] = np.where(noise['duration']>=1860, 1, 0) #detect the missing points
    noise['dummy'] = noise.missing.shift(-2) #assumes that everytime the cellphone shuts down, two timestamps are generated with -1 in the battery_health
    noise['dummy'] = noise.dummy*noise.duration
    noise['dummy'] = noise.dummy.shift(2)
    noise['missing'] = np.where(noise['missing']==1, np.round(noise['duration']/1800), 0) #calculate the number of datapoints missing
    noise = noise.drop(noise[noise.dummy==-1].index) #delete those missing datapoints due to the phone being shut down
    noise = noise.drop(['duration', 'datetime', 'dummy'],axis=1)
    return noise
