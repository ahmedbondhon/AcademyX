"""
AcademiQ — Live ML Prediction Service
"""
import os
import pickle
import pandas as pd
from sqlalchemy.orm import Session
from ml.features import extract_features_for_course, FEATURE_COLUMNS

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ml", "models", "risk_model_v1.pkl"
)

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def predict_course_risk(course_id: int, db: Session) -> list:
    """
    Run risk prediction for all students in a course.
    Returns list of students sorted by risk score (highest first).
    """
    model = load_model()
    if not model:
        return [{"error": "Model not trained yet. Run: python ml/train.py"}]

    features = extract_features_for_course(course_id, db)
    if not features:
        return []

    results = []
    for f in features:
        row = pd.DataFrame([{col: f[col] for col in FEATURE_COLUMNS}])
        score = float(model.predict_proba(row)[0][1])

        # Determine which CLOs are driving the risk for this student
        at_risk_clos = []
        clo_scores = {
            "CLO1": f["clo1_early_pct"],
            "CLO2": f["clo2_early_pct"],
            "CLO3": f["clo3_early_pct"],
            "CLO4": f["clo4_early_pct"],
        }
        
        for clo, pct in clo_scores.items():
            if 0 < pct < 60.0:  # Student attempted but scored below threshold
                at_risk_clos.append(clo)

        results.append({
            "student_id":   f["student_id"],
            "student_name": f["student_name"],
            "risk_score":   round(score, 3),
            "risk_level":   "high" if score > 0.65 else "medium" if score > 0.35 else "low",
            "risk_pct":     round(score * 100, 1),
            "at_risk_clos": at_risk_clos,  # Updated from at_risk_cos
            "early_pct":    f["early_pct"],
            "final_pct":    f["final_pct"],
        })

    # Sort by highest risk first
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results

def predict_single_student(student_id: int, course_id: int, db: Session) -> dict:
    all_predictions = predict_course_risk(course_id, db)
    for p in all_predictions:
        if p.get("student_id") == student_id:
            return p
    return {"error": "Student data not found for this course"}
