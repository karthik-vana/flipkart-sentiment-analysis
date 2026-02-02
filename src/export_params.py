import joblib
import json
import numpy as np
import os
from sklearn.base import BaseEstimator

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sentiment_model.joblib")
OUTPUT_PATH = os.path.join(BASE_DIR, "models", "model_params.json")

def to_list(array_or_matrix):
    """Helper to convert dense/sparse array to list."""
    if hasattr(array_or_matrix, "toarray"):
        return array_or_matrix.toarray().tolist()
    if hasattr(array_or_matrix, "tolist"):
        return array_or_matrix.tolist()
    return list(array_or_matrix)

def export_params():
    print(f"Loading model from {MODEL_PATH}...")
    pipeline = joblib.load(MODEL_PATH)
    
    vectorizer = pipeline.named_steps['tfidf']
    classifier = pipeline.named_steps['clf']
    
    print(f"Classifier type: {type(classifier)}")
    
    print("Extracting TF-IDF parameters...")
    # Vocabulary: word -> index
    vocab = vectorizer.vocabulary_
    # IDF params: vectorizer.idf_
    idf = vectorizer.idf_
    
    print("Extracting Classifier parameters...")
    
    if hasattr(classifier, "coef_"):
        coef = classifier.coef_
        intercept = classifier.intercept_
    elif hasattr(classifier, "feature_log_prob_"): # Naive Bayes
        # NB is a bit more complex to implement manually with just dot product (it needs log sum exp structure)
        # But for binary, it's feasible. However, sticking to LR is safer.
        print("Model is Naive Bayes. Exporting log probs.")
        coef = classifier.feature_log_prob_ 
        intercept = classifier.class_log_prior_
    elif hasattr(classifier, "feature_importances_"): # Random Forest
        print("ERROR: Random Forest cannot be exported as simple linear coefficients.")
        return
    else:
        print("ERROR: Unknown classifier type for export.")
        return

    # Check for sparse
    coef_list = to_list(coef)
    intercept_list = to_list(intercept)
    idf_list = to_list(idf)

    # Prepare JSON structure
    # Convert vocab numpy int64 to python int
    vocab = {k: int(v) for k, v in vocab.items()}
    
    params = {
        "vocabulary": vocab,
        "idf": idf_list,
        "coefficients": coef_list,
        "intercept": intercept_list,
        "classes": to_list(classifier.classes_) if hasattr(classifier, "classes_") else [0, 1]
    }
    
    print(f"Saving parameters to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(params, f)
    
    print("Export complete.")

if __name__ == "__main__":
    export_params()
