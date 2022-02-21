'''
This module is rewritten based on the missingno package.
The original files can be found here: https://github.com/ResidentMario/missingno
'''

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def bar(df, columns=None, title='Data frequency', xaxis_title = '', yaxis_title = '', sampling_freq=None, sampling_method='mean'):
    ''' Display bar chart visualization of the nullity of the given DataFrame.
    
    :param df: pandas Dataframe
        Dataframe to plot
    :param columns: list, optional
        Columns from input dataframe to investigate missingness. If none is given, uses all columns.
    :param title: str
        Figure's title
    :param xaxis_title: str, optional
        x_axis's label
    :param yaxis_title: str, optional
        y_axis's label
    :param sampling_freq: str, optional
        Frequency to resample the data. Requires the dataframe to have datetime-like index. 
    :param sampling_method: str, optional
        Resampling method. Possible values: 'sum', 'mean'. Default value is 'mean'.
    Return:
        fig: Plotly figure.
    '''
    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
    def __resample(df, freq):
        resampled_df = df.resample('T').sum()
        return resampled_df

    def _missing_percentage(df):
        
        # Return each column missing percentage
        # Count nullity in all columns
        nullity_counts = len(df) - df.isnull().sum()
        missing_perc = (nullity_counts / len(df))
        return missing_perc
    
    if columns == None:
        columns = df.columns
        
    if sampling_freq:
        assert sampling_method in ['mean', 'sum'], 'Cannot recognize sampling method. Possible values: "mean", "sum".'
        if sampling_method == 'mean':
            resampled_df = df.resample(sampling_freq).mean()
        else:
            resampled_df = df.resample(sampling_freq).sum()
            
        # Transpose the dataframe so that timestamp index become columns
        resampled_df = resampled_df[columns].transpose()

        fig = px.bar(_missing_percentage(resampled_df))
    else:

        fig = px.bar(_missing_percentage(df[columns]))
    
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