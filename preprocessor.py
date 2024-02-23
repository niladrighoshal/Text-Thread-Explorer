import re
import pandas as pd

def preprocess(data):
    pattern1 = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}(?:\s?[ap]m)?\s-\s)'
    
    def convert_date_format(match):
        date_str = match.group(0).strip()
        return pd.to_datetime(date_str, format='%d/%m/%y, %I:%M %p -').strftime('%d/%m/%Y, %H:%M -')
    
    data_formatted = re.sub(pattern1, convert_date_format, data)

    data = data_formatted

    pattern = '\d{1,2}/\d{1,2}/\d{4},\s\d{1,2}:\d{1,2}\s-'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)


    df = pd.DataFrame({'user_message' :messages, 'message_date' : dates})
    # conevrt message_date type
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M -')
    df.rename(columns = {'message_date' : 'date'}, inplace =True)


    #separate users and mesages
    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('whatsapp notification')
            messages.append(entry[0])

    df['user'] = users 
    df['message'] = messages 
    df.drop(columns = ['user_message'], inplace = True)

    df['year'] = df['date'].dt.year

    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month

    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['only_date'] = df['date'].dt.date  

    df['hour'] = df['date'].dt.hour

    df['minute'] = df['date'].dt.minute  

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1)) 
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period   

    return df 

