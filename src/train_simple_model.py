"""Train a simple Logistic Regression phishing detector from data/sample_dataset.csv.
Saves model + vectorizer into models/ folder.
"""
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

DATA_PATH = os.path.join('data', 'sample_dataset.csv')
MODEL_DIR = 'models'
MODEL_PATH = os.path.join(MODEL_DIR, 'phish_logreg.pkl')


def load_data(path: str):
    df = pd.read_csv(path)
    # Basic cleaning
    df['text'] = df['text'].fillna('').astype(str)
    df['label'] = df['label'].map({'phishing': 1, 'clean': 0})
    return df

def build_pipeline():
    return Pipeline([
        ('vec', TfidfVectorizer(ngram_range=(1,2), min_df=1)),
        ('clf', LogisticRegression(max_iter=500))
    ])

def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = load_data(DATA_PATH)
    X = df['text']
    y = df['label']
    clf = build_pipeline()
    clf.fit(X, y)
    preds = clf.predict(X)
    print("Classification report (training set – illustrative only):")
    print(classification_report(y, preds, target_names=['clean','phishing']))
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == '__main__':
    main()
