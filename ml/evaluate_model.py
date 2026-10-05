from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "sif_reports.csv")
X = df["report"].astype(str)
y = (df["label"].astype(str).str.upper() == "SIF").astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=26165, stratify=y
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=26165))
])
model.fit(X_train, y_train)
pred = model.predict(X_test)

print("=== DEMONSTRATION DATASET ONLY ===")
print("Accuracy :", round(accuracy_score(y_test, pred), 3))
print("Precision:", round(precision_score(y_test, pred, zero_division=0), 3))
print("Recall   :", round(recall_score(y_test, pred, zero_division=0), 3))
print("F1-score :", round(f1_score(y_test, pred, zero_division=0), 3))
print("Confusion matrix:")
print(confusion_matrix(y_test, pred))
print("\nThese metrics are not OIL operational performance metrics.")
