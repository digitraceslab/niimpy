###############################################################################
# This is the main file for selecting subjects based on the missing data in    #
# their datastreams                                                            #
#                                                                              #
# Contributors: Ana Triana                                                     #
################################################################################

import sys
sys.path.insert(0, '/m/cs/scratch/networks-nima/pymod/')
sys.path.insert(0,'/m/cs/scratch/networks-nima/ana/niima-code/Datastreams/Phone/')
import niimpy
import numpy as np
import pandas as pd
from pandas import Series
import time
import datetime
import pytz
import niimpy.aalto
import Functions as f


def subject_selection(database,subject,mode, include_battery=None, include_noise=None, include_screen=None):
    """ Returns a Dataframe with the missing data count (in time or missing 
    points) for a subject. Days that do not meet the criteria are discarded. 
    In brief, the criteria is:
        1. For the PHQ9 surveys: minimum of 3 answers with a gap of 20<t<65 
        days. For the ESM, minimum 2 answers per day.
        2. For the battery data: less than 12 hours with no information. Only 
        gaps of more than one hour are considered.
        3. For other sensors: for the noise data, there should be one datapoint
        every 31 minutes; for the screen data, transitions from one status to 
        itself are flagged as missing data, if the missing data is larger than 
        50% (0.5) of the total of transitions, the day is discarded. 
    
    NOTE: This function aggregates data by day. 
    
    Parameters:
    --------
    database: Niimpy database
    user: string
    mode: string
    
    Returns:
    --------
    days_ok: Dataframe 
    """
    assert isinstance(database, niimpy.database.Data1),"database not given in Niimpy database format"
    assert isinstance(mode, str),"user not given in string format"

    if(include_battery!=None):
        assert isinstance(include_battery, str),"user not given in string format"
    else:
        include_battery = 'yes'

    if(include_noise!=None):
        assert isinstance(include_noise, str),"user not given in string format"
    else:
        include_noise = 'yes'
        
    if(include_battery!=None):
        assert isinstance(include_screen, str),"user not given in string format"
    else:
        include_screen = 'yes'

    # 1. Check PHQ9/ESM
    if mode=='month':
        question = f.get_phq9(database,subject)
        question['time_diff'] = question.index.to_series(keep_tz=True).diff()
        question.iloc[0,1] = datetime.timedelta(days=0)
        number = len(question)
        max_space = question['time_diff'].max().days
        min_space = question['time_diff']<datetime.timedelta(days=20)
        if number>=3:
            if max_space<=65:
                if not min_space.all():
                    subject_ok='yes'

    if mode=='day':
        question = database.raw(table='AwareHyksConverter', user=subject)
        question=question[(question['id']=='olo_1_1')]
        question['answer']=pd.to_numeric(question['answer'])
        question = question.drop(['device', 'time', 'user'], axis=1)    
        if (pd.Timestamp.tzname(question.index[0]) != 'EET'):
            if pd.Timestamp.tzname(question.index[0]) != 'EEST':
                question.index = pd.to_datetime(question.index).tz_localize('Europe/Helsinki')    
        question=question.drop_duplicates(subset=['datetime','id'],keep='first')
        question=question.pivot_table(index='datetime', columns='id', values='answer')
        question=question.rename(columns={'olo_1_1': 'cheerful'})
        question['date'] = pd.DatetimeIndex(question.index).normalize()
        question = question.groupby(question.date).count()
        question = question[question.cheerful>=2] #there should be minimum 2 answers per day to keep it      
        if len(question)>=7: #must have 7 days of data to be accepted
            subject_ok='yes'
    
    if subject_ok=='yes':
        #Choose the timeframe based on the days we have questionnaire data
        start_date = question.index[0] 
        if mode=='month':
            end_date = question.index[-1]
        else:
            end_date = question.index[-1]+pd.Timedelta('1 days')

    #only continue for those subjects who meet the criteria for #1. 
    if subject_ok=='yes':
        #2. Check battery data
        if include_battery=='yes':
            bat = f.get_battery_data(database, subject, start=start_date, end=end_date)
            bat = bat.drop(['battery_status','battery_health','battery_adaptor'],axis=1)
            bat['datetime'] = bat.index
            bat['date'] = pd.DatetimeIndex(bat.datetime).normalize()
            #insert a timestamp at midnight every day, to start counting the number of hours lost during one hour
            dummy = pd.DataFrame(pd.date_range(start=start_date.normalize()+pd.Timedelta('1 days'), end=end_date.normalize()))
            dummy = dummy.set_index(0)
            bat = bat.merge(dummy, how='outer', left_index=True, right_index=True)
            #Calculate the difference
            bat['time_diff'] = bat.index.to_series(keep_tz=True).diff()
            #now if the gaps larger than 1 hour and discard those days in which the sum of gaps is larger than 12 hours (i.e. we lost half of the day)
            bat.loc[bat.battery_level.isnull(), 'time_diff'] = np.nan
            subject_days = bat.groupby([bat.date])['time_diff'].apply(lambda x: x[x > pd.Timedelta('1 hour')].sum()) #ignores NaT
            mask = subject_days[subject_days.gt(pd.Timedelta('12 hour'))]
            subject_days = subject_days.drop(mask.index)
            if mode=='month':
                subject_days = subject_days.iloc[1:]#discard the first date, since it is baseline. 
            subject_days = subject_days.to_frame()

        # 3. Check other sensors
        if include_noise=='yes':
            #reliable fixed frequency data? (ambient noise)
            noise = f.missing_noise(database,subject,begin=start_date,end=end_date)
            noise['date'] = noise.index.normalize()
            noise_days = noise.groupby([noise.date])['missing'].sum() #ignores NaT
            noise_days = noise_days[noise_days<=28]
            if mode=='month':
                noise_days = noise_days.iloc[1:]#discard the first date, since it is baseline. 
            noise_days = noise_days.to_frame()

        if include_screen=='yes':
            #reliable non fixed frequency data? (screen)
            sc = f.screen_missing_data(database,subject,begin=start_date,end=end_date)
            if mode=='month':
                sc = sc.iloc[1:]#discard the first date, since it is baseline. 
            sc = sc[sc['missing']<0.5]

        #merge everything into one
        if (include_battery=='yes' and include_noise=='yes' and include_screen=='yes'):
            days_ok = subject_days.merge(noise_days, how='outer', left_index=True, right_index=True)
            days_ok = days_ok.merge(sc, how='outer', left_index=True, right_index=True)
        if (include_battery=='yes' and include_noise=='yes' and include_screen=='no'):
            days_ok = subject_days.merge(noise_days, how='outer', left_index=True, right_index=True)
        if (include_battery=='yes' and include_noise=='no' and include_screen=='yes'):
            days_ok = subject_days.merge(sc, how='outer', left_index=True, right_index=True)
        if (include_battery=='no' and include_noise=='yes' and include_screen=='yes'):
            days_ok = noise_days.merge(sc, how='outer', left_index=True, right_index=True)
        if (include_battery=='no' and include_noise=='yes' and include_screen=='no'):
            days_ok = noise_days
        if (include_battery=='no' and include_noise=='no' and include_screen=='yes'):
            days_ok = sc
        if (include_battery=='yes' and include_noise=='no' and include_screen=='no'):
            days_ok = subject_days

        days_ok = days_ok.dropna()
        return days_ok

    else:
        return None