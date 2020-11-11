# Utilities for dealing with survey data

import pandas as pd

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
