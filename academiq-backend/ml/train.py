"""
AcademiQ — Train the XGBoost Risk Prediction Model
Run: python ml/train.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from database.connection import SessionLocal
from ml.features import extract_features_for_course, FEATURE_COLUMNS
from models.db_models import Course

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models", "risk_model_v1.pkl"
)

def generate_synthetic_training_data(base_features: list) -> pd.DataFrame:
    """Augments real DIU sample data with synthetic variations to train a robust ML model."""
    np.random.seed(42)
    rows = list(base_features)

    for _ in range(40):
        # Strong students
        rows.append({
            "early_pct": np.random.uniform(70, 95),
            "submission_rate": np.random.uniform(0.9, 1.0),
            "clo1_early_pct": np.random.uniform(70, 100),
            "clo2_early_pct": np.random.uniform(65, 95),
            "clo3_early_pct": np.random.uniform(70, 100),
            "clo4_early_pct": np.random.uniform(70, 100),
            "at_risk": 0
        })
        # Average students
        rows.append({
            "early_pct": np.random.uniform(55, 75),
            "submission_rate": np.random.uniform(0.7, 1.0),
            "clo1_early_pct": np.random.uniform(50, 80),
            "clo2_early_pct": np.random.uniform(55, 80),
            "clo3_early_pct": np.random.uniform(40, 75),
            "clo4_early_pct": np.random.uniform(50, 80),
            "at_risk": 0
        })
        # At-risk students
        rows.append({
            "early_pct": np.random.uniform(20, 55),
            "submission_rate": np.random.uniform(0.4, 0.8),
            "clo1_early_pct": np.random.uniform(10, 50),
            "clo2_early_pct": np.random.uniform(20, 55),
            "clo3_early_pct": np.random.uniform(10, 50),
            "clo4_early_pct": np.random.uniform(20, 60),
            "at_risk": 1
        })

    return pd.DataFrame(rows)

def run_training():
    db = SessionLocal()
    courses = db.query(Course).all()
    
    all_features = []
    for c in courses:
        all_features.extend(extract_features_for_course(c.id, db))
        
    db.close()

    if not all_features:
        print("Error: No early data found in database to train model.")
        return

    df = generate_synthetic_training_data(all_features)
    
    X = df[FEATURE_COLUMNS]
    y = df["at_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTraining XGBoost model for Week 6 Early Alerts...")
    model = XGBClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
        eval_metric="logloss", verbosity=0
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    
    print(f"\nModel Evaluation:")
    print(f"  Accuracy : {accuracy_score(y_test, y_pred):.2%}")
    print(f"  AUC-ROC  : {roc_auc_score(y_test, y_pred_prob):.3f}")
    print(f"\nDetailed Report:\n{classification_report(y_test, y_pred, target_names=['Not at risk', 'At risk'])}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved successfully to: {MODEL_PATH}")

if __name__ == "__main__":
    run_training()