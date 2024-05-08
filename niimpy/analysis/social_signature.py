import pandas as pd
import numpy as np


def social_signature(df: pd.DataFrame, to_column = "to", from_column = "from", user = None, sender = 0):
    """ Calculate the social signature for a single user.
    
    Parameters
    ----------

    df : pandas.DataFrame
        Input dataframe with a Timestamp index and 'user' column, as well as to and from columns.

    to_column : str
        Column name for the recipient of the interaction.

    from_column : str
        Column name for the sender of the interaction.

    user : str
        User for which to calculate the social signature.

    sender : str or int
        The sender ID of the user. Either the subjects user name, email address, or pseudonymous ID. 
        Defaults to 0.
    
    Returns
    -------
    social_signature : pd.DataFrame
        Dataframe with social signature for the specified user.
    """

    if user is not None:
        df = df[df['user'] == user]

    if isinstance(df[to_column].iloc[0], list):
        df = df.explode(to_column)
    
    sent_by_user = df[df[from_column] == 0]
    interaction_counts = sent_by_user.groupby(to_column).size()
        
    total_interactions = interaction_counts.sum()
    social_signature = interaction_counts / total_interactions

    return social_signature
