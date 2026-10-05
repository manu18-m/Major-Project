from pathlib import Path
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sif_reports.csv"
MODEL_PATH = ROOT / "ml" / "sif_classifier.joblib"

def train():
    data = pd.read_csv(DATA_PATH)
    X = data["report"].astype(str)
    y = (data["label"].astype(str).str.upper() == "SIF").astype(int)

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            lowercase=True,
            sublinear_tf=True,
            min_df=1
        )),
        ("clf", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=26165
        ))
    ])
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model, len(data)

if __name__ == "__main__":
    _, n = train()
    print(f"Saved: {MODEL_PATH}")
    print(f"Training samples: {n}")
