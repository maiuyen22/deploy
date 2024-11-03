# -*- coding: utf-8 -*-
"""app.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GW-WazLth6soeckYjpiIbF1SGAc4_PlA
"""

# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load the pre-trained PhoBERT model and tokenizer
model_name = "phobert_sa"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Initialize the FastAPI app
app = FastAPI()

# Define the input data model
class TextInput(BaseModel):
    text: str

# Label mapping dictionary
label_map = {0: "negative", 1: "neutral", 2: "positive"}

# Define a prediction endpoint
@app.post("/predict")
async def predict_sentiment(input: TextInput):
    # Tokenize the input text and convert it to tensor format
    inputs = tokenizer(input.text, return_tensors="pt", padding=True, truncation=True, max_length=128)

    # Set model to evaluation mode and make predictions without gradient computation
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # Get the predicted label and confidence scores
    prediction = torch.argmax(logits, dim=-1).item()
    label = label_map.get(prediction, "unknown")
    scores = logits.softmax(dim=-1).tolist()[0]  # Convert to list for easy JSON serialization

    return {"label": label, "scores": scores}