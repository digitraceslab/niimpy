# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 14:49:22 2021

@author: arsii
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def questionnaire_summary(df, question, column, title, xlabel, ylabel, user = None, group = None,):
    """Plot summary barplot for questionnaire data.
    
    Plotting options:
        - Single subject distribution
        - Group level distribution
        - Group comparison

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
        
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
        
    group : Bool or str
        If All, plot all groups together
        If False, plot group comparions
    
    Returns
    -------
    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(question,str), "question is not a string."
    assert isinstance(column, str), "column is not a string."
    assert isinstance(title, str), "title is not a string."
    assert isinstance(xlabel, str), "xlabel is not a string."
    assert isinstance(ylabel, str), "ylabel is not a string."
    assert isinstance(user, (type(None), str)), "user is not a boolean or string."
    assert isinstance(group, (type(None), str)), "group is not a boolean or string."
    
    # one subject
    if user:
        fig = px.bar(df[(df["question"] == question) & (df['user'] == user)][column].astype("category").value_counts(sort=False))
       
    # all groups together
    elif group == 'All':
        fig = px.bar(df[df["question"] == question][column].astype("category").value_counts(sort=False))
           
    # separate barplots for each group:
    else:
        df_filt = df[df["question"] == question][[column,'group']].groupby('group')
        fig = go.Figure()

        for group, answer in df_filt:
            fig.add_trace(go.Bar(name = group,x = [0,1,2,3,4], y = answer.value_counts()))

        fig.update_layout(legend_title="Groups",
                          barmode='group')
        
    fig.update_layout(title = title,
                      xaxis_title = xlabel,
                      yaxis_title = ylabel,
                      width = 900,
                      height = 500,)
    fig.show()