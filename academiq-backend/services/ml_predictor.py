import os
import pickle
import pandas as pd
from sqlalchemy.orm import Session
from ml.features import extract_features_for_course, FEATURE_COLUMNS
from models.db_models import CourseOutcome, Assessment, StudentMark

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
        row   = pd.DataFrame([{col: f[col] for col in FEATURE_COLUMNS}])
        score = float(model.predict_proba(row)[0][1])

        # Determine which COs are at risk for this student
        at_risk_cos = []
        co_scores   = {
            "CO1": f["co1_early_pct"],
            "CO2": f["co2_early_pct"],
            "CO3": f["co3_early_pct"],
            "CO4": f["co4_early_pct"],
        }
        for co, pct in co_scores.items():
            if pct < 60.0 and pct > 0:
                at_risk_cos.append(co)

        results.append({
            "student_id":   f["student_id"],
            "student_name": f["student_name"],
            "risk_score":   round(score, 3),
            "risk_level":   (
                "high"   if score > 0.65 else
                "medium" if score > 0.35 else
                "low"
            ),
            "risk_pct":     round(score * 100, 1),
            "at_risk_cos":  at_risk_cos,
            "early_pct":    f["early_pct"],
            "final_pct":    f["final_pct"],
        })

    # Sort by risk score — highest first
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results


def predict_single_student(
    student_id: int, course_id: int, db: Session
) -> dict:
    """
    Risk prediction for one specific student.
    Used for the student's own dashboard view.
    """
    all_results = predict_course_risk(course_id, db)
    match = next(
        (r for r in all_results if r["student_id"] == student_id),
        None
    )
    if not match:
        return {"error": "Student not found in this course"}
    return match