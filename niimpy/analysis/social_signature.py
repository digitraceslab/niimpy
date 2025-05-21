import pandas as pd
import numpy as np


def social_signature(df: pd.DataFrame, to_column = "to", from_column = "from", include_received=True, user = None, user_id = 0):
    """ Calculate the social signature for a single user.
    
    Parameters
    ----------

    df : pandas.DataFrame
        Input dataframe with a Timestamp index and 'user' column, as well as to and from columns.

    to_column : str
        Column name for the recipient of the interaction.

    from_column : str
        Column name for the sender of the interaction.

    include_received : bool
        If True, include interactions where the user is the recipient. If False, only include interactions
        where the user is the sender. Defaults to True.

    user : str
        User for which to calculate the social signature.

    user_id : str or int
        The numerical ID of the user. Either the subjects user name, email address, or pseudonymous ID. 
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

    to_rows = df[from_column] == user_id
    df.loc[to_rows, "contact"] = df.loc[to_rows, to_column]
    if include_received:
        from_rows = df[to_column] == user_id
        df.loc[from_rows, "contact"] = df.loc[from_rows, from_column]
        
    # Filter out rows where the user is not in the to or from columns
    df = df[df["contact"].notna()]

    interaction_counts = df.groupby("contact").size()

    total_interactions = interaction_counts.sum()
    social_signature = interaction_counts / total_interactions
    social_signature = social_signature.sort_values(ascending=False)

    return social_signature
