import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
import os

def plot_rating_distribution(df, save_path=None):
    """
    Plot the distribution of ratings.
    """
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Review_rate', data=df, palette='viridis')
    plt.title('Distribution of Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    if save_path:
        plt.savefig(os.path.join(save_path, 'rating_distribution.png'))
    plt.close()

def plot_sentiment_distribution(df, save_path=None):
    """
    Plot the distribution of sentiment.
    """
    plt.figure(figsize=(6, 5))
    sns.countplot(x='Sentiment', data=df, palette='coolwarm')
    plt.title('Distribution of Sentiment')
    plt.xlabel('Sentiment (0=Negative, 1=Positive)')
    plt.ylabel('Count')
    if save_path:
        plt.savefig(os.path.join(save_path, 'sentiment_distribution.png'))
    plt.close()

def plot_wordcloud(text_data, title, save_path=None, filename='wordcloud.png'):
    """
    Generate and plot a word cloud.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(str(text_data))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    if save_path:
        plt.savefig(os.path.join(save_path, filename))
    plt.close()
