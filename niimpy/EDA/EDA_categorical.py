# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 14:49:22 2021

@author: arsii
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def categorize_answers(df, question, answer_column):
    """ Extract a question answered and count different answers.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing questionnaire data

    question : str
        question id

    answer_column : str
        column containing the answer

    Returns
    -------
    fig: Pandas Dataframe
        Dataframe containing the category counts of answers
        filtered by the question
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(question, str), "question is not a string."
    assert isinstance(answer_column, str), "column is not a string."

    df = df[(df["question"] == question)][answer_column]
    category_counts = df.astype("category").value_counts(sort=False)
    return category_counts


def plot_categories(
    df, title=None, xlabel=None, ylabel=None, width=900, height=900
 ):
    """ Create a barplot of categorical data

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing categorized data

    title : str
        Plot title

    xlabel : str
        Plot xlabel

    ylabel : str
        Plot ylabel

    width : integer
        Plot width

    height : integer
        Plot height

    Returns
    -------
    fig: plotly Figure
        A barplot of the input data
    """
    assert isinstance(title, str), "title is not a string."
    assert isinstance(xlabel, str), "xlabel is not a string."
    assert isinstance(ylabel, str), "ylabel is not a string."
    assert isinstance(width, int), "width is not an integer."
    assert isinstance(height, int), "height is not an integer."

    fig = px.bar(df)
    fig.update_layout(title = title,
                      xaxis_title = xlabel,
                      yaxis_title = ylabel,
                      width = width,
                      height = height,)
    return fig


def questionnaire_summary(
    df, question, column, title=None, xlabel=None, ylabel=None, user=None
):
    """Plot summary barplot for questionnaire data.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing questionnaire data

    question : str
        question id

    column : str
        column containing the answer

    title : str
        Plot title

    xlabel : str
        Plot xlabel

    ylabel : str
        Plot ylabel

    user : Bool or str
        If str, plot single user data
        If False, plot group level data

    Returns
    -------
    fig: plotly Figure
        A barplot summary of the questionnaire

    """
    assert isinstance(user, (type(None), str)), "user is not a boolean or string."

    # one subject
    if user is not None:
        df = df[df['user'] == user]

    df = categorize_answers(df, question, column)
    fig = plot_categories(df, title, xlabel, ylabel)
    return fig


def question_by_group(df, question, answer_column, group):
    """Plot summary barplot for questionnaire data.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing questionnaire data

    question : str
        question id

    answer_column : str
        answer_column containing the answer

    group : str
        group by this column

    Returns
    -------
    df : Pandas DataFrameGroupBy
        Dataframe a single answers column filtered by the question
        parameter and grouped by the group parameter
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(question, str), "question is not a string."
    assert isinstance(column, str), "column is not a string."
    assert isinstance(group, (type(None), str)), "group is not a boolean or string."

    df = df[df["question"] == question][[answer_column, 'group']].groupby('group')
    return df


def plot_grouped_categories(df, title=None, xlabel=None, ylabel=None, width=900, height=900):
    """Plot summary barplot for questionnaire data.

    Parameters
    ----------
    df: Pandas DataFrameGroupBy
        A grouped dataframe containing categorical data

    title : str
        Plot title

    xlabel : str
        Plot xlabel

    ylabel : str
        Plot ylabel

    width : integer
        Plot width

    height : integer
        Plot height

    Returns
    -------
    fig: plotly Figure
        Figure containing barplots of the data in each group
    """
    assert isinstance(title, str), "title is not a string."
    assert isinstance(xlabel, str), "xlabel is not a string."
    assert isinstance(ylabel, str), "ylabel is not a string."
    assert isinstance(width, int), "width is not an integer."
    assert isinstance(height, int), "height is not an integer."

    fig = go.Figure()

    for group, answer in df:
        fig.add_trace(
            go.Bar(
                name = group,
                x = [0,1,2,3,4],
                y = answer.value_counts()
            )
        )

    fig.update_layout(title = title,
                      legend_title="Groups",
                      barmode='group'
                      xaxis_title = xlabel,
                      yaxis_title = ylabel,
                      width = 900,
                      height = 500,)

    return fig


def questionnaire_grouped_summary(
    df, question, column, title=None, xlabel=None, ylabel=None, group
):
    """ Create a barplot of categorical data

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing questionnaire data

    question : str
        question id

    column : str
        column containing the answer

    title : str
        Plot title

    xlabel : str
        Plot xlabel

    ylabel : str
        Plot ylabel

    user : Bool or str
        If str, plot single user data
        If False, plot group level data

    group : str
        group by this column

    Returns
    -------
    fig: plotly Figure
        A barplot of the input data
    """

    df_filt = question_by_group(df, question, column, group)
    fig = plot_grouped_categories(
        df_filt,
        title=None, xlabel=xlabel, ylabel=ylabel,
        width=900, height=900
    )

    return fig


