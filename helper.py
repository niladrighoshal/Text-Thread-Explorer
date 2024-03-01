from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
# import emoji  # use ' pip install emoji==1.7 '


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

    # 4. fetch number of links shared
    extract = URLExtract()
    links = []
    for Message in df['Message']:
        links.extend(extract.find_urls(Message))
    
    

    return num_Messages, len(words), num_media_Messages, len(links)
    # return linkdf


def fetch_most_busy_Users(df):
    # Message_df = df['User'].value_counts().head()
    Message_df = df['User'].value_counts().head()

    Message_percentage_df = round((df['User'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={
            'index': 'User',
            'User': 'User'
        }
    )

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

    wc = WordCloud(width=1000, height=1000, min_font_size=10,
                   background_color='white', prefer_horizontal=0.9)
    temp['Message'] = temp['Message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['Message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_User, df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_User != 'Overall':
        df = df[df['User'] == selected_User]

    temp = df[df['User'] != 'group_notification']
    temp = temp[temp['Message'] != '<Media omitted>\n']

    words = []

    for Message in temp['Message']:
        for word in Message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


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

    User_heatmap = df.pivot_table(
        index='day_name', columns='period', values='Message', aggfunc='count').fillna(0)

    return User_heatmap
