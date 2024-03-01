import re
import datetime
import calendar
import pandas as pd

re1 = r'WhatsApp\sNotification'

def preprocess(df):
    
    df['only_Date'] = datetime.datetime.strptime(calendar.month_name[df['Month']] + ' ' + str(df['Date']) + ', 20' + str(df['Year']), '%B %d, %Y').strftime('%A')
    
    period = []
    for Hour in df[['day_name', 'Hour']]['Hour']:
        if Hour == 23:
            period.append(str(Hour) + "-" + str('00'))
        elif Hour == 0:
            period.append(str('00') + "-" + str(Hour + 1)) 
        else:
            period.append(str(Hour) + "-" + str(Hour + 1))

    df['period'] = period   

    return df 

def Message_extractor(chat, pattern, n, z):

  chat = re.split(pattern, chat)
  # print('RegEx split = ', chat, '\nLength of split string list : ', len(chat), '\nInfo for individual Message :-')
  chat = [[int(chat[i]), int(chat[i+1]), int(chat[i+2]), # DD/MM/YY or MM/DD/YY
      int(chat[i+3]) + (12 if (len(chat[i+5]) == 3 and (chat[i+5][1] == 'p' or chat[i+5][1] == 'P')) else 0), int(chat[i+4]), # HH:MM
      chat[i+6][0:chat[i+6].index(':')] if ':' in chat[i+6] else 'WhatsApp Notification', # User
      chat[i+6][(chat[i+6].index(':')+2 if ':' in chat[i+6] else 0):]] # Message
      for i in range(1,len(chat),7)]

# Filtering out WhatsApp Notifications
  
  chat = filter(lambda x: len(re.findall(re1, x[5])) == 0, chat)


  # Making dataframe
  df = pd.DataFrame(chat)


  # Taking metrics of columns
  v = []
  if (z == 0):
    v = [df[0].var(), df[1].var()]
  elif (z == 1):
    v = [df[0].nunique(), df[1].nunique()]

  # Reordering columns
    # [0 : DD, 1 :MM, 2 :YY, 3 :HH, 4 :mm, 5 :Users, 6 :Messages]
  if (v[0] >= v[1]):
    df = df[[0, 1, 2, 3, 4, 5, 6]]
  else:
    df = df[[1, 0, 2, 3, 4, 5, 6]]

  # Putting column names
    #             0         1           2      3        4        5         6
  df.columns = ['Date', 'Month_num', 'Year', 'Hour', 'Minute', 'User', 'Message']
  df['Month'] = [calendar.month_name[df['Month_num'][i]] for i in range(0, df.shape[0])] 
  df['day_name'] =  [datetime.datetime.strptime(df['Month'][i] + ' ' + str(df['Date'][i]) + ', 20' + str(df['Year'][i]), '%B %d, %Y').strftime('%A') for i in range(0, df.shape[0])]
  df['only_Date'] = [datetime.datetime.strptime(df['Month'][i] + ' ' + str(df['Date'][i]) + ', 20' + str(df['Year'][i]), '%B %d, %Y').strftime('%A') for i in range(0, df.shape[0])]

  period = []
  for Hour in df[['day_name', 'Hour']]['Hour']:
      if Hour == 23:
          period.append(str(Hour) + "-" + str('00'))
      elif Hour == 0:
          period.append(str('00') + "-" + str(Hour + 1)) 
      else:
          period.append(str(Hour) + "-" + str(Hour + 1))

  df['period'] = period

  return df
