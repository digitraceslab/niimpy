import numpy as np
import pandas as pd

import niimpy
from . import read
from . import preprocess
from .battery import shutdown_info

def screen_off(screen, subject=None, begin=None, end=None, battery=None):
    """Return times of only screen offs.

    Returns a DataFrame with the timestamps of when the screen has changed
    to "OFF" status.


    NOTE: This is a helper function created originally to preprocess the application
    info data.  It differs from raw screen data in that it also considers
    battery data to find possible missing 'screen off' events caused by running
    out of battery.

    Parameters
    ----------
    screen: dataframe of screen data
    user: string
    begin: datetime, optional
    end: datetime, optional
    battery: dataframe of battery data

    Returns
    -------
    screen: Dataframe

            DataFrame with DatetimeIndex and `screen_status` column.
            All values are zero and all row indexes are the times of screen off.


    """
    # TODO: take a new argument of 'shutdown events'
    screen  = niimpy.filter_dataframe(screen, begin=begin, end=end, user=subject)

    screen=screen.groupby(screen.index).first()
    screen = screen[['screen_status']]
    screen=screen.loc[begin:end]
    screen['screen_status']=pd.to_numeric(screen['screen_status'])

    #Include the missing points that are due to shutting down the phone
    if battery is not None:
        shutdown = shutdown_info(battery,subject,begin,end)
        shutdown=shutdown.rename(columns={'battery_status':'screen_status'})
        shutdown['screen_status']=0

        if not shutdown.empty:
            screen = screen.merge(shutdown, how='outer', left_index=True, right_index=True)
            screen['screen_status'] = screen.fillna(0)['screen_status_x'] + screen.fillna(0)['screen_status_y']
            screen = screen.drop(['screen_status_x','screen_status_y'], axis=1)
            screen['datetime']=screen.index

    #Detect missing data points
    screen['missing']=0
    screen['next']=screen['screen_status'].shift(-1)
    screen['dummy']=screen['screen_status']-screen['next']
    screen['missing'] = np.where(screen['dummy']==0, 1, 0)
    screen['missing'] = screen['missing'].shift(1)
    screen = screen.drop(['dummy','next'], axis=1)
    screen = screen.fillna(0)
    '''
    new = screen
    Previous method
    for i in range(len(screen)-1):
        if ((screen.screen_status[i]==0 and screen.screen_status[i+1]==0) or
            (screen.screen_status[i]==1 and screen.screen_status[i+1]==1) or
            (screen.screen_status[i]==2 and screen.screen_status[i+1]==2) or
            (screen.screen_status[i]==3 and screen.screen_status[i+1]==3)):
            screen.missing[i+1]=1
    New method tested with assert_frame_equal(new, screen, check_dtype=False)
    '''
    #Discard missing values
    screen = screen[screen.missing == 0]
    #Select only those OFF events
    screen = screen[screen.screen_status == 0]
    return screen[['screen_status', 'missing']]


def screen_duration(screen,subject=None,begin=None,end=None,battery=None):
    """Screen on/off time and count daily aggregate.

    Returns two DataFrames contanining the duration and number of events for
    the screen transitions (ON to OFF, OFF to ON, OFF to IN USE, IRRELEVANT
    transitions). E.g. duration (in seconds) of the phone being ON during a day,
    or number of times the screen was on during the day.

    Parameters
    ----------
    database: Niimpy dataframe or database
    user: string
    begin: datetime, optional
    end: datetime, optional
    battery: Niimpy dataframe or database of battery data


    Returns
    -------
    duration: Dataframe
    count: Dataframe

    """
    screen  = niimpy.read._get_dataframe(screen, table='AwareScreen', user=subject)
    screen  = niimpy.filter_dataframe(screen, begin=begin, end=end)

    # Drop duplicates based on index
    screen = screen.groupby(screen.index).first()
    #screen = screen.drop(['device','user','time'],axis=1)
    screen = screen[['screen_status']]
    screen['datetime'] = screen.index

    screen=screen.loc[begin:end]
    screen['screen_status']=pd.to_numeric(screen['screen_status'])

    # If battery is None, then we must have been passed a database, so
    # use that in the calling of 'shutdown'.
    if battery is None and isinstance(screen, niimpy.database.Data1):
        battery = screen
    if battery is not None:
        #Include the missing points that are due to shutting down the phone
        shutdown = shutdown_info(battery,subject,begin,end)
        shutdown=shutdown.rename(columns={'battery_status':'screen_status'})
        shutdown['screen_status']=0
        shutdown['datetime'] = shutdown.index

        screen = screen.merge(shutdown, how='outer', left_index=True, right_index=True)
        screen['screen_status'] = screen.fillna(0)['screen_status_x'] + screen.fillna(0)['screen_status_y']
        screen = screen.drop(['screen_status_x','screen_status_y'],axis=1)
        screen['datetime']=screen.index

    #Detect missing data points
    screen['missing']=0
    screen['next']=screen['screen_status'].shift(-1)
    screen['dummy']=screen['screen_status']-screen['next']
    screen['missing'] = np.where(screen['dummy']==0, 1, 0)
    screen['missing'] = screen['missing'].shift(1)
    screen = screen.drop(['dummy','next'], axis=1)
    screen = screen.fillna(0)

    '''
    Previous code, updated for more efficient one
    Verified with assert_frame_equal(screen, screen_for, check_dtype=False)
    screen['missing']=0
    for i in range(len(screen)-1):
        if ((screen.screen_status[i]==0 and screen.screen_status[i+1]==0) or
            (screen.screen_status[i]==1 and screen.screen_status[i+1]==1) or
            (screen.screen_status[i]==2 and screen.screen_status[i+1]==2) or
            (screen.screen_status[i]==3 and screen.screen_status[i+1]==3)):
            screen.missing[i+1]=1'''

    #Exclude missing datapoints, but keep track of how many were excluded first
    if (1 in screen['missing'].unique()):
        missing_count=(screen['missing'].value_counts()[1]/screen['missing'].value_counts()[0])*100
        print('Missing datapoints (%): ' + str(missing_count))
    else:
        print('No missing values')

    #Discard missing values
    screen = screen[screen.missing == 0]

    #Calculate the duration
    screen['duration']=np.nan
    screen['duration']=screen['datetime'].diff()
    screen['datetime'] = screen['datetime'].dt.floor('d')
    screen['duration'] = screen['duration'].shift(-1)

    #Classify the event
    screen=screen.rename(columns={'missing':'group'})
    screen['next']=screen['screen_status'].shift(-1)
    screen['next']=screen['screen_status'].astype(int).astype(str)+screen['screen_status'].shift(-1).fillna(0).astype(int).astype(str)
    screen.loc[(screen.next=='01') | (screen.next=='02'), 'group']=1
    screen.loc[(screen.next=='03') | (screen.next=='13') | (screen.next=='23'), 'group']=2
    screen.loc[(screen.next=='12') | (screen.next=='21') | (screen.next=='31') | (screen.next=='32'), 'group']=3
    del screen['next']
    screen['group'] = screen['group'].shift(1)
    screen.loc[screen.index[:1],'group']=0
    del screen['screen_status']

    '''
    Older method. Previous code, updated for more efficient one
    Verified with assert_frame_equal(screen, screen_for, check_dtype=False)
    screen=screen.rename(columns={'missing':'group'})
    for i in range(len(screen)-1):
        if ((screen.screen_status[i]==0 and screen.screen_status[i+1]==1) or
            (screen.screen_status[i]==0 and screen.screen_status[i+1]==2)):
            screen.group[i+1]=1
        elif ((screen.screen_status[i]==0 and screen.screen_status[i+1]==3) or
            (screen.screen_status[i]==1 and screen.screen_status[i+1]==3) or
            (screen.screen_status[i]==2 and screen.screen_status[i+1]==3)):
            screen.group[i+1]=2
        elif ((screen.screen_status[i]==1 and screen.screen_status[i+1]==2) or
            (screen.screen_status[i]==2 and screen.screen_status[i+1]==1) or
            (screen.screen_status[i]==3 and screen.screen_status[i+1]==1) or
            (screen.screen_status[i]==3 and screen.screen_status[i+1]==2)):
            screen.group[i+1]=3
    '''

    #Discard the first and last row because they do not have all info. We do not
    #know what happened before or after these points.
    screen = screen.iloc[1:]
    screen = screen.iloc[:-1]

    #Discard any datapoints whose duration in “ON” and “IRRELEVANT” states are
    #longer than 2 hours
    thr = pd.Timedelta('2 hours')
    screen = screen[~((screen.group==1) & (screen.duration>thr))]

    #Finally organize everything
    # Somehow aggfunc=np.sum fails and makes an empty DataFrame.  But
    # passing it through a lambda indirection does work.  This is
    # needed in pandas>=1.30.
    duration=screen.pivot_table(values='duration',index='datetime', columns='group', aggfunc=lambda x: np.sum(x))
    #duration['total']=duration.sum(axis=1)
    #mean_hours=duration['total'].mean()
    #print('mean hours in record per day: ' + str(mean_hours))
    duration.columns = duration.columns.map({0.0: 'off', 1.0: 'on', 2.0: 'use', 3.0: 'irrelevant', 4.0: 'total'})
    duration = duration.apply(preprocess.get_seconds,axis=1)
    count=pd.pivot_table(screen,values='duration',index='datetime', columns='group', aggfunc='count')
    count.columns = count.columns.map({0.0: 'off_count', 1.0: 'on_count', 2.0: 'use_count', 3.0: 'irrelevant_count', 4.0: 'total_count'})
    # reset index names
    duration.index.name = None
    count.index.name = None
    return duration, count
