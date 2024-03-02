import pandas as pd
import tensorflow as tf
import nltk as nl
import joblib
import random
import numpy as np

def get_text(text):
    tokenizer3 = tf.keras.preprocessing.text.Tokenizer() 
    tokenizer3.fit_on_texts(text)
    word_index3 = tokenizer3.word_index
    stemmer=nl.stem.PorterStemmer()
    stemmed_wordss = [stemmer.stem(word) for word in word_index3.keys()]
    tokens_list= tokenizer3.texts_to_sequences([stemmed_wordss])[0]

    for i in range(len(tokens_list)):
        for j in range(66-len(tokens_list)):
            tokens_list.append(0)
    return tokens_list

def main():
    input_df=pd.read_csv('output1.csv')
    model = joblib.load("sentiment_LSTM.sav")
    labels_dict = {0:'sadness', 1:'joy', 2:'love', 3:'anger', 4:'fear', 5:'surprise'}
    sentiment=[]
    for i in range(len(input_df)):

        test = get_text(input_df['Message'][i])

        test = np.array(test)
        test = test.reshape(1, len(test))

        #Make predictions
        predictions = model.predict(test)

        predicted_class = np.argmax(predictions)

        sentiment.append(labels_dict.get(predicted_class))
    
    input_df['Sentiment']=sentiment
    
    return input_df

