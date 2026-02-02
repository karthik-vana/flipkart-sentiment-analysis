import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import os

# NLTK Setup for Serverless/Local
NLTK_DATA_PATH = os.path.join("/tmp", "nltk_data") if os.path.exists("/tmp") else None

def download_nltk_resource(resource, target_dir=None):
    try:
        nltk.data.find(resource)
    except LookupError:
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
            nltk.download(resource.split('/')[-1], download_dir=target_dir)
            if target_dir not in nltk.data.path:
                nltk.data.path.append(target_dir)
        else:
            nltk.download(resource.split('/')[-1])

# Download necessary resources
resources = ['corpora/stopwords', 'corpora/wordnet', 'tokenizers/punkt']
for res in resources:
    download_nltk_resource(res, target_dir=NLTK_DATA_PATH)


# Initialize Lemmatizer and Stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def get_sentiment_label(rating):
    """
    Convert numerical rating to sentiment label.
    Rating <= 2: Negative (0)
    Rating >= 4: Positive (1)
    Rating = 3: Neutral (dropped or treated as specific class, but prompt implies Binary)
    """
    if rating <= 2:
        return 0  # Negative
    elif rating >= 4:
        return 1  # Positive
    else:
        return -1 # Neutral (often ignored in binary classification)

def clean_text(text):
    """
    Clean and preprocess review text.
    - Lowercase
    - Remove HTML tags
    - Remove URLs
    - Remove special characters and punctuation
    - Remove stopwords
    - Lemmatization
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
    
    # 6. Remove Stopwords and Lemmatize
    words = text.split()
    cleaned_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    
    return " ".join(cleaned_words)
