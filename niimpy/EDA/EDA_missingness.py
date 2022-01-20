import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def bar(df):
    ''' Display bar chart visualization of the nullity of the given DataFrame.
    
    :param df: DataFrame to plot
    '''
    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
    # Count nullity in all columns
    nullity_counts = len(df) - df.isnull().sum()
    missing_perc = (nullity_counts / len(df))
        
    # Right y-axis: display number of instances
    
    fig = px.bar(missing_perc)
    
    fig.update_layout(title='Data frequency', xaxis_title = '', yaxis_title = '', showlegend=False)
    fig.show()
        
    
def matrix(df):
    ''' Display matrix visualization of the nullity of data.
    For now, this function assumes that the data frame is datetime indexed.
    
    :param df: DataFrame to plot
    '''

    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    
    # Create a boolean mask for the dataframe, where the null values are masked with False
    bool_mask = df.isna()
    
    # Plot the dataframe as pixel
    fig = px.imshow(bool_mask, color_continuous_scale='gray')
        
    # Update layout
    fig.update_layout(title="Data frequency.", coloraxis_showscale=False, height = 500)

    fig.show()