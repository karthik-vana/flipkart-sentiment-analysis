import pandas as pd
import numpy as np
import joblib
import os
import time
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report, confusion_matrix, accuracy_score

from src.preprocessing import clean_text, get_sentiment_label
# from src.feature_engineering import get_tfidf_vectorizer # We can define explicitly in pipeline for clarity

# Configuration
DATA_PATH = 'data/raw/reviews.csv'
MODELS_DIR = 'models'
REPORTS_DIR = 'reports'

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    # Basic cleaning
    df = df.dropna(subset=['Review text', 'Ratings'])
    df['cleaned_text'] = df['Review text'].apply(clean_text)
    df['sentiment'] = df['Ratings'].apply(get_sentiment_label)
    
    # Remove neutral sentiment (-1)
    df = df[df['sentiment'] != -1]
    
    return df

def train_and_evaluate(df):
    X = df['cleaned_text']
    y = df['sentiment']
    
    # Stratified Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    models = {
        'Logistic_Regression': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
            ('clf', LogisticRegression(random_state=42, max_iter=1000))
        ]),
        'Naive_Bayes': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
            ('clf', MultinomialNB())
        ]),
        'Random_Forest': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ]),
        'SVM': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
            ('clf', SVC(kernel='linear', probability=True, random_state=42))
        ])
    }
    
    results = []
    best_model = None
    best_f1 = 0
    best_model_name = ""

    print("\nStarting Model Training & Evaluation...")
    print(f"{'Model':<20} | {'F1-Score':<10} | {'Accuracy':<10} | {'Time (s)':<10}")
    print("-" * 60)
    
    for name, pipeline in models.items():
        start_time = time.time()
        pipeline.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        y_pred = pipeline.predict(X_test)
        
        f1 = f1_score(y_test, y_pred, average='weighted') # weighted for imbalance
        acc = accuracy_score(y_test, y_pred)
        
        print(f"{name:<20} | {f1:<10.4f} | {acc:<10.4f} | {train_time:<10.4f}")
        
        results.append({
            'Model': name,
            'F1_Score': f1,
            'Accuracy': acc,
            'Time': train_time
        })
        
        if f1 > best_f1:
            best_f1 = f1
            best_model = pipeline
            best_model_name = name
            
    print("-" * 60)
    print(f"Best Model: {best_model_name} with F1-Score: {best_f1:.4f}")
    
    # Save the best model
    save_path = os.path.join(MODELS_DIR, 'sentiment_model.joblib')
    joblib.dump(best_model, save_path)
    print(f"Best model saved to {save_path}")
    
    # Detailed Report for Best Model
    print(f"\nDetailed Report for {best_model_name}:")
    y_pred_best = best_model.predict(X_test)
    print(classification_report(y_test, y_pred_best))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_best))

if __name__ == "__main__":
    df = load_data(DATA_PATH)
    if df is not None:
        train_and_evaluate(df)
