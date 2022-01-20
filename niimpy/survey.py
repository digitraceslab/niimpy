# Utilities for dealing with survey data

import pandas as pd

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