from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np
from gensim.models import Word2Vec

def get_bow_vectorizer(max_features=5000):
    """
    Returns a Bag of Words vectorizer.
    """
    return CountVectorizer(max_features=max_features)

def get_tfidf_vectorizer(max_features=5000, ngram_range=(1, 2)):
    """
    Returns a TF-IDF vectorizer (unigrams + bigrams).
    """
    return TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)

def train_word2vec(tokenized_sentences, vector_size=100, window=5, min_count=2):
    """
    Trains a Word2Vec model on the provided sentences.
    """
    w2v_model = Word2Vec(sentences=tokenized_sentences, vector_size=vector_size, window=window, min_count=min_count, workers=4)
    return w2v_model

def get_sentence_embedding(sentence, w2v_model):
    """
    Averages word vectors to get a sentence embedding.
    """
    words = sentence.split()
    word_vectors = [w2v_model.wv[word] for word in words if word in w2v_model.wv]
    
    if len(word_vectors) == 0:
        return np.zeros(w2v_model.vector_size)
    
    return np.mean(word_vectors, axis=0)
