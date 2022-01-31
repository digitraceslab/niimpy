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
        dataframe column sontaining question id 

    answer_column : str
        dataframe column containing the answer

    Returns
    -------
    category_counts: Pandas Dataframe
        Dataframe containing the category counts of answers
        filtered by the question
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(question, str), "question is not a string."
    assert isinstance(answer_column, str), "column is not a string."

    df = df[(df["id"] == question)][answer_column]
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
    assert isinstance(df, pd.Series), "df is not a pandas dataframe."
    assert isinstance(title, (str,type(None))), 'title is not a string or None type.'
    assert isinstance(xlabel, (str,type(None))), "xlabel is not a string or None type."
    assert isinstance(ylabel, (str,type(None))), "ylabel is not a string or None type."
    assert isinstance(width, int), "width is not an integer."
    assert isinstance(height, int), "height is not an integer."

    fig = px.bar(df)
    fig.update_layout(title = title,
                      xaxis_title = xlabel,
                      yaxis_title = ylabel,
                      width = width,
                      height = height)
    return fig

def questionnaire_summary(
    df, question, column, title=None, xlabel=None, ylabel=None, user=None, width=900, height=900 
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
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(question, str), "question is not a string."
    assert isinstance(column, str), "column is not a string."
    assert isinstance(user, (str,type(None))), "user is not a boolean or string."
    assert isinstance(title, (str, type(None))), "title is not a string or None type."
    assert isinstance(xlabel, (str,type(None))), "xlabel is not a string or None type."
    assert isinstance(ylabel, (str,type(None))), "ylabel is not a string or None type."
    assert isinstance(width, int), "width is not an integer."
    assert isinstance(height, int), "height is not an integer."

    if user is not None:
        df = df[df['user'] == user]

    df = categorize_answers(df, question, column)
    fig = plot_categories(df, title, xlabel, ylabel,width,height)
    return fig

def question_by_group(df, question, id_column = 'id', answer_column = 'answer', group='group'):
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
    assert isinstance(id_column, str), "question is not a string."
    assert isinstance(answer_column, str), "column is not a string."
    assert isinstance(group, (type(None), str)), "group is not a boolean or string."
    
    grouped = df[df[id_column] == question][[answer_column, group]].reset_index(drop=True)
    grouped = grouped.groupby([group,answer_column]).agg({answer_column:'count'}).rename(columns={answer_column:'count'}).reset_index()
    return grouped

def plot_grouped_categories(df, group, title=None, xlabel=None, ylabel=None, width=900, height=900):
    """Plot summary barplot for questionnaire data.

    Parameters
    ----------
    df: Pandas DataFrameGroupBy
        A grouped dataframe containing categorical data

    group: str
        Column used to describe group 
        
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
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(title,(type(None), str)), "title is not a string or none type."
    assert isinstance(xlabel,(type(None), str)), "xlabel is not a string or none type."
    assert isinstance(ylabel,(type(None), str)), "ylabel is not a string or none type."
    assert isinstance(width, int), "width is not an integer."
    assert isinstance(height, int), "height is not an integer."
    
    fig = px.bar(df, 
                 x="answer", 
                 y="count",
                 color=group, 
                 barmode='group',)
    
    fig.update_layout(xaxis={'categoryorder':'category ascending'},
                      title = title,
                      legend_title="Groups",
                      barmode='group',
                      xaxis_title = xlabel,
                      yaxis_title = ylabel,
                      width = width,
                      height = height)
    
    return fig

def questionnaire_grouped_summary(
    df, question, id_column ='id', answer_column = 'answer', group = 'group', title=None, xlabel=None, ylabel=None, width=900, height=900
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
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(question, str), "question is not a string."
    assert isinstance(id_column, str), "id column is not a string."
    assert isinstance(answer_column, str), "column is not a string."
    assert isinstance(group, str), "group is not a string."
    assert isinstance(title, (str,type(None))), "title is not a string or None type."
    assert isinstance(xlabel, (str,type(None))), "xlabel is not a string or None type."
    assert isinstance(ylabel, (str,type(None))), "ylabel is not a string or None type."
    assert isinstance(width, int), "width is not an integer."
    assert isinstance(height, int), "height is not an integer."
    
    df_filt = question_by_group(df, question, id_column, answer_column, group)

    fig = plot_grouped_categories(df_filt,
                                  group=group,
                                  title=title, 
                                  xlabel=xlabel, 
                                  ylabel=ylabel,
                                  width=width, 
                                  height=height)

    return fig