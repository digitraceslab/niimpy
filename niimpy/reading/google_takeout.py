import pandas as pd
from zipfile import ZipFile
import json
import os
import datetime
import email
import uuid
import warnings
from tqdm import tqdm
from multi_language_sentiment import sentiment as get_sentiment
from niimpy.preprocessing import util
import google_takeout_email as email_utils



def format_inferred_activity(data, inferred_activity, activity_threshold):
    # Format the activity type column into activity type and
    # activity inference confidence. The data is nested a few
    # layers deep, so we first need to flatten it.
    row_index = ~data["activity"].isna()
    activities = data.loc[row_index, "activity"]
    activities = activities.str[0].str["activity"]

    if inferred_activity == "highest":
        # Get the first in the list of activity types
        activity_type = activities.str[0].str["type"]
        activity_confidence = activities.str[0].str["confidence"]
        data.loc[row_index, "activity_type"] = activity_type
        data.loc[row_index, "activity_inference_confidence"] = activity_confidence
    
    elif inferred_activity == "all" or inferred_activity == "threshold":
        # Explode the list of activity types into multiple rows
        # and get the new index
        data.loc[row_index, "activity"] = activities
        data = data.explode("activity")
        row_index = ~data["activity"].isna()
        activities = data.loc[row_index, "activity"]
        
        # Extract type and confidence into columns
        activity_type = activities.str["type"]
        activity_confidence = activities.str["confidence"]
        data.loc[row_index, "activity_type"] = activity_type
        data.loc[row_index, "activity_inference_confidence"] = activity_confidence

    if inferred_activity == "threshold":
        # remove rows with no activity type
        data.dropna(subset=["activity_type"], inplace=True)
        # remove rows with confidence below the threshold
        rows = data["activity_inference_confidence"] < activity_threshold
        data = data.loc[~rows, :]
    
    # Drop the original activity column
    data.drop(["activity"], axis=1, inplace=True)
    return data




def location_history(
        zip_filename,
        inferred_activity="highest",
        activity_threshold=0,
        drop_columns=True,
        user = None
    ):
    """  Read the location history from a google takeout zip file.

    The returned dataframe contains the expected latitude, longitude,
    altitude, velocity, heading, accuracy and verticalAccuracy. 
    Additionally, it contains
    an inferred location (latitude and longitude) and a placeId.
    the returned dataframe contains an inferred activity type
    and confidence in the inference. 
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.

    keep_activity : str, optional
        How to choose the inferred activity type to keep.
        - "highest": Only one activity with the highest confidence value 
          is kept. This is the default.
        - "all": All activity types with non-zero confidence values are
          kept as separate rows. Also keeps rows with no activity type.
        - "threshold": Set an confidence threshold for keeping an 
          inferred activity type. Measurements with no activity type are dropped.
    
    activity_threshold: int, optional
        Used when keep_activity is "threshold". The threshold for 
        keeping an inferred activity type.

    drop_columns: bool, optional
        Whether all raw data columns should be kept. This includes lists of
        wifi check points and mostly null device and OS data.

    Returns
    -------

    data : pandas.DataFrame
    """
    
    column_name_map = {'deviceTag': "device"}
    drop_columns = ['deviceDesignation', 'activeWifiScan.accessPoints', 'locationMetadata', 'osLevel']

    # Read json data from the zip file and convert to pandas DataFrame.
    try:
        zip_file = ZipFile(zip_filename)
        json_data  = zip_file.read("Takeout/Location History/Records.json")
    except KeyError:
        return pd.DataFrame()
    json_data = json.loads(json_data)
    data = pd.json_normalize(json_data["locations"])
    data = pd.DataFrame(data)

    # Convert timestamp to datetime
    data["timestamp"] = pd.to_datetime(data["timestamp"], format='ISO8601')

    # Format latitude and longitude as floating point numbers
    data["latitude"] = data["latitudeE7"] / 10000000
    data["longitude"] = data["longitudeE7"] / 10000000
    data.drop(["latitudeE7", "longitudeE7"], axis=1, inplace=True)

    # Extract inferred location and convert
    if "inferredLocation" in data.columns:
        row_index = ~data["inferredLocation"].isna()
        inferred_location = data.loc[row_index, "inferredLocation"].str[0]
        data.loc[row_index, "inferred_latitude"] = inferred_location.str["latitudeE7"] / 10000000
        data.loc[row_index, "inferred_longitude"] = inferred_location.str["longitudeE7"] / 10000000
        data.drop("inferredLocation", axis=1, inplace=True)

    
    if "activity" in data.columns:
        data = format_inferred_activity(data, inferred_activity, activity_threshold)
    
    data.set_index("timestamp", inplace=True)
    data.drop(drop_columns, axis=1, inplace=True,  errors='ignore')
    data.rename(columns=column_name_map, inplace=True)
    util.format_column_names(data)

    if user is None:
        user = uuid.uuid1()
    data["user"] = user
    return data


def activity(zip_filename, user=None):
    """ Read activity data from a Google Takeout zip file. 
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.


    Returns
    -------

    data : pandas.DataFrame
    """

    # Read the csv files in the activity directory and concatenate
    dfs = []
    with ZipFile(zip_filename) as zip_file:
        for filename in zip_file.namelist():
            # Skip the file with daily agregated data for now.
            if filename.endswith('Daily activity metrics.csv'):
                continue

            # Read the more finegrained data for each date
            if filename.startswith("Takeout/Fit/Daily activity metrics/") and filename.endswith(".csv"):
                with zip_file.open(filename) as csv_file:
                    data = pd.read_csv(csv_file)
                    date = os.path.basename(filename).replace(".csv", "")
                    data["date"] = date
                    dfs.append(data)

    if len(dfs) == 0:
        return pd.DataFrame()
    
    data = pd.concat(dfs)

    # Format start time and end time columns with date. Set start time as the
    # timestamp
    data["start_time"] = pd.to_datetime(data["date"] + ' ' + data["Start time"])
    data["end_time"] = pd.to_datetime(data["date"] + ' ' + data["End time"])
    data["timestamp"] = data["start_time"]
    data.set_index('timestamp', inplace=True)
    data.drop(["Start time", "End time", "date"], axis=1, inplace=True)

    # Fix date where end time is midnight
    row_index = data["end_time"].dt.time == datetime.time(0)
    data.loc[row_index, "end_time"] = data.loc[row_index, "end_time"] + datetime.timedelta(days=1)

    # Format durations as timedelta
    for col in data.columns:
        if col.endswith("duration (ms)"):
            new_name = col.replace(" (ms)", "")
            data[new_name] = pd.to_timedelta(data[col], unit="microseconds")
            data.drop(col, axis=1, inplace=True)

    # Format column names
    util.format_column_names(data)
    
    if user is None:
        user = uuid.uuid1()
    data["user"] = user

    return data


def pseudonymize_addresses(df, user_email = None):
    """ Replace email address strings with numerical IDs. The IDs
    start from 1 and run in order encountered.
    
    If user_email is provided, that email is labeled as 0.
    """
    address_dict = {"": pd.NA}
    if user_email is not None:
        address_dict[user_email] = 0
        
    addresses = set(df["from"].explode().unique())
    addresses |= set(df["to"].explode().unique())
    addresses |= set(df["cc"].explode().unique())
    addresses |= set(df["bcc"].explode().unique())
    addresses = list(addresses)
    for i, k in enumerate(addresses):
        if k not in address_dict:
            address_dict[k] = i+1

    def replace_to_list(addresses):
        return [address_dict[address] for address in addresses]
        
    df["to"] = df["to"].apply(replace_to_list)
    df["from"] = df["from"].apply(lambda x: address_dict[x])
    df["cc"] = df["cc"].apply(replace_to_list)
    df["bcc"] = df["bcc"].apply(replace_to_list)
    return df


def pseudonymize_message_id(df):
    """ Replace message ID strings with numerical IDs. The IDs
    start from 0 and run in order encountered.
    """
    message_id_dict = {"": pd.NA}
        
    message_ids = set(df["message_id"].explode().unique())
    message_ids |= set(df["in_reply_to"].explode().unique())
    message_ids = list(message_ids)
    for i, k in enumerate(message_ids):
        if k not in message_id_dict:
            message_id_dict[k] = i

    df["message_id"] = df["message_id"].apply(lambda x: message_id_dict[x])
    df["in_reply_to"] = df["in_reply_to"].apply(lambda x: message_id_dict[x])
    return df


def infer_user_email(df):
    """Try to infer the user email. Since the user appears on
    every row, their address should be the most common.
    
    df: pandas.DataFrame
        A dataframe with "from" column containing a single email
        address and a "to" column containing a list of addresses.
    """
    
    addresses = df.apply(lambda row: row["to"] + [row["from"]], axis=1)
    address_counts = addresses.explode().value_counts()
    if address_counts.iloc[1] == address_counts.iloc[0]:
        warnings.warn("Could not infer user email address.")
        return None
    return address_counts.keys()[0]


class email_file():
    """ Opens both Google Takeout zip files and .mbox files. """
    def __init__(self, filename):
        self.filename = filename
        if filename.endswith(".zip"):
            self.zip_file = ZipFile(filename)
            internal_filename = "Takeout/Mail/All mail Including Spam and Trash.mbox"
            self.mailbox_file = self.zip_file.open(internal_filename)
        elif filename.endswith(".mbox"):
            self.mailbox_file = open(filename)
        else:
            raise ValueError("Unknown file")
        
        self.mailbox = email_utils.MailboxReader(self.mailbox_file)

    @property
    def messages(self):
        return self.mailbox.messages

    def close(self):
        self.mailbox.close()
        self.mailbox_file.close()
        if self.filename.endswith(".zip"):
            self.zip_file.close()


def email_activity(
        filename,
        pseudonymize=True,
        user=None,
        sentiment=False,
        sentiment_batch_size = 100,
    ):
    """ Extract message header data from the GMail inbox in
    a Google Takeout zip file.

    Note: there are several alternate spellings of email fields below.
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.
    pseudonymize: bool (optional)
        Replace senders and receivers with ID numbers. Defaults to True.
    user: str (optiona)
        A user ID that is added as a column to the dataframe. In not
        provided, a random user UI is generated.
    sentiment: Bool (optiona)
        Include sentiment analysis of the message content
        
    Returns
    -------

    data : pandas.DataFrame
    """
    try:
        mailbox = email_file(filename)
    except KeyError:
        return pd.DataFrame()

    data = []
    for message in mailbox.messages:
        # Several fields have different alternate spellings.
        # We use message.get to check all we have encountered
        # so far.

        # We use the date entry as the timestamp
        try:
            timestamp = message.get("Date", "")
            timestamp = message.get("date", timestamp)
            if timestamp:
                timestamp = email.utils.parsedate_to_datetime(timestamp)
            timestamp = pd.to_datetime(timestamp)
        except:
            warnings.warn(f"Could not parse message timestamp: {received}")

        # Extract received time and convert to datetime.
        # Entries are separated by ";" and the date is the last 
        # one
        received = message.get("received", "")
        received = message.get("received", received)
        received = received.split(";")[-1].strip()
        try:
            if received:
                received = email.utils.parsedate_to_datetime(received)
            received = pd.to_datetime(received)
        except:
            warnings.warn(f"Failed to format received time: {received}")

        in_reply_to = message.get("In-Reply-To", "")
        in_reply_to = message.get("In-reply-to", in_reply_to)
        in_reply_to = message.get("in-reply-to", in_reply_to)
        in_reply_to = message.get("Reply-To", in_reply_to)
        in_reply_to = message.get("Reply-to", in_reply_to)
        in_reply_to = message.get("Mail-Reply-To", in_reply_to)
        in_reply_to = message.get("Mail-Followup-To", in_reply_to)

        cc = str(message.get("CC", ""))
        cc = str(message.get("Cc", cc))
        cc = str(message.get("cc", cc))
        bcc = str(message.get("Bcc", ""))
        bcc = str(message.get("BCC", bcc))
        bcc = str(message.get("BCc", bcc))
        bcc = str(message.get("bcc", bcc))

        message_id = str(message.get("Message-ID", ""))
        message_id = str(message.get("Message-Id", message_id))
        message_id = str(message.get("Message-id", message_id))
        message_id = str(message.get("message-id", message_id))

        from_address = str(message.get("From", ""))
        from_address = str(message.get("FROM", from_address))
        from_address = str(message.get("from", from_address))

        to_address = str(message.get("To", ""))
        to_address = str(message.get("TO", to_address))
        to_address = str(message.get("to", to_address))
        to_address = str(message.get("Sender", to_address))
        to_address = str(message.get("sender", to_address))

        content = email_utils.extract_content(message)

        row = {
            "timestamp": timestamp,
            "received": received,
            "from": email_utils.strip_address(from_address),
            "to": email_utils.parse_address_list(to_address),
            "cc": email_utils.parse_address_list(cc),
            "bcc": email_utils.parse_address_list(bcc),
            "message_id": message_id,
            "in_reply_to": in_reply_to,
            "character_count": len(content),
            "word_count": len(content.split())
        }
        data.append(row)

    mailbox.close()

    df = pd.DataFrame(data)

    if pseudonymize:
        user_email = infer_user_email(df)
        df = pseudonymize_addresses(df, user_email)
        df = pseudonymize_message_id(df)

    if user is None:
        user = uuid.uuid1()
    df["user"] = user

    df.set_index("timestamp", inplace=True)

    # Run sentiment analysis if requested. This might take some time.
    if sentiment:
        print(f"Running sentiment analysis on {len(df)} messages.")
        content_batch = []
        sentiments = []
        mailbox = email_file(filename)

        with tqdm(total=len(df)) as pbar:
            for message in mailbox.messages:
                content_batch.append(email_utils.extract_content(message))
                if len(content_batch) >= sentiment_batch_size:
                    sentiments += get_sentiment(content_batch)
                    content_batch = []
                    pbar.update(sentiment_batch_size)
        if len(content_batch) >= 0:
            sentiments += get_sentiment(content_batch)

        mailbox.close()

        labels = [s["label"] for s in sentiments]
        scores = [s["score"] for s in sentiments]
        df["sentiment"] = labels
        df["sentiment_score"] = scores

    return df


def chat(
        zip_filename, user=None,
        sentiment=False, sentiment_batch_size = 100,
        pseudonymize=True,
    ):
    """ Read Google chat messages from a Google Takeout zip file.

    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.


    Returns
    -------

    data : pandas.DataFrame
    """

    # Each group chat is stored in a separate file. We read all of them.
    dfs = []
    group_index = 0
    with ZipFile(zip_filename) as zip_file:
        for filename in zip_file.namelist():
            # Read the more finegrained data for each date
            if filename.startswith("Takeout/Google Chat/Groups/") and filename.endswith("messages.json"):
                with zip_file.open(filename) as json_file:
                    data = json.load(json_file)
                    data["chat_group"] = group_index
                    group_index += 1
                    # flatten the nested json data
                    print(data["messages"])
                    data = pd.json_normalize(data["messages"])
                    dfs.append(data)

    if len(dfs) == 0:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["created_date"])
    df.set_index("timestamp", inplace=True)
    df.drop("created_date", axis=1, inplace=True)

    df["character_count"] = df["text"].apply(len)
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))

    if pseudonymize:
        user_email = df["creator.email"].value_counts().idxmax()
        addresses = set(df["creator.email"].unique())
        address_map = {user_email: 0}
        for i, address in enumerate(addresses):
            if address not in address_map:
                address_map[address] = i+1
        
        df["creator.email"] = df["creator.email"].apply(lambda x: address_map[x])

        user_name = df["creator.name"].value_counts().idxmax()
        names = set(df["creator.name"].unique())
        name_map = {user_name: 0}
        for i, name in enumerate(names):
            if name not in name_map:
                name_map[name] = i+1
        
        df["creator.name"] = df["creator.name"].apply(lambda x: name_map[x])

    if sentiment:
        content_batch = []
        sentiments = []
        with tqdm(total=len(df)) as pbar:
            for message in df["text"]:
                content_batch.append(message)
                if len(content_batch) >= sentiment_batch_size:
                    sentiments += get_sentiment(content_batch)
                    content_batch = []
                    pbar.update(sentiment_batch_size)
            if len(content_batch) >= 0:
                sentiments += get_sentiment(content_batch)

        labels = [s["label"] for s in sentiments]
        scores = [s["score"] for s in sentiments]
        df["sentiment"] = labels
        df["sentiment_score"] = scores

    df.drop("text", axis=1, inplace=True)

    return df



