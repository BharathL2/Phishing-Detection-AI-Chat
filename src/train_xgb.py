"""Train an XGBoost phishing detector.
Loads labeled dataset (prefers data/kaggle_phishing.csv else data/sample_dataset.csv).
Saves TF-IDF vectorizer + XGBoost classifier pipeline to models/phish_xgb.pkl.
Run: python src/train_xgb.py
"""
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
import json
from xgboost import XGBClassifier

PRIMARY = os.path.join('data','kaggle_phishing.csv')
FALLBACK = os.path.join('data','sample_dataset.csv')
MODEL_DIR = 'models'
MODEL_PATH = os.path.join(MODEL_DIR,'phish_xgb.pkl')


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['text'] = df['text'].fillna('').astype(str)
    # map labels to binary
    df['label'] = df['label'].str.lower().map({'phishing':1,'clean':0})
    # drop rows with unknown label mapping
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].astype(int)
    return df


def build_pipeline() -> Pipeline:
    vec = TfidfVectorizer(ngram_range=(1,2), min_df=1)
    # Lightweight XGB config (CPU friendly for demo)
    xgb = XGBClassifier(
        max_depth=4,
        n_estimators=120,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        objective='binary:logistic',
        eval_metric='logloss',
        verbosity=0,
        n_jobs=4
    )
    return Pipeline([
        ('vec', vec),
        ('xgb', xgb)
    ])


def main():
    data_path = PRIMARY if os.path.exists(PRIMARY) else FALLBACK
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"No dataset at {PRIMARY} or {FALLBACK}")
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = load_data(data_path)
    X, y = df['text'], df['label']
    pipe = build_pipeline()
    pipe.fit(X, y)
    preds = pipe.predict(X)
    print("Training set classification report (illustrative only):")
    print(classification_report(y, preds, target_names=['clean','phishing']))
    joblib.dump(pipe, MODEL_PATH)
    print(f"Saved XGBoost model to {MODEL_PATH}")
    # Save basic metrics for UI display
    acc = float(accuracy_score(y, preds))
    p,r,f1,_ = precision_recall_fscore_support(y, preds, average='binary', zero_division=0)
    metrics = {
        'accuracy': round(acc,4),
        'precision': round(float(p),4),
        'recall': round(float(r),4),
        'f1': round(float(f1),4),
        'samples': int(len(y))
    }
    with open(os.path.join(MODEL_DIR,'phish_xgb_metrics.json'),'w',encoding='utf-8') as f:
        json.dump(metrics, f)
    print("Saved metrics to models/phish_xgb_metrics.json:", metrics)

if __name__ == '__main__':
    main()
