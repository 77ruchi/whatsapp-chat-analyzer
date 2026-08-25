from urlextract import URLExtract
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import emoji

extract = URLExtract()


def fetch_stats(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    df['message'] = df['message'].fillna('').astype(str)

    num_messages = df.shape[0]
    words = df['message'].str.split().str.len().sum()
    num_med_message = df[df['message'] == '<Media omitted>'].shape[0]

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, words, num_med_message, len(links)


def most_busy_users(df):
    x = df['user'].value_counts()

    percent_df = ((df['user'].value_counts() / df.shape[0]) * 100).round(2).reset_index()
    percent_df.columns = ['name', 'percent']

    return x, percent_df


def create_wordcloud(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>']

    text = df['message'].fillna('').astype(str).str.cat(sep=" ")

    if text.strip() == "":
        return None

    wc = WordCloud(width=500, height=500, background_color='white')
    return wc.generate(text)


def most_common_words(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    temp['message'] = temp['message'].fillna('').astype(str)

    words = []
    for msg in temp['message']:
        words.extend(msg.split())

    return pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])


def emoji_helper(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    df['message'] = df['message'].fillna('').astype(str)

    emojis = []
    for msg in df['message']:
        emojis.extend([c for c in msg if emoji.is_emoji(c)])

    return pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])


def monthly_timeline(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date').count()['message'].reset_index()


def week_activity_map(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()

    heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    )

    return heatmap.fillna(0)
