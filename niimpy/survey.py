# Utilities for dealing with survey data

import pandas as pd

# The below mapping works only with Corona dataset. Adjust them to your own need.
PHQ2_MAP = {
    'Little interest or pleasure in doing things.' : 'PHQ2_1',
    'Feeling down; depressed or hopeless.' : 'PHQ2_2',
}

PSQI_MAP = {
    'Currently; is your sleep typically interrupted? (For example; for attending to a child or due to loud neighbours or medical reasons.)' : 'PSQI_1',
    'During the past month; how often have you taken medicine (prescribed or “over the counter”) to help you sleep?' : 'PSQI_2',
    'During the past month; how often have you had trouble staying awake while driving; eating meals; or engaging in social activity?' : 'PSQI_3',
    'During the past month; how much of a problem has it been for you to keep up enthusiasm to get things done?' : 'PSQI_4',
    'During the past month; how would you rate your sleep quality overall?' : 'PSQI_5',
    'When have you usually gone to bed? (hh:mm)' : 'PSQI_6',
    'What time have you usually gotten up in the morning? (hh:mm)' : 'PSQI_7',
    'How long (in minutes) has it taken you to fall asleep each night?' : 'PSQI_8',
    'How many hours of actual sleep did you get at night?' : 'PSQI_9',
}

PSS10_MAP = {
    'In the last month; how often have you been upset because of something that happened unexpectedly?' : 'PSS10_1',
    'In the last month; how often have you felt that you were unable to control the important things in your life?' : 'PSS10_2',
    'In the last month; how often have you felt nervous and “stressed”?' : 'PSS10_3',
    'In the last month; how often have you felt confident about your ability to handle your personal problems?' : 'PSS10_4',
    'In the last month; how often have you felt that things were going your way?' : 'PSS10_5',
    'In the last month; how often have you been able to control irritations in your life?' : 'PSS10_6',
    'In the last month; how often have you felt that you were on top of things?' : 'PSS10_7',
    'In the last month; how often have you been angered because of things that were outside of your control?' : 'PSS10_8',
    'In the last month; how often have you felt difficulties were piling up so high that you could not overcome them?' : 'PSS10_9',
}

PANAS_MAP = {
    'Upset': 'pre_upset',
    'Hostile': 'pre_hostile',
    'Alert': 'pre_alert',
    'Ashamed': 'pre_ashamed',
    'Inspired': 'pre_inspired',
    'Nervous': 'pre_nervous',
    'Determined': 'pre_determined',
    'Attentive': 'pre_attentive',
    'Afraid': 'pre_afraid',
    'Active': 'pre_active',
    
    'Upset.1': 'during_upset',
    'Hostile.1': 'during_hostile',
    'Alert.1': 'during_alert',
    'Ashamed.1': 'during_ashamed',
    'Inspired.1': 'during_inspired',
    'Nervous.1': 'during_nervous',
    'Determined.1': 'during_determined',
    'Attentive.1': 'during_attentive',
    'Afraid.1': 'during_afraid',
    'Active.1': 'during_active'
}

GAD2_MAP = {
    'Feeling nervous; anxious or on edge.': 'GAD2_1',
    'Not being able to stop or control worrying.': 'GAD2_2'
}

PSS_ANSWER_MAP = {
    'never': 0,
    'almost-never': 1,
    'sometimes': 2,
    'fairly-often': 3,
    'very-often': 4
}

PHQ2_ANSWER_MAP = {
    'not-at-all': 0,
    'several-days': 1,
    'more-than-half-the-days': 2,
    'nearly-every-day': 3
}

ID_MAP_PREFIX = {'PSS' : PSS_ANSWER_MAP,
                 'PHQ2' : PHQ2_ANSWER_MAP,
                 'GAD2' : PHQ2_ANSWER_MAP}

def convert_to_numerical_answer(df, answer_col, question_id, id_map, use_prefix=False):
    """Convert text answers into numerical value (assuming a long dataframe).
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing the questions
        
    answer_col : str
        Name of the column containing the answers
        
    question_id : str
        Name of the column containing the question id.
        
    id_map : dictionary
        Dictionary containing answer mappings (value) for each each question id (key).
    
    use_prefix : boolean
        If True, use question id prefix map. The default is False.
    
    Returns
    -------
    result : pandas series
        Series containing converted values
    
    """
    result = df[answer_col]
    
    for key,value in id_map.items():
        if use_prefix == True:
            temp = df[df[question_id].str.startswith(key)][answer_col]
        else:
            temp = df[df[question_id] == key][answer_col]
        temp = temp.replace(value)
        result.loc[temp.index] = temp[:]
        del temp
        
    return result

def print_statistic(df, question_id = 'id', answer_col = 'answer', prefix=None, group=None):
    '''
    Return survey statistic. The statistic includes min, max, average and s.d values.

    :param df: 
        DataFrame contains survey score.
    :param question_id: string. 
        Column contains question id.
    :param answer: 
        Column contains answer in numerical values.
    :param prefix: list. 
        List contains survey prefix. If None is given, search question_id for all possible categories.
    
    Return: dict
        A dictionary contains summary of each questionaire category.
        Example: {'PHQ9': {'min': 3, 'max': 8, 'avg': 4.5, 'std': 2}}
    '''
    
    def calculate_statistic(df, prefix, answer_col, group=None):
        
        d = {}
        if group:
            assert isinstance(group, str),"group is not given in string format"
            
            # Groupby, aggregate and extract statistic from answer column 
            agg_df = df.groupby(['user', group]) \
                         .agg({'answer': sum}) \
                         .groupby(group) \
                         .agg({'answer': ['mean', 'min', 'max','std']})
            agg_df.columns = agg_df.columns.get_level_values(1) #flatten columns 
            agg_df = agg_df.rename(columns={'': group}).reset_index() # reassign group column 
            lst = []

            for index, row in agg_df.iterrows():
                temp = {'min': row['min'], 'max': row['max'], 
                        'avg': row['mean'], 'std': row['std']}
                d[(prefix,row[group])] = temp
        else:
            
            agg_df = df.groupby('user').agg({answer_col: sum})
            d[prefix] = {'min': agg_df[answer_col].min(), 'max': agg_df[answer_col].max(), 
                         'avg': agg_df[answer_col].mean(), 'std': agg_df[answer_col].std()}
        return d
    
    res = {}
    
    # Collect questions with the given prefix. Otherwise, collect all prefix, assuming that 
    # the question id follows this format: {prefix}_id.
    if prefix:
        if isinstance(prefix, str):
            
            temp = df[df[question_id].str.startswith(prefix)]
            return calculate_statistic(temp, prefix, answer_col, group)
        elif isinstance(prefix, list):
            
            for pr in prefix:
                temp = df[df[question_id].str.startswith(pr)]
                d = calculate_statistic(temp, prefix, answer_col, group)
                res.update(d)
        else:
            raise ValueError('prefix should be either list or string')

    else:
        
        # Search for all possible prefix (extract everything before the '_' delimimeter)
        # Then compute statistic as usual
        prefix_lst = list(set(df[question_id].str.split('_').str[0]))
        for pr in prefix_lst:
            temp = df[df[question_id].str.startswith(pr)]
            d = calculate_statistic(temp, pr, answer_col, group)
            res.update(d)
    return res

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
    # Make this function compatible with the logic in this module
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

def sum_survey_scores(df, survey_prefix, answer_column='answer', id_column='id'):
    """Sum all columns (like ``PHQ9_*``) to get a survey score.

    Input dataframe: has a DateTime index, an answer_column with numeric
    scores, and an id_column with question IDs like "PHQ9_1", "PHQ9_2",
    etc.  The given survey_prefix is the "PHQ9" (no underscore) part
    which selects the right questions (rows not matching this prefix
    won't be included).

    This assumes that all surveys have a different time.

    survey: The servey prefix in the 'id' column, e.g. 'PHQ9'.  An '_' is appended.
    """
    # TODO: drop duplicate options
    # TODO: support caterogization ('categories' option which gets
    #       added to dataframe and grouped by)
    if survey_prefix is not None:
        answers = df[df[id_column].str.startswith(survey_prefix+'_')]
    else:
        answers = df
    answers[answer_column] = pd.to_numeric(answers[answer_column])
    # Group by both user and indxe.  I make this groupby_columns to be
    # able to select both the index and the user, when you don't know
    # what name the index might have.
    groupby_columns = [ ]
    if 'user' in answers.columns:
        groupby_columns.append(df['user'])
    groupby_columns.append(df.index)
    #
    survey_score = answers.groupby(groupby_columns)[answer_column].apply(lambda x: x.sum(skipna=False))

    survey_score = survey_score.to_frame()
    survey_score = survey_score.rename({'answer': 'score'}, axis='columns')
    return survey_score


# Move to analysis layer
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