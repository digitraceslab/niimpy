# Utilities for dealing with survey data

import pandas as pd
import numpy as np
from niimpy.preprocessing import util


# Below, we provide some mappings between standardized survey raw questions and their respective codes
# You will need to adjust these mappings to your own needs if your questions do not match with these values.

# PHQ2: Patient Health Questionnaire. Link: https://en.wikipedia.org/wiki/Patient_Health_Questionnaire
PHQ2_MAP = {
    'Little interest or pleasure in doing things' : 'PHQ2_1',
    'Feeling down depressed or hopeless' : 'PHQ2_2',
}

# PHQ9: Patient Health Questionnaire. Link: https://en.wikipedia.org/wiki/PHQ-9
PHQ9_MAP = {'Little interest or pleasure in doing things' : "PHQ9_1",
            'Feeling down depressed or hopeless' : "PHQ9_2",
            'Trouble falling or staying asleep or sleeping too much' : "PHQ9_3",
            'Feeling tired or having little energy' : "PHQ9_4",
            'Poor appetite or overeating' : "PHQ9_5",
            'Feeling bad about yourself or that you are a failure or have let yourself or your family down' : "PHQ9_6",
            'Trouble concentrating on things such as reading the newspaper or watching television' : "PHQ9_7",
            'Moving or speaking so slowly that other people could have noticed. Or the opposite being so fidgety or restless that you have been moving around a lot more than usual' : "PHQ9_8",
            'Thoughts that you would be better off dead or of hurting yourself' : "PHQ9_9",
            }

# PSQI: Pittsburgh Sleep Quality Index. Link: https://en.wikipedia.org/wiki/Pittsburgh_Sleep_Quality_Index
PSQI_MAP = {
    'Currently is your sleep typically interrupted? (For example for attending to a child or due to loud neighbours or medical reasons.)' : 'PSQI_1',
    'During the past month how often have you taken medicine (prescribed or “over the counter”) to help you sleep' : 'PSQI_2',
    'During the past month how often have you had trouble staying awake while driving eating meals or engaging in social activity' : 'PSQI_3',
    'During the past month how much of a problem has it been for you to keep up enthusiasm to get things done' : 'PSQI_4',
    'During the past month how would you rate your sleep quality overall' : 'PSQI_5',
    'When have you usually gone to bed? (hh:mm)' : 'PSQI_6',
    'What time have you usually gotten up in the morning? (hh:mm)' : 'PSQI_7',
    'How long (in minutes) has it taken you to fall asleep each night' : 'PSQI_8',
    'How many hours of actual sleep did you get at night' : 'PSQI_9',
}

# PSS-10: Perceived Stress Scale. Link: https://en.wikipedia.org/wiki/Perceived_Stress_Scale
PSS10_MAP = {
    'In the last month how often have you been upset because of something that happened unexpectedly' : 'PSS10_1',
    'In the last month how often have you felt that you were unable to control the important things in your life' : 'PSS10_2',
    'In the last month how often have you felt nervous and “stressed”' : 'PSS10_3',
    'In the last month how often have you felt confident about your ability to handle your personal problems' : 'PSS10_4',
    'In the last month how often have you felt that things were going your way' : 'PSS10_5',
    'In the last month how often have you been able to control irritations in your life' : 'PSS10_6',
    'In the last month how often have you felt that you were on top of things' : 'PSS10_7',
    'In the last month how often have you been angered because of things that were outside of your control' : 'PSS10_8',
    'In the last month how often have you felt difficulties were piling up so high that you could not overcome them' : 'PSS10_9',
    'In the last month how often have you found that you could not cope with all the things that you had to do': 'PSS10_10'
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
    'Feeling nervous anxious or on edge': 'GAD2_1',
    'Not being able to stop or control worrying': 'GAD2_2'
}

# The below mappings map between answers to the questionnaires and their numerical values
# You will need to adjust these mappings to your own needs if the answers do not match with these values.
PSS_ANSWER_MAP = {
    'never': 0,
    'almost never': 1,
    'sometimes': 2,
    'fairly often': 3,
    'very often': 4
}

PHQ2_ANSWER_MAP = {
    'not at all': 0,
    'several days': 1,
    'more than half the days': 2,
    'nearly every day': 3
}

PHQ9_ANSWER_MAP = {
    "Not at all": 0,
    "Several days": 1,
    "More than half the days": 2,
    "Nearly every day": 3
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

group_by_columns = set(["user", "device", "group"])


def clean_survey_column_names(df):
    """
    This function takes a pandas DataFrame as input and cleans the column names
    by removing or replacing specified characters. It helps to ensure standardized
    and clean column names for further analysis or processing.
    
    Parameters
    ----------
        df : pandas dataframe
          The input DataFrame with column names to be cleaned.
    
    Returns
    -------
        df : pandas.DataFrame
          The DataFrame with cleaned column names.
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"

    for char in ['.', ',', ':', ';', '!', '?', '(', ')', '[', ']', '{', '}']:
        df.columns = df.columns.str.replace(char, "")
    for char in ['-', '_', '—']:
        df.columns = df.columns.str.replace(char, " ")
    return df


def convert_survey_to_numerical_answer(df, id_map, use_prefix=False):
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
    assert isinstance(id_map, dict), "id_map is not a dictionary."
    assert isinstance(use_prefix, bool), "use_prefix is not a bool."

    for key, map in id_map.items():
        if use_prefix == True:
            columns  = [c for c in df.columns if c.startswith(key)]
        else:
            columns = [c for c in df.columns if c == key]
        for col in columns:
            for char in [',', ':', ';', '!', '?', '(', ')', '[', ']', '{', '}']:
                df[col] = df[col].str.replace(char, "")
            for char in ['-', '_', '—']:
                df[col] = df[col].str.replace(char, " ")
            df[col] = df[col].map(map)
    return df

def survey_statistic(df, columns=None, prefix=None, resample_args={"rule":"1D"}, **kwargs):
    '''
    Return statistics for a single survey question or a list of questions.
    Assuming that each of the columns contains numerical values representing
    answers, this function returns the mean, maximum, minimum and standard
    deviation for each question in separate columns.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict, optional
        Dictionary keys containing optional arguments for the computation of screen
        information

        configuration options include:
            columns: string or list(string), optional
                A list of columns to process. If empty, the prefix will be
                used to identify columns
            prefix: string or list(string)
                required unless columns is given. The function will process
                columns whose name starts with the prefix (QID_0, QID_1, ...)
                
    Returns
    -------
    dict: pandas.DataFrame
        A dataframe containing summaries of each questionaire.
    '''
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if columns is not None:
        assert type(columns) == str or type(columns) == list, "columns is not a string or a list of strings."
    if prefix is not None:
        assert type(prefix) == str or type(prefix) == list, "prefix is not a string or a list of strings."
    if columns is None and prefix is None:
        raise ValueError("Either columns or prefix must be specified.")
    
    if columns is None:
        if type(prefix) == list:
            columns = []
            for pref in prefix:
                columns += [c for c in df.columns if c.startswith(pref)]
        else:
            columns = [c for c in df.columns if c.startswith(prefix)]
    
    if type(columns) == str:
        columns = [columns]
    
    def calculate_statistic(df):
        result = {}
        for answer_col in columns:
            result[answer_col+"_mean"] = df[answer_col].mean()
            result[answer_col+"_min"] = df[answer_col].min()
            result[answer_col+"_max"] = df[answer_col].max()
            result[answer_col+"_std"] = df[answer_col].std()
        return pd.Series(result)

    res = util.group_data(df).resample(**resample_args).apply(calculate_statistic)
    res = util.reset_groups(res)
    return res


def sum_survey_scores(df, survey_prefix=None):
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
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert type(survey_prefix) == str or type(survey_prefix) == list, "survey_prefix is not a string or a list of strings."

    result = pd.DataFrame(df["user"])

    if type(survey_prefix) == str:
        survey_prefix = [survey_prefix]

    for prefix in survey_prefix:
        columns = [c for c in df.columns if c.startswith(prefix)]
        result[prefix] = df[columns].sum(axis=1, skipna=False)
    
    return result


ALL_FEATURES = [globals()[name] for name in globals()
                         if name.startswith('survey_')]
ALL_FEATURES = {x: {} for x in ALL_FEATURES}

def extract_features_survey(df, features=None):
    """Calculates survey features

    Parameters
    ----------
    df : pd.DataFrame
        dataframe of survey data. Must follow Niimpy format. In additions,
        each survey question must be in a single column and the column name
        must be formatted as survey-id_question-number (for example PHQ9_3).
    features : map (dictionary) of functions that compute features.
        it is a map of map, where the keys to the first map is the name of
        functions that compute features and the nested map contains the keyword
        arguments to that function. If there is no arguments use an empty map.
        Default is None. If None, all the available functions are used.
        Those functions are in the dict `survey.ALL_FEATURES`.
        You can implement your own function and use it instead or add it
        to the mentioned map.

    Returns
    -------
    features : pd.DataFrame
        Dataframe of computed features where the index is users and columns
        are the the features.
    """
    if features is None:
        features = ALL_FEATURES
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"

    computed_features = []
    for features, feature_arg in features.items():
        computed_feature = features(df, **feature_arg)
        index_by = list(set(group_by_columns) & set(computed_feature.columns))
        computed_feature = computed_feature.set_index(index_by, append=True)
        computed_features.append(computed_feature)
    
    computed_features = pd.concat(computed_features, axis=1)
    computed_features = computed_features.loc[:,~computed_features.columns.duplicated()]

    if 'group' in df:
        computed_features['group'] = df.groupby('user')['group'].first()

    computed_features = util.reset_groups(computed_features)
    return computed_features
