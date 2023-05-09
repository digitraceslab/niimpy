# Utilities for dealing with survey data

import pandas as pd


# Below, we provide some mappings between standardized survey raw questions and their respective codes
# You will need to adjust these mappings to your own needs if your questions do not match with these values.

# PHQ2: Patient Health Questionnaire. Link: https://en.wikipedia.org/wiki/Patient_Health_Questionnaire
PHQ2_MAP = {
    'Little interest or pleasure in doing things.' : 'PHQ2_1',
    'Feeling down; depressed or hopeless.' : 'PHQ2_2',
}

# PHQ9: Patient Health Questionnaire. Link: https://en.wikipedia.org/wiki/PHQ-9
PHQ9_MAP = {'Little interest in doing things.' : "PHQ9_1",
            'Feeling down, depressed, or hopeless.' : "PHQ9_2",
            'Trouble falling or staying asleep, or sleeping too much.' : "PHQ9_3",
            'Feeling tired or having little energy.' : "PHQ9_4",
            'Poor appetite or overeating.' : "PHQ9_5",
            'Feeling bad about yourself or that you are a failure or have let yourself or your family down.' : "PHQ9_6",
            'Trouble concentrating on things, such as reading the newspaper or watching television.' : "PHQ9_7",
            'Moving or speaking so slowly that other people could have noticed. Or the opposite being so fidgety or restless that you have been moving around a lot more than usual.' : "PHQ9_8",
            'Thoughts that you would be better off dead, or of hurting yourself.' : "PHQ9_9",
            }

# PSQI: Pittsburgh Sleep Quality Index. Link: https://en.wikipedia.org/wiki/Pittsburgh_Sleep_Quality_Index
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

# PSS-10: Perceived Stress Scale. Link: https://en.wikipedia.org/wiki/Perceived_Stress_Scale
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
    'In the last month, how often have you found that you could not cope with all the things that you had to do?': 'PSS10_10'
}

# PANAS: Positive and Negative Affect Schedule. Link: https://en.wikipedia.org/wiki/Positive_and_Negative_Affect_Schedule
PANAS_MAP = {
    'Upset': 'upset',
    'Hostile': 'hostile',
    'Alert': 'alert',
    'Ashamed': 'ashamed',
    'Inspired': 'inspired',
    'Nervous': 'nervous',
    'Determined': 'determined',
    'Attentive': 'attentive',
    'Afraid': 'afraid',
    'Active': 'active',
}

# GAD: Generalized anxiety disorder. Link: https://en.wikipedia.org/wiki/Generalized_anxiety_disorder
GAD2_MAP = {
    'Feeling nervous; anxious or on edge.': 'GAD2_1',
    'Not being able to stop or control worrying.': 'GAD2_2'
}

# The below mappings map between answers to the questionnaires and their numerical values
# You will need to adjust these mappings to your own needs if the answers do not match with these values.
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

# use this mapping for prefix option, so that multiple question id's can be processed
# simultaneuously
ID_MAP_PREFIX = {'PSS' : PSS_ANSWER_MAP,
                 'PHQ2' : PHQ2_ANSWER_MAP,
                 'GAD2' : PHQ2_ANSWER_MAP}

# use this mapping if you want to explicitly specify the mapping for each question
ID_MAP =  {'PSS10_1' : PSS_ANSWER_MAP,
           'PSS10_2' : PSS_ANSWER_MAP,
           'PSS10_3' : PSS_ANSWER_MAP,
           'PSS10_4' : PSS_ANSWER_MAP,
           'PSS10_5' : PSS_ANSWER_MAP,
           'PSS10_6' : PSS_ANSWER_MAP,
           'PSS10_7' : PSS_ANSWER_MAP,
           'PSS10_8' : PSS_ANSWER_MAP,
           'PSS10_9' : PSS_ANSWER_MAP,
           'PSS10_10' : PSS_ANSWER_MAP}

def survey_convert_to_numerical_answer(df, answer_col, question_id, id_map, use_prefix=False):
    """Convert text answers into numerical value (assuming a long dataframe).
    Use answer mapping dictionaries provided by the users to convert the answers.
    Can convert multiple questions having the same prefix (e.g., PSS10_1, PSS10_2, ...,PSS10_9)
    if prefix mapping is provided. Function returns original values for the 
    answers that have not been specified for conversion.
    
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing the questions
        
    answer_col : str
        Name of the column containing the answers
        
    question_id : str
        Name of the column containing the question id.
        
    id_map : dictionary
        Dictionary containing answer mappings (value) for each question_id (key),
        or a dictionary containing a map for each question id prefix if use_prefix 
        option is used.
           
    use_prefix : boolean
        If False, uses given map (id_map) to convert questions. The default is False.  
        If True, use question id prefix map, so that multiple question_id's having 
        the same prefix may be converted on the same time. 
    
    Returns
    -------
    result : pandas series
        Series containing converted values and original values for aswers hat are not 
        supposed to be converted.
    
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(answer_col, str), "answer_col is not a string."
    assert isinstance(question_id, str), "question_id is not a string."
    assert isinstance(id_map, dict), "id_map is not a dictionary."
    assert isinstance(use_prefix, bool), "use_prefix is not a bool."
    
    # copy original answers
    result = df.copy()[answer_col]
    
    for key,value in id_map.items():
        if use_prefix == True:
            temp = df[df[question_id].str.startswith(key)][answer_col]
        
        else:
            temp = df[df[question_id] == key][answer_col]
        
        temp = temp.replace(value)
        result.loc[temp.index] = temp[:]
        del temp
        
    return result

def survey_print_statistic(df, question_id_col = 'id', answer_col = 'answer', prefix=None, group=None):
    '''
    Return survey statistic. Assuming that the question ids are stored in question_id_col and 
    the survey answers are stored in answer_col, this function returns all the relevant statistics for each question. 
    The statistic includes min, max, average and s.d of the scores of each question.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    question_id_col: string. 
        Column contains question id.
    answer_col: string
        Column contains answer in numerical values.
    prefix: list, optional
        List contains survey prefix. If None is given, search question_id_col for all possible categories.
    group: string, optional
        Column contains group factor. If this is given, survey statistics for each group will be returned
    Returns
    -------
    dict: dictionary
        A dictionary contains summary of each questionaire category.
        Example: {'PHQ9': {'min': 3, 'max': 8, 'avg': 4.5, 'std': 2}}
    '''
    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(answer_col, str), "answer_col is not a string."
    assert isinstance(question_id_col, str), "question_id is not a string."
    
    
    def calculate_statistic(df, prefix, answer_col, group=None):
        
        d = {}
        if group:
            assert isinstance(group, str),"group is not given in string format"
            
            # Groupby, aggregate and extract statistic from answer column 
            agg_df = df.groupby(['user', group]) \
                         .agg({answer_col: sum}) \
                         .groupby(group) \
                         .agg({answer_col: ['mean', 'min', 'max','std']})
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
            
            temp = df[df[question_id_col].str.startswith(prefix)]
            return calculate_statistic(temp, prefix, answer_col, group)
        elif isinstance(prefix, list):
            
            for pr in prefix:
                temp = df[df[question_id_col].str.startswith(pr)]
                d = calculate_statistic(temp, prefix, answer_col, group)
                res.update(d)
        else:
            raise ValueError('prefix should be either list or string')

    else:
        
        # Search for all possible prefix (extract everything before the '_' delimimeter)
        # Then compute statistic as usual
        prefix_lst = list(set(df[question_id_col].str.split('_').str[0]))
        for pr in prefix_lst:
            temp = df[df[question_id_col].str.startswith(pr)]
            d = calculate_statistic(temp, pr, answer_col, group)
            res.update(d)
    return res


def survey_sum_scores(df, survey_prefix=None, answer_col='answer', id_column='id'):
    """Sum all columns (like ``PHQ9_*``) to get a survey score.

    Parameters
    -------
    
    df: pandas DataFrame 
        DataFrame should be a DateTime index, an answer_column with numeric
        scores, and an id_column with question IDs like "PHQ9_1", "PHQ9_2",
        etc.  The given survey_prefix is the "PHQ9" (no underscore) part
        which selects the right questions (rows not matching this prefix
        won't be included).

    survey_prefix: string
        The survey prefix in the 'id' column, e.g. 'PHQ9'.  An '_' is appended.
        
    
    Return
    -------
    survey_score: pandas DataFrame
        DataFrame contains the sum of each questionnaires marked with survey_prefix
    """

    answers = df[df[id_column].str.startswith(survey_prefix)]
    
    groupby_columns = [ ]
    if 'user' in answers.columns:
        groupby_columns.append(df['user'])
    groupby_columns.append(df.index)
    
    survey_score = answers.groupby(groupby_columns)[answer_col].apply(lambda x: x.sum(skipna=False))
    
    survey_score = survey_score.to_frame()
    survey_score = survey_score.rename({answer_col: 'score'}, axis='columns')
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
