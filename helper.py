from urlextract import URLExtract
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import emoji

extract = URLExtract()


# -------------------- FETCH STATS --------------------
def fetch_stats(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # ✅ FIX: ensure string type
    df['message'] = df['message'].fillna('').astype(str)

    num_messages = df.shape[0]

    # Total words
    words = df['message'].str.split().str.len().sum()

    # Media messages
    num_med_message = df[df['message'] == '<Media omitted>'].shape[0]

    # Links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, words, num_med_message, len(links)


# -------------------- MOST BUSY USERS --------------------
def most_busy_users(df):
    x = df['user'].value_counts()

    percent_df = (
        (df['user'].value_counts() / df.shape[0]) * 100
    ).round(2).reset_index()

    percent_df.columns = ['name', 'percent']

    return x, percent_df


# -------------------- WORDCLOUD --------------------
def create_wordcloud(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # Clean data
    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>']

    # ✅ FIX: ensure string + remove empty
    text = df['message'].fillna('').astype(str).str.cat(sep=" ")

    if text.strip() == "":
        return None

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color='white'
    )

    return wc.generate(text)


# -------------------- MOST COMMON WORDS --------------------
def most_common_words(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    # ✅ FIX: ensure string
    temp['message'] = temp['message'].fillna('').astype(str)

    words = []
    for message in temp['message']:
        words.extend(message.split())

    most_common_df = pd.DataFrame(
        Counter(words).most_common(20),
        columns=['word', 'count']
    )

    return most_common_df


# -------------------- EMOJI ANALYSIS --------------------
def emoji_helper(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    # ✅ FIX: ensure string
    df['message'] = df['message'].fillna('').astype(str)

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(),
        columns=['emoji', 'count']
    )

    return emoji_df


# -------------------- MONTHLY TIMELINE --------------------
def monthly_timeline(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


# -------------------- DAILY TIMELINE --------------------
def daily_timeline(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date').count()['message'].reset_index()


# -------------------- WEEK ACTIVITY --------------------
def week_activity_map(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


# -------------------- MONTH ACTIVITY --------------------
def month_activity_map(selected_user, df):

    if selected_user != 'overall':   # ✅ FIXED (was 'Overall')
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


# -------------------- HEATMAP --------------------
def activity_heatmap(selected_user, df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()

    user_heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    )

    return user_heatmap.fillna(0)
