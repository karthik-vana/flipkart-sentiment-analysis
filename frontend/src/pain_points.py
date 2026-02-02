from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def extract_pain_points(df, top_n=10):
    """
    Extract key pain points (keywords/phrases) from negative reviews.
    """
    # Filter negative reviews
    neg_reviews = df[df['sentiment'] == 0]['cleaned_text']
    
    if neg_reviews.empty:
        return []
    
    # Use TF-IDF to find important n-grams (2-3 words)
    tfidf = TfidfVectorizer(ngram_range=(2, 3), max_features=100, stop_words='english')
    X = tfidf.fit_transform(neg_reviews)
    
    # Sum tfidf scores for each term
    scores = X.sum(axis=0).A1
    feature_names = tfidf.get_feature_names_out()
    
    # Create a DataFrame of terms and scores
    freq_df = pd.DataFrame({'phrase': feature_names, 'score': scores})
    freq_df = freq_df.sort_values(by='score', ascending=False)
    
    return freq_df.head(top_n)['phrase'].tolist()
