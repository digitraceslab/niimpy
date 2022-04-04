import numpy as np
import pandas as pd

import niimpy.preprocessing.survey

def test_sum_survey_scores_indexonly():
    df = df1.copy()
    df.index.name = None

    results = niimpy.preprocessing.survey.sum_survey_scores(df, 'S1')

    assert results.loc['2019-01-01']['score'] == 3
    assert results.loc['2019-01-02']['score'] == 12
    assert np.isnan(results.loc['2019-01-03']['score'])
