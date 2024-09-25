import pandas as pd
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
from tqdm import tqdm  
from sklearn.preprocessing import LabelEncoder

def main(test_data):
    model_name = 'distilbert-base-uncased'
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)

    model_path = 'model_5_BERT_ekmann'
    model = DistilBertForSequenceClassification.from_pretrained(model_path)

    test_data_1 = pd.read_excel("result_final.xlsx") 
    test_sentences = test_data['Message'].tolist()

    test_labels=test_data_1['Label'].tolist()
    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(test_labels)

    # Tokenize the test sentences
    inputs = tokenizer(test_sentences, padding=True, truncation=True, return_tensors="pt")

    # Run inference on the test data
    predictions = []
    with torch.no_grad():
        for i in tqdm(range(0, len(inputs['input_ids']), 32)):  # Use tqdm for progress bar
            batch_inputs = {key: val[i:i+32] for key, val in inputs.items()}  # Create batches
            outputs = model(**batch_inputs)
            predictions.extend(torch.argmax(outputs.logits, dim=1).tolist())

    predictions = label_encoder.inverse_transform(predictions)
    # Add predicted labels to the DataFrame
    test_data['Sentiment'] = predictions
    test_data['Sentiment'] = test_data['Sentiment'].str.capitalize()

    # Save predictions to Excel file
    return test_data
