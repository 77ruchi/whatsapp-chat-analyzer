import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    # ✅ Encoding Fix
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            data = bytes_data.decode("latin-1")
        except:
            data = bytes_data.decode("ISO-8859-1")

    # preprocess
    df = preprocessor.preprocess(data)

    # ✅ Fix message column
    df['message'] = df['message'].fillna('').astype(str)

    # user list
    user_list = df['user'].dropna().astype(str).unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # ---------------- STATS ----------------
        num_messages, words, num_med_message, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top statistics")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Messages", num_med_message)
        col4.metric("Links Shared", num_links)

        # ---------------- MONTHLY TIMELINE ----------------
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)

        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'])
        plt.xticks(rotation=90)
        st.pyplot(fig)

        # ---------------- DAILY TIMELINE ----------------
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)

        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'])
        plt.xticks(rotation=90)
        st.pyplot(fig)

        # ---------------- ACTIVITY MAP ----------------
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation=90)
            st.pyplot(fig)

        with col2:
            st.subheader("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values)
            plt.xticks(rotation=90)
            st.pyplot(fig)

        # ---------------- HEATMAP ----------------
        st.title("Weekly Activity Map")
        heatmap = helper.activity_heatmap(selected_user, df)

        if heatmap.empty:
            st.warning("No activity data available")
        else:
            fig, ax = plt.subplots()
            sns.heatmap(heatmap, ax=ax)
            st.pyplot(fig)

        # ---------------- MOST BUSY USERS ----------------
        if selected_user == "overall":
            st.title("Most Busy Users")

            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values)
                plt.xticks(rotation=90)
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # ---------------- WORDCLOUD ----------------
        st.title("Wordcloud")

        df_wc = helper.create_wordcloud(selected_user, df)

        if df_wc is not None:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.warning("No words available to generate wordcloud.")

        # ---------------- MOST COMMON WORDS ----------------
        st.title("Most Common Words")

        common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()
        ax.bar(common_df['word'], common_df['count'])
        plt.xticks(rotation=90)
        st.pyplot(fig)

        # ---------------- EMOJI ----------------
        st.title("Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            top = emoji_df.head(5)
            fig, ax = plt.subplots()
            ax.pie(top['count'], labels=top['emoji'], autopct='%1.1f%%')
            st.pyplot(fig)
