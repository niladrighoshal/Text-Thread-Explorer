from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import spacy
import re
import iso639
import streamlit as st
from matplotlib import pyplot as plt
from spacy.language import Language
from spacy_language_detection import LanguageDetector

def detect_lang(df):
      
    def get_lang_detector(nlp, name):
        return LanguageDetector(seed=42)  # We use the seed 42

    nlp_model = spacy.load("xx_ent_wiki_sm")
    if 'sentencizer' not in nlp_model.pipe_names:
        nlp_model.add_pipe('sentencizer')
    Language.factory("language_detector", func=get_lang_detector)
    nlp_model.add_pipe('language_detector', last=True)
    detected_languages=[]
    for _,row in df.iterrows():
        message = nlp_model(row['Message'])
        if(message._.language.get('score')>=0.95):
            lang_code=message._.language.get('language')
            try:
                language_name = iso639.to_name(lang_code)
                detected_languages.append(language_name)
            except iso639.NonExistentLanguageError:
                detected_languages.append(None)  
        else:
            detected_languages.append(None) 
    df['Detected Language']=detected_languages
    return df     
          
    # Plot emotion analysis visualization
def visualise_sentiment(df,selected_User):
    if(selected_User=='Overall'):
        sentiment_counts = df.groupby(['User', 'Sentiment']).size().unstack(fill_value=0)
        sentiment_counts = sentiment_counts.plot(kind='bar', stacked=True, figsize=(10, 6))
        for p in sentiment_counts.patches:
            width, height = p.get_width(), p.get_height()
            x, y = p.get_xy() 
            sentiment_counts.text(x + width / 2, y + height / 2, f'{height}', ha='center', va='center')
    else:
        sentiment_counts = df['Sentiment'].value_counts()
        sentiment_counts = sentiment_counts.plot(kind='bar', color='skyblue',figsize=(10, 6))
        for p in sentiment_counts.patches:
            sentiment_counts.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_y()+p.get_height() / 2.),ha='center', va='center')

    return sentiment_counts

    #Ghosting
def ghost(df,User_list):
    total_message_reply_pairs={}
    # Extract the first two characters of the year
    df['Complete_date']=df['Date']+'/'+df['Month_num']+'/'+df['Year']
    df['Complete_time']=df['Hour']+':'+df['Minute']
    df['Datetime'] = pd.to_datetime(df['Complete_date'] + ' ' + df['Complete_time'], format='%d/%m/%Y %H:%M')
    time_diff_list=[]
    ghost_list={}
    User_list_without_overall=User_list.copy()
    User_list_without_overall.pop(0)
    for user_name in User_list_without_overall:
        ghost_list[user_name] = 0
        total_message_reply_pairs[user_name]=0

    for index, row in df.iterrows():
        if index < len(df) - 1:
            if(row['User']!=df.at[index + 1, 'User']):
                total_message_reply_pairs[df.at[index + 1, 'User']]+=1
                time_diff_list.append((df.at[index + 1, 'Datetime']-row['Datetime'])/pd.Timedelta(minutes=1))
    mean_time_diff = sum(time_diff_list) / len(time_diff_list)

    for index, row in df.iterrows():
        if index < len(df) - 1:
            if(row['User']!=df.at[index + 1, 'User']):
                time_diff=(df.at[index + 1, 'Datetime']-row['Datetime'])/pd.Timedelta(minutes=1)
                if(time_diff>=mean_time_diff):
                    ghost_list[df.at[index + 1, 'User']]+=1

    for user, count in ghost_list.items():
        ghost_list[user]=(count/total_message_reply_pairs[user])*100    
    return ghost_list

def poll(df,selected_User):
    if (selected_User != 'Overall'):
        df=df[df['User']==selected_User]
    re_poll = r'POLL:\r\n(.*)\r\n(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)?(OPTION:\s.*\s\(\d*\svotes?\)\r\n)'
    re_option = r'OPTION:\s(.*)\s\((\d*)\svotes?\)'
    num_of_plots=0
    for _,row in df.iterrows():
        x = re.findall(re_poll, row['Message'])
        if len(x) == 1:
            num_of_plots+=1
    if(num_of_plots>0):
        count=1
        num_rows = int(num_of_plots**0.5)  
        num_cols = (num_of_plots + num_rows - 1) // num_rows
        fig, ax = plt.subplots(num_rows,num_cols,figsize=(15,9))
        row_index=0
        col_index=0
        for _,row in df.iterrows():
            x = re.findall(re_poll, row['Message'])
            if len(x) == 1:
                if(count == 1):
                    st.title("Poll Reports")
                x = [y for y in list(x[0]) if len(y) > 0]
                topic = x[0]
                x = [re.split(re_option, x[i]) for i in range(1, len(x))]
                labels = [x[i][1] for i in range(0, len(x))]
                freq = [int(x[i][2]) for i in range(0, len(x))]
                if(num_rows==1):
                    if (col_index<num_cols):
                        _, _, autotexts = ax[col_index].pie(freq, labels=None, startangle=140, autopct='%1.1f%%')
                        ax[col_index].set_title(f"Poll by {row['User']} on '{topic}'",fontsize=14.5)

                        # Adding legend
                        ax[col_index].legend(labels, bbox_to_anchor=(0.10, 0.24))

                        # Removing labels from pie slices
                        for autotext in autotexts:
                            autotext.set_color('black')
                        col_index+=1

                elif(num_rows>1):
                    if(row_index<num_rows): 
                        if(col_index==num_cols):
                            col_index=0
                            row_index+=1
                        if(col_index<num_cols):
                            _, _, autotexts = ax[row_index,col_index].pie(freq, labels=None, startangle=140, autopct='%1.1f%%')
                            ax[row_index,col_index].set_title(f"Poll by {row['User']} on '{topic}'",fontsize=14.5)
                            
                            # Adding legend
                            ax[row_index,col_index].legend(labels, bbox_to_anchor=(0.10, 0.24))

                            # Removing labels from pie slices
                            for autotext in autotexts:
                                autotext.set_color('black')
                            col_index+=1
                count+=1
        st.pyplot(fig)

def fetch_stats(selected_User, df):
    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    # 1. fetch number of Messages
    num_Messages = df.shape[0]

    # 2. fetch number of words
    words = []
    for Message in df['Message']:
        words.extend(Message.split())

    # 3. fetch number of media Messages
    num_media_Messages = df[df['Message'] == '<Media omitted>\n'].shape[0]

    # 4. fetch links shared
    extract = URLExtract()
    links = []

    for Message in df['Message']:
        links.extend(extract.find_urls(Message))

    df_links = pd.DataFrame(links, columns=['Links'])
    df_links['Index'] = df_links.index+1
    return num_Messages, len(words), num_media_Messages, df_links,len(links)

def fetch_most_busy_Users(df):
    Message_df = df['User'].value_counts().head()
    Message_percentage_df = round((df['User'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    Message_percentage_df = Message_percentage_df.rename(columns={'count': 'Number of messages (in %)'})
    return Message_df, Message_percentage_df

def create_wordcloud(selected_User, df):
    f = open('cleaned_sorted_stopwords.txt', 'r')
    stop_words = f.read()

    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    temp = df[df['User'] != 'group_notification']
    temp = temp[temp['Message'] != '<Media omitted>\n']

    def remove_stop_words(Message):
        y = []
        for word in Message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=1000, height=1000, min_font_size=10,background_color='white', prefer_horizontal=0.9)
    temp['Message'] = temp['Message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['Message'].str.cat(sep=" "))
    return df_wc

def Monthly_timeline(selected_User, df):

    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    timeline = df.groupby(['Year', 'Month_num', 'Month']).count()[
        'Message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['Month'][i] + "-" + str(timeline['Year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_User, df):

    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    daily_timeline = df.groupby('only_Date').count()['Message'].reset_index()

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Convert day names to categorical type with specified order
    daily_timeline['only_Date'] = pd.Categorical(daily_timeline['only_Date'], categories=days_order, ordered=True)

    # Sort by the categorical order
    daily_timeline.sort_values('only_Date', inplace=True)
    
    return daily_timeline


def week_activity_map(selected_User, df):

    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    return df['day_name'].value_counts()


def Month_activity_map(selected_User, df):

    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    return df['Month'].value_counts()


def activity_heatmap(selected_User, df):

    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    User_heatmap = df.pivot_table(index='day_name', columns='period', values='Message', aggfunc='count').fillna(0)

    return User_heatmap