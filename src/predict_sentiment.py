from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
from config import MODEL_PATH

_tokenizer = None
_model = None

def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        if not os.path.exists(MODEL_PATH):
            fallback_model = "distilbert-base-uncased-finetuned-sst-2-english"
            print(f"Local model not found at {MODEL_PATH}. Falling back to '{fallback_model}'...")
            _tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            _model = AutoModelForSequenceClassification.from_pretrained(fallback_model)
        else:
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    return _tokenizer, _model

def predict_sentiment(cleaned_text):
    tokenizer, model = load_model()
    inputs = tokenizer(cleaned_text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1).numpy()[0]
        score = probs[1] - probs[0]  
    return float(score)