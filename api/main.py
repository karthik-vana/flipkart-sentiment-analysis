from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

import os
import sys

# Add project root to path to allow importing src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing import clean_text

app = FastAPI(title="Flipkart Sentiment Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model
# Get absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sentiment_model.joblib")
model = None

# Global variable for pain points (could remain static or loaded)
PAIN_POINTS = ["bad quality", "waste of money", "poor quality", "defective product", "not original"] 

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        print("Model not found! Please train the model first.")

class ReviewRequest(BaseModel):
    review: str

class ReviewResponse(BaseModel):
    sentiment: str
    confidence: float
    pain_points: list[str] = []

@app.get("/")
def home():
    return {"message": "Sentiment Analysis API is Running"}

@app.post("/predict", response_model=ReviewResponse)
def predict_sentiment(request: ReviewRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    cleaned_review = clean_text(request.review)
    
    # Predict
    # The pipeline expects a list/series
    prediction = model.predict([cleaned_review])[0]
    probabilities = model.predict_proba([cleaned_review])[0]
    
    sentiment = "Positive" if prediction == 1 else "Negative"
    confidence = max(probabilities)
    
    warnings = []
    if sentiment == "Negative":
        # Simple extraction: check if know pain points are in the text
        # In a real system, this would be more dynamic
        for point in PAIN_POINTS:
            if point in cleaned_review:
                warnings.append(point)
                
    return {
        "sentiment": sentiment,
        "confidence": float(confidence),
        "pain_points": warnings
    }
