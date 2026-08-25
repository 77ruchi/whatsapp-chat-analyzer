import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    # ✅ Handle encoding safely
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            data = bytes_data.decode("latin-1")
        except UnicodeDecodeError:
            data = bytes_data.decode("ISO-8859-1")

    # preprocess data
    df = preprocessor.preprocess(data)

    if df.empty:
        st.error("No valid messages could be parsed from this file. Please make sure it's an exported WhatsApp chat (.txt).")
        st.stop()

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

        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Messages", num_messages)
        col2.metric("Words", words)
        col3.metric("Media", num_med_message)
        col4.metric("Links", num_links)

        # ---------------- MONTHLY TIMELINE ----------------
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)

        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'])
        plt.xticks(rotation=90)
        st.pyplot(fig)

        # ---------------- DAILY TIMELINE ----------------
        st.title("Daily Timeline")
        daily = helper.daily_timeline(selected_user, df)

        fig, ax = plt.subplots()
        ax.plot(daily['only_date'], daily['message'])
        plt.xticks(rotation=90)
        st.pyplot(fig)

        # ---------------- ACTIVITY ----------------
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Busy Days")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation=90)
            st.pyplot(fig)

        with col2:
            st.subheader("Busy Months")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values)
            plt.xticks(rotation=90)
            st.pyplot(fig)

        # ---------------- HEATMAP ----------------
        st.title("Weekly Activity Heatmap")
        heatmap = helper.activity_heatmap(selected_user, df)

        if heatmap.empty:
            st.warning("No activity data available")
        else:
            fig, ax = plt.subplots()
            sns.heatmap(heatmap, ax=ax)
            st.pyplot(fig)

        # ---------------- BUSY USERS ----------------
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

        wc = helper.create_wordcloud(selected_user, df)

        if wc is not None:
            fig, ax = plt.subplots()
            ax.imshow(wc)
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.warning("No words available to generate wordcloud.")

        # ---------------- COMMON WORDS ----------------
        st.title("Most Common Words")

        common = helper.most_common_words(selected_user, df)

        if common.empty:
            st.warning("No common words available.")
        else:
            fig, ax = plt.subplots()
            ax.bar(common['word'], common['count'])
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

            if not top.empty:
                fig, ax = plt.subplots()
                ax.pie(top['count'], labels=top['emoji'], autopct='%1.1f%%')
                st.pyplot(fig)
            else:
                st.warning("No emojis found.")
