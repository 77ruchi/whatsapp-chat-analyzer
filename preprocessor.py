import re
import pandas as pd


def preprocess(data):
    # correct regex (raw string + supports 24hr time)
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{2}:\d{2}'

    # extract messages and dates
    message = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # create dataframe
    df = pd.DataFrame({'user_message': message, 'message_date': dates})

    # convert to datetime (safe)
    df['message_date'] = pd.to_datetime(
        df['message_date'],
        format="%d/%m/%y, %H:%M",
        errors='coerce'
    )
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # extract users and messages
    users = []
    messages = []
    for msg in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', msg)
        if len(entry) > 2:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # remove rows where date failed to parse
    df = df.dropna(subset=['date'])

    # datetime features
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    df['minute'] = df['date'].dt.minute

    # build the hourly "period" bucket, e.g. "9-10", "23-00", "00-1"
    df['period'] = df['hour'].apply(
        lambda h: f"{h}-00" if h == 23 else (f"00-{h + 1}" if h == 0 else f"{h}-{h + 1}")
    )

    return df
