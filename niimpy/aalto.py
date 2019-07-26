# Aalto-specific niimpy functions

from .database import ALL

from . import survey

import pandas as pd
PHQ9_ANSWER_MAP = {
    "Ei lainkaan": 0,
    "Useina päivinä": 1,
    "Useina pÃ¤ivinÃ¤": 1,
    "Useammin kuin puolet ajasta": 2,
    "Useammin kuin puolet ajasta": 2,
    "Lähes joka päivä": 3,
    "LÃ¤hes joka pÃ¤ivÃ¤": 3,
}


def phq9_raw(db, user=ALL):
    """Given a database, extract all the relevant PHQ9 from pilot study.

    This extracts PHQ9 survey responses from a database and normalizes
    them properly.
    """

    tables = db.tables()
    scores = [ ]
    for survey_table in ['HyksSurveyAllAnswers', 'HyksPHQ9Answers', # pilot
                         'MMMBaseline', 'MMMPostActive',
                         ]:
        if survey_table in tables:
            initial = db.raw(survey_table, user=user)
            initial = initial[initial['id'].str.startswith('PHQ9_')]
            initial['source'] = survey_table
            scores.append(initial[["user", "id", "answer", "source"]])
            del initial

    if 'AwareHyksConverter' in tables:
        apphyks = db.raw('AwareHyksConverter', user=user)
        apphyks = apphyks[apphyks['id'].str.startswith('PHQ9_')]
        apphyks['answer'] = apphyks['answer'].replace(PHQ9_ANSWER_MAP)
        apphyks['source'] = 'AwarePilot'
        scores.append(apphyks[["user", "id", "answer", "source"]])
        del apphyks

    scores = pd.concat(scores)
    scores['answer'] = pd.to_numeric(scores['answer'])
    return scores


def phq9_scores(db, user=ALL):
    raw = phq9_raw(db, user=user)
    scores = survey.sum_survey_scores(raw, "PHQ9")
    return scores
