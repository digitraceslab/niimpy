'''
This module is rewritten based on the missingno package.
The original files can be found here: https://github.com/ResidentMario/missingno
'''

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def bar(df, title='Data frequency', xaxis_title = '', yaxis_title = ''):
    ''' Display bar chart visualization of the nullity of the given DataFrame.
    
    :param df: DataFrame to plot
    
    Return:
        fig: Plotly figure.
    '''
    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
    def _missing_percentage(df):
        
        # Return each column missing percentage
        # Count nullity in all columns
        nullity_counts = len(df) - df.isnull().sum()
        missing_perc = (nullity_counts / len(df))
        return missing_perc
    
    # Right y-axis: display number of instances
    
    fig = px.bar(_missing_percentage(df))
    
    fig.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title, showlegend=False)
    return fig
        
    
def matrix(df, height=500, title='Data frequency'):
    ''' Retu matrix visualization of the nullity of data.
    For now, this function assumes that the data frame is datetime indexed.
    
    :param df: DataFrame to plot
    
    :return: Plotly figure
    '''

    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
    # Create a boolean mask for the dataframe, where the null values are masked with False
    bool_mask = df.isna()
    
    # Plot the dataframe as pixel
    fig = px.imshow(bool_mask, color_continuous_scale='gray')
        
    # Update layout
    fig.update_layout(title=title, coloraxis_showscale=False, height=height)

    return fig

def heatmap(df, height=800, width=800):
    ''' Return 'plotly' heatmap visualization of the nullity correlation of the Dataframe.
    
    :param df: DataFrame to plot
    
    :return: Plotly figure
    '''
    
    # Remove completely filled or completely empty variables.
    df = df.iloc[:, [i for i, n in enumerate(np.var(df.isnull(), axis='rows')) if n > 0]]

    # Create and mask the correlation matrix. Construct the base heatmap.
    corr_mat = df.isnull().corr()
    
    fig = go.Figure(data=go.Heatmap(z=corr_mat, x = df.columns, y=df.columns)) 
    
    fig.update_layout(height=height, width=width)
    return fig