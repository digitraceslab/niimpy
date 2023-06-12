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
         "S1_1": ["no", "some", "a_lot"],
         "S1_2": ["no", "some", "a_lot"],
         "S1_3": ["no", "some", ""],
        })
df2['time'] = pd.to_datetime(df2['time'])
df2 = df2.set_index('time')

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
        "a_lot": 2,
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


