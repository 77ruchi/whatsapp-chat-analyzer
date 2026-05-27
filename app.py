import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocessor.preprocess(data)


    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)


    if st.sidebar.button("Show Analysis", key="analyze_btn"):

        # ---------------- STATS ----------------
        num_messages, words, num_med_message, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Media Messages")
            st.title(num_med_message)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        #timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        plt.plot(timeline['time'], timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)


        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig,ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)


        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig,ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")

        user_heatmap = helper.activity_heatmap(selected_user, df)

        if user_heatmap.empty:
            st.warning("No activity data available for this user.")
        else:
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap, ax=ax)
            st.pyplot(fig)

        # ---------------- MOST BUSY USERS ----------------
        if selected_user == "overall":
            st.title("Most Busy Users")

            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # ---------------- WORDCLOUD ----------------
        st.title("Wordcloud")

        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()

        ax.imshow(df_wc)
        ax.axis('off')

        st.pyplot(fig)

        # ---------------- MOST COMMON WORDS ----------------
        st.title("Most Common Words")

        most_common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()
        ax.bar(most_common_df['word'], most_common_df['count'])
        plt.xticks(rotation='vertical')

        st.pyplot(fig)


        # ---------------- EMOJI ANALYSIS ----------------
        st.title("Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            # limit for better pie chart
            emoji_df_top = emoji_df.head(5)

            fig, ax = plt.subplots()
            ax.pie(
                emoji_df_top['count'],
                labels=emoji_df_top['emoji'],
                autopct='%1.1f%%'
            )

            st.pyplot(fig)