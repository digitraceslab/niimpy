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
