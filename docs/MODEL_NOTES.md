# Model Notes

Prototype:
- TF-IDF n-gram representation
- Logistic Regression classifier
- Balanced class weighting
- SIF probability output

Why this baseline?
It is lightweight, explainable and suitable for a first prototype. A later version
can compare Logistic Regression, SVM, Random Forest, XGBoost, BERT/RoBERTa and
domain-adapted transformer models.

Evaluation for the actual project should report:
- Precision
- Recall
- F1-score
- Confusion matrix
- PR-AUC / ROC-AUC
- SIF-class recall

The SIF class is safety-critical; accuracy alone is insufficient.
