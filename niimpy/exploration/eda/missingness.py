'''
This module is rewritten based on the missingno package.
The original files can be found here: https://github.com/ResidentMario/missingno
'''

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff

from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import squareform

def bar_count(df, columns=None, title='Data frequency', xaxis_title = '', yaxis_title = '', sampling_freq='h'):
    ''' Display bar chart visualization of the nullity of the given DataFrame.
    
    Parameters
    ----------
    df: pandas Dataframe
        Dataframe to plot
    columns: list, optional
        Columns from input dataframe to investigate missingness. If none is given, uses all columns.
    title: str
        Figure's title
    xaxis_title: str, optional
        x_axis's label
    yaxis_title: str, optional
        y_axis's label
    sampling_freq: str, optional
        Frequency to resample the data. Requires the dataframe to have datetime-like index. Possible values: 'h', 'min'

    Returns
    -------
    fig: Plotly figure.
    '''
    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
    if columns == None:
        columns = df.columns
       
    resampled_df = df.resample(sampling_freq).count()
    
    if sampling_freq == 'h':
        resampled_df = resampled_df.groupby([resampled_df.index.hour])[columns].sum()
        fig = px.bar(resampled_df)
        
        # Define xticks
        tickvals = list(range(0, 24))
        ticktexs = []
        for tick in tickvals:
            ticktexs.append("{:02d}:00:00".format(tick))
            
        fig.update_layout(
            xaxis = dict(
                tickangle= 90,
                tickmode = 'array',
                tickvals = tickvals,
                ticktext = ticktexs,
                dtick = 5
            )
        )

    elif sampling_freq == 'min':
        resampled_df = resampled_df.groupby([resampled_df.index.minute])[columns].sum()
            
        fig = px.bar(resampled_df)
        
        # Define xticks
        tickvals = list(range(0, 60))
        ticktexs = []
        for tick in tickvals:
            ticktexs.append("{:02d}:00".format(tick))
            
        fig.update_layout(
            xaxis = dict(
                tickmode = 'array',
                tickvals = tickvals,
                ticktext = ticktexs,
                dtick = 5
            )
        )
        
    fig.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title, showlegend=False)
    
    return fig

def bar(df, columns=None, title='Data frequency', xaxis_title = '', yaxis_title = '', sampling_freq=None, sampling_method='mean'):
    ''' Display bar chart visualization of the nullity of the given DataFrame.
    
    Parameters
    ----------
    df: pandas Dataframe
        Dataframe to plot
    columns: list, optional
        Columns from input dataframe to investigate missingness. If none is given, uses all columns.
    title: str
        Figure's title
    xaxis_title: str, optional
        x_axis's label
    yaxis_title: str, optional
        y_axis's label
    sampling_freq: str, optional
        Frequency to resample the data. Requires the dataframe to have datetime-like index. Possible values: 'h', 'min'
    sampling_method: str, optional
        Resampling method. Possible values: 'sum', 'mean'. Default value is 'mean'.
    Returns
    -------
    fig: Plotly figure.
    '''
    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
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


def matrix(df, height=500, title='Data frequency', xaxis_title = '', yaxis_title = '', sampling_freq=None, sampling_method='mean'):
    ''' Return matrix visualization of the nullity of data.
    For now, this function assumes that the data frame is datetime indexed.
    
    Parameters
    ----------
    df: pandas Dataframe
        Dataframe to plot
    columns: list, optional
        Columns from input dataframe to investigate missingness. If none is given, uses all columns.
    title: str
        Figure's title
    xaxis_title: str, optional
        x_axis's label
    yaxis_title: str, optional
        y_axis's label
    sampling_freq: str, optional
        Frequency to resample the data. Requires the dataframe to have datetime-like index. Possible values: 'h', 'min'
    sampling_method: str, optional
        Resampling method. Possible values: 'sum', 'mean'. Default value is 'mean'.
    Returns
    -------
    fig: Plotly figure.
    '''

    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
    if sampling_freq:
        assert sampling_method in ['mean', 'sum'], 'Cannot recognize sampling method. Possible values: "mean", "sum".'
        if sampling_method == 'mean':
            resampled_df = df.resample(sampling_freq).mean()
        else:
            resampled_df = df.resample(sampling_freq).sum()
    else:
        resampled_df = df.copy()
        
    # Create a boolean mask for the dataframe, where the null values are masked with False
    bool_mask = resampled_df.isna()
    
    # Plot the dataframe as pixel
    fig = px.imshow(bool_mask, color_continuous_scale='gray')
        
    # Update layout
    fig.update_layout(title=title, xaxis_title = xaxis_title, yaxis_title = yaxis_title,
                      coloraxis_showscale=False, height=height)

    return fig

def heatmap(df, height=800, width=800, title='', xaxis_title='', yaxis_title=''):
    ''' Return 'plotly' heatmap visualization of the nullity correlation of the Dataframe.
    
     Parameters
    ----------
    df: pandas Dataframe
        Dataframe to plot
    width: int:
        Figure's width
    height: int:
        Figure's height
    Returns
    -------
    fig: Plotly figure.
    '''
    
    # Remove completely filled or completely empty variables.
    df = df.iloc[:, [i for i, n in enumerate(np.var(df.isnull(), axis='rows')) if n > 0]]

    # Create and mask the correlation matrix. Construct the base heatmap.
    corr_mat = df.isnull().corr()
    
    # Calculate dissimilarity distance. 
    # Dissimilarity is close to zero if correlation is close to 1 or -1. 
    dissimilarity = 1 - abs(corr_mat)
    labels = df.columns

    # Initialize figure by creating upper dendrogram
    fig = ff.create_dendrogram(dissimilarity, orientation='bottom', labels=labels)
    for i in range(len(fig['data'])):
        fig['data'][i]['yaxis'] = 'y2'

    # Create Side Dendrogram
    dendro_side = ff.create_dendrogram(dissimilarity, orientation='right', labels=labels)
    dendro_side.for_each_trace(lambda trace: trace.update(visible=False))
    for i in range(len(dendro_side['data'])):
        dendro_side['data'][i]['xaxis'] = 'x2'

    # Add Side Dendrogram Data to Figure
    for data in dendro_side['data']:
        fig.add_trace(data)

    # Create Heatmap
    dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
    dendro_vals =  dendro_side['layout']['yaxis']['tickvals']

    heat_data = corr_mat.reindex(columns=dendro_leaves)
    heat_data = heat_data.reindex(dendro_leaves)
    
    heatmap = [
        go.Heatmap(
            x = dendro_leaves,
            y = dendro_leaves,
            z = heat_data,
            colorscale = 'Blues'
        )
    ]

    heatmap[0]['x'] = fig['layout']['xaxis']['tickvals']
    heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

    # Add Heatmap Data to Figure
    for data in heatmap:
        fig.add_trace(data)
    
    # Edit Layout
    fig.update_layout({'width':width, 
                       'height':height,
                       'showlegend':False, 
                       'hovermode': 'closest',
                       'title':title, 
                       'xaxis_title':xaxis_title, 
                       'yaxis_title':yaxis_title})
    # Edit xaxis
    fig.update_layout(xaxis={'domain': [.15, 1],
                              'mirror': False,
                              'showgrid': False,
                              'showline': False,
                              'zeroline': False,
                              'ticks':""})
    # Edit xaxis2
    fig.update_layout(xaxis2={'domain': [0, .15],
                               'mirror': False,
                               'showgrid': False,
                               'showline': False,
                               'zeroline': False,
                               'showticklabels': False,
                               'ticks':""})

    # Edit yaxis
    fig.update_layout(yaxis={'domain': [0, .85],
                             'mirror': False,
                             'showgrid': False,
                             'showline': False,
                             'zeroline': False,
                             'ticks': "",
                             'tickmode': 'array',
                             'ticktext': dendro_leaves,
                             'tickvals': dendro_vals})
    # Edit yaxis2
    fig.update_layout(yaxis2={'domain':[.825, .975],
                               'mirror': False,
                               'showgrid': False,
                               'showline': False,
                               'zeroline': False,
                               'showticklabels': False,
                               'ticks':""})

    return fig
