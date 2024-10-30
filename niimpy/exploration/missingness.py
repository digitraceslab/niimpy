# TODO: probably put them in some other files within missingess folder

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

def screen_missing_data(database,subject,start=None,end=None):
    """ Returns a DataFrame contanining the percentage (range [0,1]) of loss data
    calculated based on the transitions of screen status. In general, if
    screen_status(t) == screen_status(t+1), we declared we have at least one
    missing point.

    Parameters
    ----------
    database: Niimpy database
    user: string
    start: datetime, optional
    end: datetime, optional


    Returns
    -------
    count: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"usr not given in string format"

    screen = database.raw(table='AwareScreen', user=subject)

    if(start!=None):
        assert isinstance(start,pd.Timestamp),"start not given in timestamp format"
    else:
        start = screen.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = screen.iloc[len(screen)-1]['datetime']

    screen=screen.drop_duplicates(subset=['datetime'],keep='first')
    screen = screen.drop(['device','user','time'],axis=1)
    screen=screen.loc[start:end]
    screen['screen_status']=pd.to_numeric(screen['screen_status'])

    #Include the missing points that are due to shutting down the phone
    shutdown = shutdown_info(database,subject,start,end)
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

def missing_noise(database,subject,start=None,end=None):
    """ Returns a Dataframe with the estimated missing data from the ambient
    noise sensor.



    NOTE: This function aggregates data by day.

    Parameters
    ----------
    database: Niimpy database
    user: string
    start: datetime, optional
    end: datetime, optional


    Returns
    -------
    avg_noise: Dataframe

    """

    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(subject, str),"user not given in string format"

    noise = database.raw(table='AwareAmbientNoise', user=subject)

    if(start!=None):
        assert isinstance(start,pd.Timestamp),"start not given in timestamp format"
    else:
        start = noise.iloc[0]['datetime']
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"
    else:
        end = noise.iloc[len(noise)-1]['datetime']

    noise = noise.drop(['device','user','time','silence_threshold','rms','blob_raw','is_silent','frequency'],axis=1)
    noise = noise.loc[start:end]
    noise['duration'] = noise['datetime'].diff()
    noise['duration'] = get_seconds(noise['duration'])
    noise = noise.iloc[1:]
    shutdown = shutdown_info(database,subject,start,end)
    shutdown=shutdown.rename(columns={'battery_status':'duration'})
    noise = noise.merge(shutdown, how='outer', left_index=True, right_index=True)
    noise['duration_x'] = noise.fillna(0)['duration_x'] + noise.fillna(0)['duration_y']
    noise=noise.rename(columns={'duration_x':'duration'})
    dates=noise.datetime_x.combine_first(noise.datetime_y)
    noise['datetime']=dates
    noise = noise.drop(['datetime_x','datetime_y'],axis=1)
    noise=noise.drop(['decibels', 'duration_y'],axis=1)
    noise['missing'] = np.where(noise['duration']>=1860, 1, 0) #detect the missing points
    noise['dummy'] = noise.missing.shift(-2) #assumes that everytime the cellphone shuts down, two timestamps are generated with -1 in the battery_health
    noise['dummy'] = noise.dummy*noise.duration
    noise['dummy'] = noise.dummy.shift(2)
    noise['missing'] = np.where(noise['missing']==1, np.round(noise['duration']/1800), 0) #calculate the number of datapoints missing
    noise = noise.drop(noise[noise.dummy==-1].index) #delete those missing datapoints due to the phone being shut down
    noise = noise.drop(['duration', 'datetime', 'dummy'],axis=1)
    return noise
