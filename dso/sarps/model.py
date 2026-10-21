"""Module 3 - Model training, evaluation and persistence."""
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .data_ingestion import FEATURES


def train(df, seed=42):
    X, y = df[FEATURES], df["at_risk"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=seed)
    candidates = {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced")),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=8, class_weight="balanced", random_state=seed),
    }
    results, fitted = {}, {}
    for name, m in candidates.items():
        m.fit(Xtr, ytr)
        p, prob = m.predict(Xte), m.predict_proba(Xte)[:, 1]
        results[name] = {"accuracy": accuracy_score(yte, p), "precision": precision_score(yte, p),
                         "recall": recall_score(yte, p), "f1": f1_score(yte, p),
                         "roc_auc": roc_auc_score(yte, prob),
                         "cv_f1": cross_val_score(m, X, y, cv=5, scoring="f1").mean(),
                         "confusion": confusion_matrix(yte, p).tolist()}
        fitted[name] = m
    best = max(results, key=lambda k: results[k]["f1"])
    return fitted[best], best, results, (Xte, yte)


def save(model, path="models/risk_model.joblib"):
    joblib.dump(model, path)


def load(path="models/risk_model.joblib"):
    return joblib.load(path)


def feature_importance(model):
    est = model[-1] if hasattr(model, "steps") else model
    imp = est.feature_importances_ if hasattr(est, "feature_importances_") else np.abs(est.coef_[0])
    return dict(sorted(zip(FEATURES, imp / imp.sum()), key=lambda kv: -kv[1]))
