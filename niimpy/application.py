

#Application
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

    # TODO: Split those missing data imputation methods to another function
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
