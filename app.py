import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(layout="wide")
st.sidebar.title("TextThread Explorer")

uploaded_file = st.sidebar.file_uploader("Choose your exported chat")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df,df1 = preprocessor.Message_extractor(data ,r'(\d\d)/(\d\d)/(\d\d),\s(\d{1,2}):(\d\d)(\sam|\spm|\sAM|\sPM|)\s-\s', -1, 0)
    current_date = datetime.now()
    df2=df
    df2['Date']=df2['Date'].apply(lambda x: str(x).zfill(2))
    df2['Month_num']=df2['Month_num'].apply(lambda x: str(x).zfill(2))
    df2['Year'] =str(current_date.year)[:2]+df2['Year'].astype(str)
    df2['Hour']=df2['Hour'].apply(lambda x: str(x).zfill(2))
    df2['Minute']=df2['Minute'].apply(lambda x: str(x).zfill(2))

    # Extract the first two characters of the year
    st.title("Chat Analysis")
    st.dataframe(df2,column_config={"Month_num": "Month Number","day_name":"Day","only_Date":None,"period":None},use_container_width=True,hide_index=True)
    
    # fetch User Message frequency
    User_counts = df['User'].value_counts()

    # fetch unique Users
    User_list = User_counts.index.tolist()
    if 'WhatsApp Notification' in User_list:
        User_list.remove('WhatsApp Notification')

    User_list.insert(0, 'Overall')

    selected_User = st.sidebar.selectbox("Show Analysis WRT", User_list)

    if st.sidebar.button("Show Analysis"):
        if selected_User == 'Overall':
            st.title("Emotion Analysis")
            st.dataframe(df1,column_config={"Sentiment": "Emotion"},use_container_width=True,hide_index=True)

            #Visualize sentiment for group
            sentiment_counts=helper.visualise_sentiment(df1,selected_User)
            plt.title('Emotion Distribution by User')
            plt.xlabel('User')
            plt.ylabel('Count of Emotions')
            plt.legend(title='Emotion')
            plt.xticks(rotation=45)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.pyplot()

        else:
            df3=df1[df1['User']==selected_User]
            st.title("Emotion Analysis")
            st.dataframe(df3,column_config={"Sentiment": "Emotion"},use_container_width=True,hide_index=True)

            #Visualize sentiment for individual
            sentiment_counts=helper.visualise_sentiment(df3,selected_User)
            plt.title(f'Emotions Displayed by {selected_User}')
            plt.xlabel('Emotion')
            plt.ylabel('Count of Emotions')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.pyplot()

        # Statistics Area
        num_Messages, num_words, num_media_Messages, df_links, num_links = helper.fetch_stats(selected_User, df)

        if(len(User_list)==3):
            #Ghosting and display of links for overall
            ghost_list=helper.ghost(df2,User_list)
            if(selected_User=='Overall'):
                if not df_links.empty:
                    with st.container(height=250,border=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.title("Ghosting Report")
                            for user, percent in ghost_list.items():
                                st.write(f'{user} has a ghosting rate of {percent:.2f}% in the total number of responses sent by {user}, taking into account the average response time per message.') 
                        with col2:
                            st.title("Links Available")
                            st.dataframe(df_links,column_order=('Index','Links'),column_config={'Index':st.column_config.TextColumn(width='small'),'Links': st.column_config.LinkColumn(width='large')},use_container_width=True,hide_index=True)
                else:
                    st.title("Ghosting Report")
                    for user, percent in ghost_list.items():
                        st.write(f'{user} has a ghosting rate of {percent:.2f}% in the total number of responses sent by {user}, taking into account the average response time per message.')  
            else:
            #Ghosting and display of links for selected users
                if not df_links.empty:
                    with st.container(height=300,border=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.title("Ghosting Report")
                            st.write(f'{selected_User} has a ghosting rate of {ghost_list[selected_User]:.2f}% in the total number of responses sent by {selected_User}, taking into account the average response time per message.')  
                        with col2:
                            st.title("Links Available")
                            st.dataframe(df_links,column_order=('Index','Links'),column_config={'Index':st.column_config.TextColumn(width='small'),'Links': st.column_config.LinkColumn(width='large')},use_container_width=True,hide_index=True)
                else:
                    st.title("Ghosting Report")
                    st.write(f'{selected_User} has a ghosting rate of {ghost_list[selected_User]:.2f}% in the total number of responses sent by {selected_User}, taking into account the average response time per message.')  
        else:
            st.title("Links Available")
            st.dataframe(df_links,column_order=('Index','Links'),column_config={'Index':st.column_config.TextColumn(width='small'),'Links': st.column_config.LinkColumn(width='large')},use_container_width=True,hide_index=True)
        
        #Polling reports
        helper.poll(df2,selected_User)

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
            Message_df, Message_percentage_df = helper.fetch_most_busy_Users(df)
            figure, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(Message_df.index, Message_df.values, color='#FF4B4B')
                plt.xticks(rotation=15, ha='right')
                ax.set_ylabel("Number of Messages")
                st.pyplot(figure)

            with col2:
                st.dataframe(Message_percentage_df,use_container_width=True,hide_index=True)

        # WordCloud
        st.title('WordCloud')
        wc = helper.create_wordcloud(selected_User, df)
        df_wc = helper.create_wordcloud(selected_User, df)

        # Set the figsize to control the size of the WordCloud
        figure, ax = plt.subplots(figsize=(10, 10))

        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')  # Turn off axis labels

        ax.imshow(df_wc)
        st.pyplot(figure)

        col1,col2=st.columns(2)
        with col1:
        # Monthly timeline
            st.title("Monthly Timeline")
            timeline = helper.Monthly_timeline(selected_User, df)
            fig, ax = plt.subplots(figsize=(7,5))
            ax.plot(timeline['time'], timeline['Message'], color='green')
            plt.xticks(rotation=35, ha='right')
            ax.set_xlabel("Month of the Year")
            ax.set_ylabel("Number of Messages")
            st.pyplot(fig)

        with col2:
        # daily timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_User, df)
            fig, ax = plt.subplots(figsize=(7,5))
            ax.plot(daily_timeline['only_Date'], daily_timeline['Message'], color='black')
            plt.xticks(rotation=15, ha='right')
            ax.set_xlabel("Day of the Week")
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
            ax.set_xlabel("Day of the Week")
            ax.set_ylabel("Number of Messages")
            st.pyplot(fig)

        with col2:
            st.header("Most busy Month")
            busy_Month = helper.Month_activity_map(selected_User, df)
            fig, ax = plt.subplots()
            ax.bar(busy_Month.index, busy_Month.values, color='orange')
            plt.xticks(rotation=35, ha='right')
            ax.set_xlabel("Month of the Year")
            ax.set_ylabel("Number of Messages")
            st.pyplot(fig)
    
        st.title("Weekly Activity Map")
        User_heatmap = helper.activity_heatmap(selected_User, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(User_heatmap)
        x_labels = [label.get_text() for label in ax.get_xticklabels()]
        for i in range(len(x_labels)):
            parts = x_labels[i].split('-')  
            for j in range(len(parts)):
                parts[j] = parts[j].zfill(2) 
            x_labels[i] = '-'.join(parts)
        ax.set_xticklabels(x_labels)
        plt.xticks(rotation=60, ha='right')
        ax.set_xlabel("Period (in 24 hrs time format)")
        ax.set_ylabel("Day of the Week")
        st.pyplot(fig)
