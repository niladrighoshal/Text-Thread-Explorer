import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
st. set_page_config(layout="wide")
st.sidebar.title("Whatsapp Chat Analyzer")


uploaded_file = st.sidebar.file_uploader("Choose your exported chat")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.text(data)
    df = preprocessor.preprocess(data)

    st.dataframe(df)

    # fetch user message frequency
    user_counts = df['user'].value_counts()

    # fetch unique users
    # user_list = df['user'].unique().tolist()
    user_list = user_counts.index.tolist()
    user_list.remove('whatsapp notification')
    user_list.insert(0, 'Overall')
    selected_user = st.sidebar.selectbox("Show Analysis WRT", user_list)

    if st.sidebar.button("Show Analysis"):

        # Statistics Area

        num_messages, num_words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(num_words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)
        

        # Finding the busiest user of the group
        
        if selected_user == 'Overall':
            st.title("Most Busy Users")
            message_df, message_percentage_df = helper.fetch_most_busy_users(df)
            figure, ax = plt.subplots()
            
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(message_df.index, message_df.values, color ='#FF4B4B')
                plt.xticks(rotation = 15, ha='right')
                st.pyplot(figure)
            
            with col2:
                st.dataframe(message_percentage_df)

        
        # WordCloud
        st.title('WordCloud')
        # st.dataframe(df['message'])
        wc = helper.create_wordcloud(selected_user, df)
        df_wc = helper.create_wordcloud(selected_user, df)
        figure , ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(figure)
        



