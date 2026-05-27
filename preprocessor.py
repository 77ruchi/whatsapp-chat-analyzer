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

    # remove rows where date failed
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

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['period'] = df['hour'].apply(
        lambda x: f"{x}-{(x + 1) % 24}"
    )

    df['period'] = period


    return df