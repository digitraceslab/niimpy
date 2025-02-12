import pandas as pd
from zipfile import ZipFile
import json
import os
import numpy as np
import email
import uuid
import warnings
import re

from tqdm import tqdm
from bs4 import BeautifulSoup
from niimpy.reading import util
import google_takeout_email as email_utils
from niimpy.reading.html_iterator import ContentDivIterator

try:
    from multi_language_sentiment import sentiment as get_sentiment
except ImportError:
    def get_sentiment(*args, **kwargs):
        raise ImportError("Sentiment analysis requested, but the optional dependency 'sentiment' is not installed. To install it, run `pip install niimpy[sentiment]`")


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



def read_json_after_timestamp(zip_file, filename, start_date):
    """ Read the json file from the zip file line by line and discard
    entries with timestamp before start_date. The dictionary contains
    a "locations" list. Each entry takes multiple lines and needs to
    be read fully before including or discarding it.
    
    Parameters
    ----------
    zip_file : zipfile.ZipFile
        The zip file object.
    filename : str
        The name of the file in the zip file.
    start_date : datetime.datetime
        The timestamp to filter by.
    
    Returns
    -------
    data : list
        A list of dictionaries with json data.
    """

    with zip_file.open(filename) as json_file:
        data = []
        entry = ""
        depth = 0
        for line in json_file:
            if isinstance(line, bytes):
                line = line.decode()

            if '"locations":' in line:
                # list started
                data = []
                depth = 0
                entry = ""
                # anything after the first "[" is part of the list
                line = '['.join(line.split("[")[1:])

            for char in line:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        entry += char
                        entry = json.loads(entry)
                        if pd.to_datetime(entry["timestamp"], format='ISO8601') > start_date:
                            data.append(entry)
                        entry = ""
                        char = ""
                if depth > 0:
                    entry += char
                    
                        
    return data


def location_history(
        zip_filename,
        inferred_activity="highest",
        activity_threshold=0,
        drop_columns=True,
        user = None,
        start_date = None,
        end_date = None,
        timezone = "Europe/Helsinki"
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
        filename = "Takeout/Location History (Timeline)/Records.json"
        if start_date is not None:
            json_data = read_json_after_timestamp(zip_file, filename, start_date)
        else:
            json_data  = zip_file.read(filename)
            json_data = json.loads(json_data)["locations"]
    except KeyError:
        return pd.DataFrame()
    data = pd.json_normalize(json_data)
    data = pd.DataFrame(data)

    # Convert timestamp to datetime
    data["timestamp"] = pd.to_datetime(data["timestamp"], format='ISO8601')

    # Filter by end date
    if end_date is not None:
        data = data[data["timestamp"] < end_date]

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
    util.set_timezone(data, tz=timezone)

    if user is None:
        user = uuid.uuid1()
    data["user"] = user
    return data


def activity(
    zip_filename,
    user=None,
    timezone = 'Europe/Helsinki',
    start_date = None,
    end_date = None
):
    """ Read activity daily data from a Google Takeout zip file. 
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.
    user: str (optional)
        A user ID that is added as a column to the dataframe. If not provided,
        a random user UI is generated.
    start_date : datetime.datetime, optional
        The start date for the data. If provided, only data after this date is
        included.
    end_date : datetime.datetime, optional
        The end date for the data. If provided, only data before this date is
        included.

    Returns
    -------
    data : pandas.DataFrame
    """

    # Read the csv files in the activity directory and concatenate
    with ZipFile(zip_filename) as zip_file:
        filename = None
        for f in zip_file.namelist():
            # Skip the file with daily agregated data for now.
            if f.endswith('Daily activity metrics.csv'):
                filename = f
                break

        if filename is None:
            return pd.DataFrame()
        
        # Read the more fine grained data for each date
        data = pd.read_csv(zip_file.open(filename))
    
    data["timestamp"] = pd.to_datetime(data["Date"])

    data.set_index('timestamp', inplace=True)
    util.format_column_names(data)
    util.set_timezone(data, tz=timezone)

    if start_date is not None:
        data = data[data.index >= start_date]
    
    if end_date is not None:
        data = data[data.index <= end_date]

    if user is None:
        user = uuid.uuid1()
    data["user"] = user

    return data


def pseudonymize_addresses(df, user_email = None):
    """ Replace email address strings with numerical IDs. The IDs
    start from 1 and run in order encountered.
    
    If user_email is provided, that email is labeled as 0.
    Label "" as pd.NA.
    """
    address_dict = {"": pd.NA}
    if user_email is not None:
        address_dict[user_email] = 0
        
    addresses = set(df["from"].explode().unique())
    addresses |= set(df["to"].explode().unique())
    addresses |= set(df["cc"].explode().unique())
    addresses |= set(df["bcc"].explode().unique())
    addresses = list(addresses)

    address_dict = {k: i for i, k in enumerate(addresses, 1)}
    if user_email is not None:
        address_dict[user_email] = 0
    address_dict[""]= pd.NA

    df["to"] = df["to"].apply(lambda x: [address_dict[k] for k in x])
    df["from"] = df["from"].apply(lambda x: address_dict[x])
    df["cc"] = df["cc"].apply(lambda x: [address_dict[k] for k in x])
    df["bcc"] = df["bcc"].apply(lambda x: [address_dict[k] for k in x])
    return df


def pseudonymize_message_id(df):
    """ Replace message ID strings with numerical IDs. The IDs
    start from 0 and run in order encountered. Message ids are
    found in message_id and in_reply_to columns.

    map "" to pd.NA.
    """
    message_ids = set(df["message_id"].explode().unique())
    message_ids |= set(df["in_reply_to"].explode().unique())
    message_ids = list(message_ids)

    message_id_dict = {k: i for i, k in enumerate(message_ids)}
    message_id_dict[""] = pd.NA

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


def sentiment_analysis_from_email(
        df,
        filename,
        sentiment_batch_size=100,
        start_date=None,
        end_date=None,
        timezone = "Europe/Helsinki"
    ):
    """ Run sentiment analysis on the content of the email messages
    in the dataframe. """
    content_batch = []
    sentiments = []
    mailbox = email_file(filename)

    with tqdm(total=len(df)) as pbar:
        for message in mailbox.messages:
            try:
                timestamp = message.get("Date", "")
                timestamp = message.get("date", timestamp)
                if timestamp:
                    timestamp = email.utils.parsedate_to_datetime(timestamp)
                timestamp = pd.to_datetime(timestamp)
                if start_date is not None and timestamp < start_date:
                    continue
                if end_date is not None and timestamp > end_date:
                    continue
            except:
                # Warning should already have been raised
                continue

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
    util.set_timezone(df, tz=timezone)

    return df


def email_activity(
        filename,
        pseudonymize=True,
        user=None,
        sentiment=False,
        sentiment_batch_size = 100,
        start_date = None,
        end_date = None,
        timezone = "Europe/Helsinki"
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
    sentiment_batch_size: int (optional)
        The number of messages to run sentiment analysis on at a time.
        Defaults to 100.
    start_date : datetime.datetime, optional
        The start date for the data. If provided, only data after this date is
        included.
    end_date : datetime.datetime, optional
        The end date for the data. If provided, only data before this date is
        included.
        
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
            if start_date is not None and timestamp < start_date:
                continue
            if end_date is not None and timestamp > end_date:
                continue
        except:
            warnings.warn(f"Could not parse message timestamp: {received}")
            continue

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
            "word_count": len(content.split()),
        }
        data.append(row)

    mailbox.close()

    df = pd.DataFrame(data)

    user_email = infer_user_email(df)
    df.loc[df["from"] != user_email, "message_type"] = "incoming"
    df.loc[df["from"] == user_email, "message_type"] = "outgoing"

    if pseudonymize:
        
        df = pseudonymize_addresses(df, user_email)
        df = pseudonymize_message_id(df)

    if user is None:
        user = uuid.uuid1()
    df["user"] = user

    df.set_index("timestamp", inplace=True)
    util.format_column_names(df)
    util.set_timezone(df, tz=timezone)

    # Run sentiment analysis if requested. This might take some time.
    if sentiment:
        print(f"Running sentiment analysis on {len(df)} messages.")
        sentiment_analysis_from_email(df, filename, sentiment_batch_size, start_date, end_date)

    return df



def sentiment_analysis_from_text_column(df,
        text_content_column,
        sentiment_batch_size=100,
        timezone = "Europe/Helsinki"
    ):
    """ Run sentiment analysis on a dataframe with text content
    and add the results as new columns. """
    content_batch = []
    sentiments = []
    with tqdm(total=len(df)) as pbar:
        for message in df[text_content_column]:
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
    util.format_column_names(df)
    util.set_timezone(df, tz=timezone)
    return df




def chat(
        zip_filename, user=None,
        sentiment=False, sentiment_batch_size = 100,
        pseudonymize=True,
        start_date = None,
        end_date = None,
        timezone = "Europe/Helsinki"
    ):
    """ Read Google chat messages from a Google Takeout zip file.

    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.
    user: str (optiona)
        A user ID that is added as a column to the dataframe. In not
        provided, a random user UI is generated.
    sentiment: Bool (optional)
        Include sentiment analysis of the message content
    sentiment_batch_size: int (optional)
        The number of messages to send to the sentiment analysis
        service in each batch. Defaults to 100.
    pseudonymize: bool (optional)
        Replace senders and receivers with ID numbers. Defaults to True.
    start_date : datetime.datetime, optional
        The start date for the data. If provided, only data after this date is
        included.
    end_date : datetime.datetime, optional
        The end date for the data. If provided, only data before this date is
        included.

    Returns
    -------

    data : pandas.DataFrame
    """

    dfs = []
    group_index = 0
    user_emails = []
    user_names = []
    with ZipFile(zip_filename) as zip_file:
        # Find the user email from Takeout/Google Chat/Users/*/user_info.json
        for filename in zip_file.namelist():
            if filename.startswith("Takeout/Google Chat/Users/") and filename.endswith("user_info.json"):
                with zip_file.open(filename) as json_file:
                    user_info = json.load(json_file)
                    user_emails.append(user_info["user"]["email"])
                    user_names.append(user_info["user"]["name"])
        # Each group chat is stored in a separate file. We read all of them.
        for filename in zip_file.namelist():
            # Read the more finegrained data for each date
            if filename.startswith("Takeout/Google Chat/Groups/") and filename.endswith("messages.json"):
                with zip_file.open(filename) as json_file:
                    data = json.load(json_file)["messages"]
                    for i in range(len(data)):
                        data[i]["chat_group"] = group_index
                    group_index += 1
                    # flatten the nested json data
                    data = pd.json_normalize(data)
                    dfs.append(data)

    if len(dfs) == 0:
        return pd.DataFrame()
    
    if len(user_emails) > 1:
        warnings.warn("Multiple user emails found. Using the first one.")
    user_email = user_emails[0]
    user_name = user_names[0]
    
    # create dataframe and set index. Timestamp is formatted as Tuesday, January 30, 2024 at 1:27:33 PM UTC
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["created_date"], format="%A, %B %d, %Y at %I:%M:%S %p %Z")
    df.set_index("timestamp", inplace=True)
    df.drop("created_date", axis=1, inplace=True)

    # Filter by start and end date
    if start_date is not None:
        df = df[df.index >= start_date]
    if end_date is not None:
        df = df[df.index <= end_date]

    df["character_count"] = df["text"].apply(len)
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))

    if user is None:
        df["user"] = uuid.uuid1()
    else:
        df["user"] = user

    df.loc[df["creator.email"] != user_email, "message_type"] = "incoming"
    df.loc[df["creator.email"] == user_email, "message_type"] = "outgoing"

    if pseudonymize:
        addresses = set(df["creator.email"].unique())
        address_map = {address: i for i, address in enumerate(addresses, 1)}
        address_map[user_email] = 0
        df["creator.email"] = df["creator.email"].apply(lambda x: address_map[x])

        names = set(df["creator.name"].unique())
        name_map = {address: i for i, address in enumerate(names, 1)}
        name_map[user_name] = 0
        df["creator.name"] = df["creator.name"].apply(lambda x: name_map[x])

    if sentiment:
        df = sentiment_analysis_from_text_column(df, "text", sentiment_batch_size)

    df.drop("text", axis=1, inplace=True)

    util.format_column_names(df)
    util.set_timezone(df, tz=timezone)
    return df



def youtube_watch_history(
        zip_filename,
        user=None,
        pseudonymize=True,
        start_date = None,
        end_date = None,
        timezone = "Europe/Helsinki"
    ):
    """ Read the watch history from a Google Takeout zip file.

    Watch history is stored as an html file. We parse the file
    and extract record times. These correspond to the time the
    user has started watching a given video.

    We do not return video titles or channel titles, but we
    convert these into unique identifiers and include those.
    
    Parameters
    ----------

    zip_filename : str
        The filename of the zip file.
    user: str (optional)
        A user ID that is added as a column to the dataframe. If not provided,
        a random user UI is generated.
    pseudonymize: bool (optional)
        Replace video and channel titles with ID numbers. Defaults to True.
    start_date : datetime.datetime, optional
        The start date for the data. If provided, only data after this date is
        included.
    end_date : datetime.datetime, optional
        The end date for the data. If provided, only data before this date is
        included.

    Returns
    -------

    data : pandas.DataFrame
    """

    # Read the html file with the watch history
    try:
        with ZipFile(zip_filename) as zip_file:
            with zip_file.open("Takeout/YouTube and YouTube Music/history/watch-history.html") as file:
                html = file.read().decode()
    except KeyError:
        return pd.DataFrame()
    
    # Extract divs with class content-cell. These contain the watch history.
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("div", {"class": "content-cell"})

    data = []
    for row in rows:
        a = row.find_all("a")
        if len(a) > 1:
            item = {
                "video_title": a[0].text,
                "channel_title": a[1].text,
                "timestamp": row.find_all("br")[1].next_sibling.text
            }
            timestamp = pd.to_datetime(item["timestamp"], format="%b %d, %Y, %I:%M:%S %p %Z")
            if start_date is not None:
                if timestamp < start_date:
                    continue
            if end_date is not None:
                if timestamp > end_date:
                    continue
            data.append(item)

    # Create the dataframe and set the timestamp as the index
    # Time format is like Feb 13, 2024, 8:35:03 AM EET
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%b %d, %Y, %I:%M:%S %p %Z"
    )
    df.set_index("timestamp", inplace=True)
    if user is None:
        user = uuid.uuid1()
    df["user"] = user

    # Pseudonymize the titles
    if pseudonymize:
        df["video_title"] = df["video_title"].astype("category").cat.codes
        df["channel_title"] = df["channel_title"].astype("category").cat.codes

    util.format_column_names(df)
    util.set_timezone(df, tz=timezone)
    return df


def fit_list_data(zip_filename):
    """ List data types in the Google Fit All Data folder.

    parameters
    ----------
    zip_filename : str
        The filename of the zip file.

    returns
    -------
    data descriptions : pd.DataFrame
        A pandas dataframe with data content types and descriptions.
        It contains the columns 
        - derived: bool

    """

    all_data_path = "Takeout/Fit/All Data"

    try:
        with ZipFile(zip_filename) as zip_file:
            data_types = []
            for filename in zip_file.namelist():
                if not filename.startswith(all_data_path):
                    continue
                # if the filename contains (NN).json, drop it
                if re.search(r'\(\d+\).json', filename):
                    continue
                full_path = filename
                filename = filename.replace(all_data_path + "/", "")
                try:
                    with zip_file.open(full_path) as file:
                        data = json.load(file)["Data Source"]
                        data_types.append(filename+":"+data)
                except:
                    continue
    except:
        return pd.DataFrame()

    formatted = []
    for data_source in data_types:

        data = {}
        entries = data_source.split(":")
        data["filename"] = entries[0]
        data["derived"] = entries[1]
        data["content"] = re.sub(r'^com\.google\.', '', entries[2])
        data["source"] = entries[3]
        data["source type"] = entries[-1]            

        formatted.append(data)

    return pd.DataFrame(formatted)


def fit_expand_data_filename(zip_filename, filename):
    """ List files with names filename(NN).json in the Google Fit All Data folder.
    """
    try:
        with ZipFile(zip_filename) as zip_file:
            filenames = zip_file.namelist()
    except:
        return pd.DataFrame()
    
    all_data_path = "Takeout/Fit/All Data"
    filename = os.path.join(all_data_path, filename)
    filename_pattern = filename.replace(".json", r'(.*).json$')

    filenames = [f for f in filenames if f.startswith(all_data_path)]
    filenames = [f for f in filenames if re.search(filename_pattern, f)]
    return filenames


def fit_read_data_file(
        zip_filename,
        data_filename,
        timezone = "Europe/Helsinki"
    ):
    """ Read a data file in the Google Fit All Data folder.
    """
    try:
        with ZipFile(zip_filename) as zip_file:
            with zip_file.open(data_filename) as file:
                read_data = json.load(file)
                data = read_data["Data Points"]
    except:
        return pd.DataFrame()
    
    # normalize
    data = pd.json_normalize(data)
    df = pd.DataFrame(data)
    
    if df.shape[0] == 0:
        return df

    def process_unit_value(value):
        if "fpVal" in value:
            return float(value["fpVal"])
        elif "intVal" in value:
            return int(value["intVal"])
        elif "stringVal" in value:
            return value["stringVal"]
        return value

    def process_fitValue(value, parent_index=None):
        if type(value) == list:
            values = []
            for i, v in enumerate(value):
                if parent_index is not None:
                    id = f"{parent_index}_{i}"
                else:
                    id = i
                values += process_fitValue(v, id)
            return values
        
        if type(value) == dict:
            if "value" in value:
                id = value.get("key", parent_index)
                value = value["value"]
                if "mapVal" in value:
                    return process_fitValue(value["mapVal"], id)
                
                # We are now at bottom level, assuming only
                # mapVal can be a list
                value = process_unit_value(value)
                return [{"id": id, "value": value}]

        raise ValueError("Unknown value type")

    if "fitValue" in df.columns:
        df = df.reset_index().rename(columns={'index': 'measurement_index'})
        df["_fitValue"] = df["fitValue"].apply(process_fitValue)
        df = df.explode('_fitValue').reset_index(drop=True)
        new_columns = pd.json_normalize(df['_fitValue'])
        df = pd.concat([df, new_columns], axis=1)
        df.drop(["fitValue", "_fitValue"], axis=1, inplace=True)

    if "startTimeNanos" in df.columns:
        df["timestamp"] = pd.to_datetime(df["startTimeNanos"], unit="ns")
        df.set_index("timestamp", inplace=True)
        df.drop("startTimeNanos", axis=1, inplace=True)
    
    if "endTimeNanos" in df.columns:
        df["end_time"] = pd.to_datetime(df["endTimeNanos"], unit="ns")
        df.drop("endTimeNanos", axis=1, inplace=True)
    
    if "modifiedTimeMillis" in df.columns:
        df["modified_time"] = pd.to_datetime(df["modifiedTimeMillis"], unit="ms")
        df.drop("modifiedTimeMillis", axis=1, inplace=True)

    if "dataTypeName" in df.columns:
        df["datatype"] = df["dataTypeName"].apply(lambda x: re.sub(r'^com\.google\.', '', x))
        df.drop("dataTypeName", axis=1, inplace=True)

    if "rawTimestampNanos" in df.columns:
        if (df["rawTimestampNanos"] == 0).all():
            df.drop("rawTimestampNanos", axis=1, inplace=True)
    
    if "originDataSourceId" in df.columns:
        if (df["originDataSourceId"] == "").all():
            df.drop("originDataSourceId", axis=1, inplace=True)
    
    util.format_column_names(df)
    util.set_timezone(df, tz=timezone)
    return df

    
def fit_read_data(
        zip_filename,
        data_filename,
        timezone = "Europe/Helsinki"
    ):
    """ Read multiple data files in the Google Fit All Data folder.
    """

    if type(data_filename) == str:
        filenames = fit_expand_data_filename(zip_filename, data_filename)
    else:
        try:
            filenames = []
            for filename in data_filename:
                filenames.extend(fit_expand_data_filename(zip_filename, filename))
        except TypeError:
            raise ValueError("data_filename should be a string or an iterable containign filename strings.")
    
    dfs = []
    measurement_index = 0
    for filename in filenames:
        df = fit_read_data_file(zip_filename, filename)
        if df.shape[0] == 0:
            continue
        df["measurement_index"] += measurement_index
        measurement_index = df["measurement_index"].max() + 1
        dfs.append(df)

    df = pd.concat(dfs)
    df.sort_index(inplace=True)
    util.set_timezone(df, tz=timezone)
    return df


def fit_all_data(zip_filename, timezone = "Europe/Helsinki"):
    """ Read all the data in the Google Fit All Data folder.
    """
    datafiles = fit_list_data(zip_filename)["filename"]
    data = fit_read_data(zip_filename, datafiles)
    return data


def fit_heart_rate_data(zip_filename, timezone = "Europe/Helsinki"):
    """ Read heart rate data from Google Fit All Data folder and
    format it more nicely.

    Parameters
    ----------
    zip_filename : str
        The filename of the zip file.

    Returns
    -------
    data : pandas.DataFrame
    """
    entries = fit_list_data(zip_filename)
    entries = entries[entries["content"].str.contains("heart_rate")]
    entries = entries[~entries["content"].str.contains("summary")]
    entries = entries[entries["derived"] == "raw"]
    df = fit_read_data(zip_filename, entries["filename"])

    df = df[["value", "modified_time"]]
    df.rename(columns={"value": "heart_rate"}, inplace=True)
    return df


def fit_sessions(zip_filename, timezone = "Europe/Helsinki"):
    """ Read all Google Takeout sessions and concatenate them into
    a dataframe. Each file contains aggregate data for a single 
    activity session or sleep session.
    """

    session_data_path = "Takeout/Fit/All Sessions"

    data = []
    try:
        with ZipFile(zip_filename) as zip_file:
            filenames = zip_file.namelist()
            for filename in filenames:
                if not filename.startswith(session_data_path):
                    continue
                with zip_file.open(filename) as file:
                    session_data = json.load(file)
                    if "segment" in session_data:
                        del session_data["segment"]
                    if "aggregate" in session_data:
                        for aggregate in session_data["aggregate"]:
                            name = aggregate["metricName"]
                            name = re.sub(r'^com\.google\.', '', name)
                            if "floatValue" in aggregate:
                                session_data[name] = aggregate["floatValue"]
                            elif "intValue" in aggregate:
                                session_data[name] = aggregate["intValue"]
                        del session_data["aggregate"]
                    data.append(session_data)
    
    except:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["startTime"], format='mixed')
    df["end_time"] = pd.to_datetime(df["endTime"], format='mixed')
    df.set_index("timestamp", inplace=True)
    df.drop(["startTime", "endTime"], axis=1, inplace=True)

    if "duration" in df.columns:
        df["duration"] = pd.to_timedelta(df["duration"])

    util.format_column_names(df)
    util.set_timezone(df, tz=timezone)

    return df


def myactivity(zip_filename, section, start_date=None, end_date=None):
    data_path = os.path.join("Takeout", "My Activity", section, "MyActivity.html")

    with ZipFile(zip_filename) as zip_file:
        with zip_file.open(data_path) as file:
            html = file.read().decode()

        date_pattern = re.compile(r"(.+?)\s+(\w+\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M\s+\w+)")

        data = []
        for text in ContentDivIterator(html):
            match = date_pattern.search(text)
            if match:
                timestamp = match.group(2)

                timestamp = pd.to_datetime(timestamp, format='%b %d, %Y, %I:%M:%S %p %Z')
                if start_date is not None and timestamp < start_date:
                    break
                if end_date is not None and timestamp > end_date:
                    continue

                data.append({"timestamp": timestamp, "description": text})
    
    df = pd.DataFrame(data)
    if len(df) == 0:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"], format='%b %d, %Y, %I:%M:%S %p %Z', utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert('EET')
    df.set_index("timestamp", inplace=True)
    return df


def list_myactivity_sections(zip_filename):
    """ List sections in the My Activity in a given Google Takeout zip file.
    """
    data_path = os.path.join("Takeout", "My Activity")

    with ZipFile(zip_filename) as zip_file:
        filenames = zip_file.namelist()
        sections = set()
        for filename in filenames:
            if not filename.startswith(data_path):
                continue
            sections.add(filename.split("/")[2])
    return sections



def YouTube(zip_filename, start_date=None, end_date=None):
    df = myactivity(zip_filename, "YouTube", start_date, end_date)
    activity_strings ={
        "Watched ": "Watched",
        "Viewed ": "Viewed",
        "Liked ": "Liked",
        "Disliked ": "Disliked",
        "Voted on ": "Voted",
        "Shared ": "Shared",
        "Commented on ": "Commented",
        "Subscribed to ": "Subscribed",
        "Unsubscribed from ": "Unsubscribed",
        "Answered ": "Answered",
        "Joined ": "Joined",
    }

    for activity_string, activity_type in activity_strings.items():
        rows = df["description"].str.startswith(activity_string)
        df.loc[rows, "activity_type"] = activity_type
        df.loc[rows, "description"] = df.loc[rows, "description"].str.replace(activity_string, "")

    description_lines = df["description"].str.split("\n")
    df["title"] = description_lines.str[0].str.strip()
    df["channel"] = description_lines.str[1].str.strip()

    # For "Subscribed" events, the title is missing
    rows = df["activity_type"] == "Subscribed"
    df.loc[rows, "channel"] = df.loc[rows, "title"]
    df.loc[rows, "title"] = np.NaN

    # Some times the channel and title are missing, and only a video
    # link is provided. In these cases, set that as title.
    rows = (df["activity_type"] == "Watched") & (
        df["description"].str.len() == 2)
    df.loc[rows, "channel"] = ""

    return df


def PlayStore(zip_filename, start_date=None, end_date=None):
    """ Read Play Store data from Google Takeout zip file.
    
    This contains app usage as well as activity in the Play Store app.
    """
    df = myactivity(zip_filename, "Google Play Store", start_date, end_date)
    description_lines = df["description"].str.split("\n")
    df["activity_type"] = description_lines.str[0].str.strip()
    df["name"] = description_lines.str[1:].str.join(" ").str.strip()
    df[df["name"].isna()] = ""

    activity_types = ["Used", "Searched", "Joined beta program for", "Visited", "Started to purchase", "Apps management notification", "Clicked on a notification", "Received a notification", "Viewed a notification", "Launched"]

    # When the name is not a link, the name is contained in the first
    # element of the description.
    for activity_type in activity_types:
        rows = df["activity_type"].str.startswith(activity_type+" ")
        df.loc[rows, "name"] = df.loc[rows, "activity_type"].str.replace(activity_type+" ", "").str.strip()
        df.loc[rows, "activity_type"] = activity_type

    df.loc[df["activity_type"] == "Searched for", "activity_type"] = "Searched"

    return df


def app_used(
        zip_filename,
        start_date=None,
        end_date=None,
        day_divide_time = "04:00:00"
    ):
    """ Read app usage data from the Play Store activity in Google Takeout
    zip file.
    
    Format the time stamp into a day used. The time stamp does not match actual
    time used, but we can deduce the day used from the time stamp.
    """
    df = PlayStore(zip_filename, start_date, end_date)
    df = df[df["activity_type"] == "Used"]
    df.drop("activity_type", axis=1, inplace=True)

    df["day"] = df.index - pd.to_timedelta(day_divide_time)
    df["day"] = df["day"].dt.floor("d")

    return df


def Search(zip_filename, start_date=None, end_date=None):
    """ Read search history from Google Takeout zip file.
    """
    df = myactivity(zip_filename, "Search", start_date, end_date)
    activity_strings ={
        "Visited ": "Visited",
        "Searched for ": "Searched"
    }

    for activity_string, activity_type in activity_strings.items():
        rows = df["description"].str.startswith(activity_string)
        df.loc[rows, "activity_type"] = activity_type
        df.loc[rows, "description"] = df.loc[rows, "description"].str.replace(activity_string, "")
    
    description_lines = df["description"].str.split("\n")
    df["channel"] = description_lines.str[1].str.strip()

    return df


def Maps(zip_filename, start_date=None, end_date=None):
    """ Read Google Maps history from Google Takeout zip file.
    """
    df = myactivity(zip_filename, "Maps", start_date, end_date)
    activity_strings ={
        "Viewed ": "Viewed",
        "Used ": "Used",
        "Directions to ": "Directions",
        "Searched for ": "Searched",
        "Explored ": "Explored",
    }

    for activity_string, activity_type in activity_strings.items():
        rows = df["description"].str.startswith(activity_string)
        df.loc[rows, "activity_type"] = activity_type
        df.loc[rows, "description"] = df.loc[rows, "description"].str.replace(activity_string, "")

    df.loc[df["activity_type"].isna(), "activity_type"] = "Viewed"
    
    description_lines = df["description"].str.split("\n")
    df[""] = description_lines.str[0].str.strip()

    del df["description"]

    return df

