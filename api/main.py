from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import os
import re
import math
import sys

# Project root setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import preprocessing (ensure it doesn't depend on heavy libs)
from src.preprocessing import clean_text

app = FastAPI(title="Flipkart Sentiment Analysis API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model Parameters
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAMS_PATH = os.path.join(BASE_DIR, "models", "model_params.json")

model_params = None

@app.on_event("startup")
def load_params():
    global model_params
    if os.path.exists(PARAMS_PATH):
        print("Loading model parameters...")
        with open(PARAMS_PATH, 'r') as f:
            model_params = json.load(f)
        # Convert lists back to numpy/optimized structures for fast inference
        model_params["idf"] = np.array(model_params["idf"])
        model_params["coefficients"] = np.array(model_params["coefficients"])
        model_params["intercept"] = np.array(model_params["intercept"])
        print("Model parameters loaded successfully.")
    else:
        print("Model parameters not found! Please export model first.")

# Scikit-Learn TfidfVectorizer Tokenizer Pattern
TOKEN_PATTERN = re.compile(r"(?u)\b\w\w+\b")

def simple_tfidf_transform(text, vocab, idf):
    """
    Re-implementation of TfidfVectorizer transform for a single document.
    """
    # 1. Tokenize
    tokens = TOKEN_PATTERN.findall(text.lower())
    
    # 2. Count (TF)
    tf = {}
    for token in tokens:
        if token in vocab:
            idx = vocab[token]
            tf[idx] = tf.get(idx, 0) + 1
            
    # 3. Create Vector (Sparse representation)
    if not tf:
        return np.zeros(len(vocab))
        
    indices = np.array(list(tf.keys()))
    values = np.array(list(tf.values()))
    
    # 4. Apply IDF
    # TF-IDF = tf * idf
    # Note: TfidfVectorizer with sublinear_tf=False (default) uses raw counts * idf
    # Check if we need to log(tf)? Default is simple counts.
    
    # Vector of size vocab
    vector = np.zeros(len(vocab))
    vector[indices] = values * idf[indices]
    
    # 5. L2 Normalization
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
        
    return vector

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class ReviewRequest(BaseModel):
    review: str

class ReviewResponse(BaseModel):
    sentiment: str
    confidence: float
    pain_points: list[str] = []

PAIN_POINTS = ["bad quality", "waste of money", "poor quality", "defective product", "not original", "worst product", "fake", "damage"]

@app.get("/")
def home():
    return {"message": "Sentiment Analysis API is Running (Lightweight)"}

@app.post("/predict", response_model=ReviewResponse)
def predict_sentiment(request: ReviewRequest):
    if not model_params:
        raise HTTPException(status_code=500, detail="Model parameters not loaded")
    
    # 1. Preprocess
    # Note: Training pipeline applied clean_text BEFORE Tfidf?
    # Yes, train_model.py: df['cleaned_text'] = df['Review text'].apply(clean_text)
    cleaned_review = clean_text(request.review)
    
    # 2. Vectorize
    vector = simple_tfidf_transform(
        cleaned_review, 
        model_params["vocabulary"], 
        model_params["idf"]
    )
    
    # 3. Predict (Dot Product + Intercept)
    # Coef shape: (1, n_features) or (n_classes, n_features) if multiclass
    # For binary, sklearn stores (1, n_features).
    try:
        linear_pred = np.dot(model_params["coefficients"], vector) + model_params["intercept"]
        
        # Binary Classification
        # If linear_pred > 0 -> Positive (Class 1)
        # Probabilities
        prob_pos = sigmoid(linear_pred)[0] # probability of class 1
        prob_neg = 1 - prob_pos
        
        if prob_pos > 0.5:
            sentiment = "Positive"
            confidence = prob_pos
        else:
            sentiment = "Negative"
            confidence = prob_neg
            
    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    warnings = []
    if sentiment == "Negative":
        lower_rev = request.review.lower()
        for point in PAIN_POINTS:
            if point in lower_rev:
                warnings.append(point)
                
    return {
        "sentiment": sentiment,
        "confidence": float(confidence),
        "pain_points": warnings
    }
