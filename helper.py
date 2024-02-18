from urlextract import URLExtract
from wordcloud import WordCloud



def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    # 1. fetch number of messages
    num_messages = df.shape[0]

    # 2. fetch number of words 
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 3. fetch number of media messages 
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
        
    # 4. fetch number of links shared 
    extract = URLExtract()
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))


    return num_messages, len(words), num_media_messages, len(links)

def fetch_most_busy_users(df):
    # message_df = df['user'].value_counts().head()
    message_df = df[df['user'] != 'whatsapp notification']['user'].value_counts().head()

    message_percentage_df = round((df['user'].value_counts() / df.shape[0]) *100 , 2).reset_index().rename(
        columns = {
            'index' : 'name',
            'user' : 'percentage'
        }
    )
    
    return message_df, message_percentage_df



def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    wc = WordCloud(width=1000, height=1000, min_font_size=10, background_color='white')

    df1 = df['message'].str.cat(sep=" ")
    stopwords_file_path = 'D:\Python Proj\major_vs\cleaned_sorted_stopwords.txt'

    # Load stopwords from the text file
    with open(stopwords_file_path, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().split('\n'))

    # Filter out stopwords from df1
    filtered_df1 = ' '.join(word for word in df1.split() if word.lower() not in stopwords)

    # Generate WordCloud
    df_wc = wc.generate(filtered_df1)

    return df_wc

