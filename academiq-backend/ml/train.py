"""
Train the XGBoost risk prediction model.
Run with: python ml/train.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    roc_auc_score
)
from database.connection import SessionLocal
from ml.features import extract_features_for_course, FEATURE_COLUMNS
from models.db_models import Course

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models", "risk_model_v1.pkl"
)

def generate_synthetic_training_data(base_features: list) -> pd.DataFrame:
    """
    We have 10 students in the demo database.
    That's not enough to train a real ML model (need at least 50+).
    This function augments the real data with synthetic variations
    to create a proper training dataset.
    """
    np.random.seed(42)
    rows = []

    # Use real data as base
    for f in base_features:
        rows.append(f)

    # Generate synthetic students based on real patterns
    # Strong students (at_risk = 0)
    for _ in range(40):
        rows.append({
            "student_id":      9999,
            "student_name":    "Synthetic",
            "course_id":       1,
            "early_pct":       np.random.uniform(70, 98),
            "submission_rate": np.random.uniform(80, 100),
            "co1_early_pct":   np.random.uniform(70, 98),
            "co2_early_pct":   np.random.uniform(65, 95),
            "co3_early_pct":   np.random.uniform(70, 98),
            "co4_early_pct":   np.random.uniform(68, 95),
            "at_risk":         0,
            "final_pct":       np.random.uniform(70, 98),
        })

    # Average students (at_risk = 0, borderline)
    for _ in range(30):
        rows.append({
            "student_id":      9999,
            "student_name":    "Synthetic",
            "course_id":       1,
            "early_pct":       np.random.uniform(55, 72),
            "submission_rate": np.random.uniform(60, 85),
            "co1_early_pct":   np.random.uniform(55, 72),
            "co2_early_pct":   np.random.uniform(50, 70),
            "co3_early_pct":   np.random.uniform(55, 72),
            "co4_early_pct":   np.random.uniform(52, 70),
            "at_risk":         0,
            "final_pct":       np.random.uniform(60, 72),
        })

    # Weak students (at_risk = 1)
    for _ in range(30):
        rows.append({
            "student_id":      9999,
            "student_name":    "Synthetic",
            "course_id":       1,
            "early_pct":       np.random.uniform(15, 52),
            "submission_rate": np.random.uniform(20, 60),
            "co1_early_pct":   np.random.uniform(10, 50),
            "co2_early_pct":   np.random.uniform(10, 48),
            "co3_early_pct":   np.random.uniform(15, 52),
            "co4_early_pct":   np.random.uniform(10, 50),
            "at_risk":         1,
            "final_pct":       np.random.uniform(15, 55),
        })

    return pd.DataFrame(rows)


def train():
    print("AcademiQ — ML Risk Model Training")
    print("=" * 45)

    db = SessionLocal()

    # Extract features from real database
    print("Extracting features from database...")
    courses = db.query(Course).all()
    all_features = []
    for course in courses:
        features = extract_features_for_course(course.id, db)
        all_features.extend(features)
        print(f"  Course {course.code}: {len(features)} students extracted")

    db.close()

    if not all_features:
        print("No data found. Make sure seed_data.py has been run.")
        return

    # Augment with synthetic data for training
    print(f"\nReal students extracted: {len(all_features)}")
    print("Augmenting with synthetic training data...")
    df = generate_synthetic_training_data(all_features)
    print(f"Total training samples: {len(df)}")

    # Prepare features and labels
    X = df[FEATURE_COLUMNS]
    y = df["at_risk"]

    print(f"\nClass distribution:")
    print(f"  Not at risk (0): {(y == 0).sum()}")
    print(f"  At risk     (1): {(y == 1).sum()}")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Train XGBoost model
    print("\nTraining XGBoost model...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
        verbosity=0,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred      = model.predict(X_test)
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    accuracy    = accuracy_score(y_test, y_pred)
    auc         = roc_auc_score(y_test, y_pred_prob)

    print(f"\nModel Evaluation:")
    print(f"  Accuracy : {accuracy:.2%}")
    print(f"  AUC-ROC  : {auc:.3f}")
    print(f"\nDetailed Report:")
    print(classification_report(y_test, y_pred,
          target_names=["Not at risk", "At risk"]))

    # Feature importance
    print("Feature Importance:")
    importance = dict(zip(FEATURE_COLUMNS, model.feature_importances_))
    for feat, imp in sorted(importance.items(), key=lambda x: -x[1]):
        bar = "█" * int(imp * 40)
        print(f"  {feat:20s} {imp:.3f} {bar}")

    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved to: {MODEL_PATH}")
    print("Training complete!")


if __name__ == "__main__":
    train()