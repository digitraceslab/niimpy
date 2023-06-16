import numpy as np
import pandas as pd

import niimpy.preprocessing.survey

df1 = pd.DataFrame(
        {"time": ['2019-01-01'] + ['2019-01-02'] + ['2019-01-03'],
         "user": [1, 1, 3],
         "S1_1": [0, 1, 2],
         "S1_2": [3, 4, 5],
         "S1_3": [6, 7, np.nan],
        })
df1['time'] = pd.to_datetime(df1['time'])
df1 = df1.set_index('time')

df2 = pd.DataFrame(
        {"time": ['2019-01-01'] + ['2019-01-02'] + ['2019-01-03'],
         "user": [1, 1, 3],
         "S1_1": ["no", "some", "a lot"],
         "S1_2": ["no", "some", "a lot"],
         "S1_3": ["no", "some", ""],
        })
df2['time'] = pd.to_datetime(df2['time'])
df2 = df2.set_index('time')

df3 = pd.DataFrame(
        {"time": ['2019-01-01'] + ['2019-01-02'] + ['2019-01-03'],
         "user": [1, 1, 3],
         "question_1.": ["no", "some", "a lot"],
         "question_2,": ["no", "some", "a lot"],
         "question_3?": ["no", "some", ""],
        })
df3['time'] = pd.to_datetime(df3['time'])
df3 = df3.set_index('time')

def test_sum_survey_scores():
    df = df1.copy()

    results = niimpy.preprocessing.survey.sum_survey_scores(df, 'S1')

    assert results.loc['2019-01-01']['S1'] == 9.0
    assert results.loc['2019-01-02']['S1'] == 12.0
    assert np.isnan(results.loc['2019-01-03']['S1'])

def test_convert_survey_to_numerical_answer():
    df = df2.copy()

    ID_MAP = {"S1": {
        "no": 0,
        "some": 1,
        "a lot": 2,
    }}
    results = niimpy.preprocessing.survey.convert_survey_to_numerical_answer(
        df,
        id_map=ID_MAP,
        use_prefix=True
    )

    assert results.loc['2019-01-01']['S1_1'] == 0
    assert results.loc['2019-01-02']['S1_2'] == 1
    assert results.loc['2019-01-03']['S1_1'] == 2
    assert np.isnan(results.loc['2019-01-03']['S1_3'])


def test_clean_survey_column_names():
    df = df3.copy()

    cleaned_df = niimpy.preprocessing.survey.clean_survey_column_names(df)

    expected_column_names = ["user", 'question 1', 'question 2', 'question 3']
    assert all([a == b for a, b in zip(cleaned_df.columns, expected_column_names)])


