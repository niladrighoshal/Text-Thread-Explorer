import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# import model
st.set_page_config(layout="wide")
st.sidebar.title("Whatsapp Chat Analyzer")


uploaded_file = st.sidebar.file_uploader("Choose your exported chat")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.text(data)
    df = preprocessor.Message_extractor(data ,r'(\d\d)/(\d\d)/(\d\d),\s(\d{1,2}):(\d\d)(\sam|\spm|\sAM|\sPM|)\s-\s', -1, 0)
    # df = preprocessor.preprocess(df)
    st.title("Chat Analysis")
    # modified_df = df.drop(columns=['Month_num', 'day', 'only_Date', 'hour', 'minute', 'period', 'Year', 'Month'])
    st.dataframe(df)

    # fetch User Message frequency
    User_counts = df['User'].value_counts()

    # fetch unique Users
    # User_list = df['User'].unique().tolist()
    User_list = User_counts.index.tolist()


    if 'WhatsApp Notification' in User_list:
        User_list.remove('WhatsApp Notification')


    # Sentiment analysis code
    # df['Sentiment_Value'] = [model.run(df['Message'][i]) for i in range(0, df.shape[0])]


    User_list.insert(0, 'Overall')

    # User_list = df['User']
    selected_User = st.sidebar.selectbox("Show Analysis WRT", User_list)

    if st.sidebar.button("Show Analysis"):

        # Statistics Area

        num_Messages, num_words, num_media_Messages, num_links = helper.fetch_stats(
            selected_User, df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_Messages)
        with col2:
            st.header("Total Words")
            st.title(num_words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_Messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Finding the busiest User of the group

        if selected_User == 'Overall':
            st.title("Most Busy Users")
            Message_df, Message_percentage_df = helper.fetch_most_busy_Users(
                df)
            figure, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(Message_df.index, Message_df.values, color='#FF4B4B')
                plt.xticks(rotation=15, ha='right')
                ax.set_ylabel("Number of Messages")
                st.pyplot(figure)

            with col2:
                Message_percentage_df = Message_percentage_df.rename(
                    columns={0: 'UserS', 1: 'Contribution'})

                # st.dataframe(Message_percentage_df)
                st.dataframe(Message_percentage_df)
        



        # WordCloud
        st.title('WordCloud')
        # st.dataframe(df['Message'])
        wc = helper.create_wordcloud(selected_User, df)
        df_wc = helper.create_wordcloud(selected_User, df)
        # Set the figsize to control the size of the WordCloud
        figure, ax = plt.subplots(figsize=(10, 10))

        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')  # Turn off axis labels

        ax.imshow(df_wc)
        st.pyplot(figure)

        # Monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.Monthly_timeline(selected_User, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['Message'], color='green')
        plt.xticks(rotation=35, ha='right')
    
        ax.set_xlabel("Monthly Timeline")
        ax.set_ylabel("Number of Messages")
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_User, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_Date'],
                daily_timeline['Message'], color='black')
        plt.xticks(rotation=15, ha='right')
    
        ax.set_xlabel("Name of the Day")
        ax.set_ylabel("Number of Messages")
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_User, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation=30, ha='right')
            
            ax.set_xlabel("Name of the Day")
            ax.set_ylabel("Number of Messages")
            st.pyplot(fig)

        with col2:
            st.header("Most busy Month")
            busy_Month = helper.Month_activity_map(selected_User, df)
            fig, ax = plt.subplots()
            ax.bar(busy_Month.index, busy_Month.values, color='orange')
            plt.xticks(rotation=35, ha='right')
            ax.set_xlabel("Name of the Month")
            ax.set_ylabel("Number of Messages")
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        User_heatmap = helper.activity_heatmap(selected_User, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(User_heatmap)
        plt.xticks(rotation=60, ha='right')
        ax.set_xlabel("Period (in 24 hrs time format)")
        ax.set_ylabel("Name of the Day")
        st.pyplot(fig)
