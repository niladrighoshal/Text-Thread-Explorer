import torch
import pandas
from tqdm import tqdm
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, AdamW
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

excel_file = 'ekmann_2.xlsx'
df = pandas.read_excel(excel_file)
df = df.dropna()
df.fillna("", inplace=True)

labels=df['Label'].tolist()
label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)
labels_tensor = torch.tensor(labels_encoded)

# Step 2: Tokenize text using BERT tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Tokenize texts and convert them to input features
input_ids = []
attention_masks = []

for text in df['Text']:
    encoded_dict = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        padding='max_length',
        max_length=128,
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )
    input_ids.append(encoded_dict['input_ids'])
    attention_masks.append(encoded_dict['attention_mask'])

input_ids = torch.cat(input_ids, dim=0)
attention_masks = torch.cat(attention_masks, dim=0)

# Step 3: Split the dataset into training and validation sets
train_inputs, val_inputs, train_masks, val_masks, train_labels, val_labels = train_test_split(
    input_ids, attention_masks, labels_tensor, test_size=0.2, random_state=42
)

# Step 4: Create DataLoader for training and validation sets
batch_size = 32

train_dataset = TensorDataset(train_inputs, train_masks, train_labels)
train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

val_dataset = TensorDataset(val_inputs, val_masks, val_labels)
val_dataloader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# Step 5: Load pre-trained BERT model for sequence classification
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=7)

# Step 6: Fine-tune BERT model
optimizer = AdamW(model.parameters(), lr=2e-5)
num_epochs = 3

for epoch in range(num_epochs):
    model.train()
    total_train_loss = 0
    progress_bar = tqdm(train_dataloader, desc=f'Epoch {epoch+1}/{num_epochs}')
    for batch in progress_bar:
        input_ids, attention_mask, labels = batch
        optimizer.zero_grad()
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        total_train_loss += loss.item()
        progress_bar.set_postfix({'Training Loss': total_train_loss / len(progress_bar)})

# Step 7: Evaluate the model
model.eval()
val_loss = 0
val_preds = []
val_true = []
for batch in val_dataloader:
    input_ids, attention_mask, labels = batch
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
    logits = outputs.logits
    val_loss += outputs.loss.item()
    val_preds.extend(logits.argmax(dim=1).tolist())
    val_true.extend(labels.tolist())

avg_val_loss = val_loss / len(val_dataloader)

print(f"Validation Loss: {avg_val_loss:.4f}")

model.save_pretrained('model_5_BERT_ekmann')

# Calculate precision, recall, and F1 score
class_names = label_encoder.classes_
print(classification_report(val_true, val_preds, target_names=class_names))
