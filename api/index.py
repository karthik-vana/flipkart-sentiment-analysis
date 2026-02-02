from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import os
import re

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

def load_params():
    global model_params
    if model_params is not None:
        return
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
        print(f"Model parameters not found at {PARAMS_PATH}!")

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
    vector = np.zeros(len(vocab))
    vector[indices] = values * idf[indices]
    
    # 5. L2 Normalization
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
        
    return vector

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Inline text cleaning to avoid NLTK dependency issues in serverless
import string

def clean_text_simple(text):
    """
    Simple text cleaning without NLTK dependencies.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # 3. Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # 4. Remove emojis (basic unicode range) and special characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # 5. Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 6. Basic stopword removal (common words)
    stopwords = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
                 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
                 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
                 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
                 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
                 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
                 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
                 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
                 'will', 'just', 'don', 'should', 'now'}
    
    words = text.split()
    cleaned_words = [word for word in words if word not in stopwords]
    
    return " ".join(cleaned_words)

class ReviewRequest(BaseModel):
    review: str

class ReviewResponse(BaseModel):
    sentiment: str
    confidence: float
    pain_points: list[str] = []

PAIN_POINTS = ["bad quality", "waste of money", "poor quality", "defective product", "not original", "worst product", "fake", "damage"]

@app.get("/")
def home():
    return {"message": "Sentiment Analysis API is Running (Serverless)"}

@app.get("/api")
def api_home():
    return {"message": "Sentiment Analysis API is Running (Serverless)"}

@app.post("/predict")
@app.post("/api/predict")
def predict_sentiment(request: ReviewRequest):
    load_params()
    
    if not model_params:
        raise HTTPException(status_code=500, detail="Model parameters not loaded")
    
    # 1. Preprocess
    cleaned_review = clean_text_simple(request.review)
    
    # 2. Vectorize
    vector = simple_tfidf_transform(
        cleaned_review, 
        model_params["vocabulary"], 
        model_params["idf"]
    )
    
    # 3. Predict (Dot Product + Intercept)
    try:
        linear_pred = np.dot(model_params["coefficients"], vector) + model_params["intercept"]
        
        # Binary Classification
        prob_pos = sigmoid(linear_pred)[0]
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
