import numpy as np
import pandas as pd

import niimpy
from . import preprocess

def get_battery_data(battery, user=None, start = None, end = None):
    """ Returns a DataFrame with battery data for a user.
    Parameters
    ----------
    battery: DataFrame with battery data
    user: string, optional
    start: datetime, optional
    end: datetime, optional
    """
    assert isinstance(battery, pd.core.frame.DataFrame), "data is not a pandas DataFrame"
    
    if(user!= None):
        assert isinstance(user, str),"user not given in string format"
        battery_data = battery[(battery['user']==user)]
    else:
        battery_data = battery
        
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
