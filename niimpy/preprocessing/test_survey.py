import numpy as np
import pandas as pd

import niimpy.preprocessing.survey

df1 = pd.DataFrame(
        {"time": ['2019-01-01']*3 + ['2019-01-02']*3 + ['2019-01-03']*3,
         "answer": [0, 1, 2, 3, 4, 5, 6, 7, np.nan],
        "id": ["S1_1", "S1_2", "S1_3"] * 3,
        })
df1['time'] = pd.to_datetime(df1['time'])
df1 = df1.set_index('time')


def test_sum_survey_scores():
    df = df1.copy()
    print(df)

    results = niimpy.survey.sum_survey_scores(df, 'S1')
    print(results)

    assert results.loc['2019-01-01']['score'] == 3
    assert results.loc['2019-01-02']['score'] == 12
    assert np.isnan(results.loc['2019-01-03']['score'])

    df['user'] = 'some_user'
    results = niimpy.survey.sum_survey_scores(df, 'S1')
    print(results)
    results = results.loc['some_user']
    assert results.loc['2019-01-01']['score'] == 3
    assert results.loc['2019-01-02']['score'] == 12
    assert np.isnan(results.loc['2019-01-03']['score'])

def test_sum_survey_scores_indexonly():
    df = df1.copy()
    df.index.name = None
    print(df)

    results = niimpy.survey.sum_survey_scores(df, 'S1')
    print(results)

    assert results.loc['2019-01-01']['score'] == 3
    assert results.loc['2019-01-02']['score'] == 12
    assert np.isnan(results.loc['2019-01-03']['score'])
