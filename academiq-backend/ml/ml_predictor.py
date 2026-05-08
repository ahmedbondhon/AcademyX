import pickle
import os
import pandas as pd
from sqlalchemy.orm import Session
from ml.features import extract_features_for_course, FEATURE_COLUMNS

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models", "risk_model_v1.pkl"
)

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None

def predict_course_risk(course_id: int, db: Session):
    model = load_model()
    
    # 1. Get student data safely
    try:
        student_data = extract_features_for_course(course_id, db)
    except Exception as e:
        student_data = []

    # If empty (because of Week 6 filter or no data), return empty list safely
    if not student_data:
        return {"course_id": course_id, "students": []}

    df = pd.DataFrame(student_data)
    
    results = []
    for i, row in df.iterrows():
        early_pct = row.get("early_pct", 50) # Fallback to 50% if missing
        
        # 2. Try ML, fallback to Heuristics
        if model and all(col in df.columns for col in FEATURE_COLUMNS):
            try:
                X = df.iloc[[i]][FEATURE_COLUMNS]
                risk_prob = float(model.predict_proba(X)[0][1])
            except Exception:
                risk_prob = (100 - early_pct) / 100.0
        else:
            # Fallback Heuristic: Risk is the inverse of their early performance
            risk_prob = (100 - early_pct) / 100.0
            
        risk_score = round(risk_prob * 100, 1)
        
        # Build the exact dictionary the UI and Alerts expect
        results.append({
            "student_id": int(row["student_id"]),
            "name": row.get("student_name", f"Student {int(row['student_id'])}"),
            "risk_score": risk_score,
            "at_risk_cos": row.get("at_risk_cos", []), # Alert Service needs this!
            "status": "High Risk" if risk_score > 70 else ("Moderate Risk" if risk_score > 40 else "Low Risk")
        })

    # Return under the key "students" for FacultyDashboard.jsx
    return {
        "course_id": course_id,
        "students": results
    }

def predict_single_student(student_id: int, course_id: int, db: Session):
    risk_data = predict_course_risk(course_id, db)
    students = risk_data.get("students", [])
    for s in students:
        if s["student_id"] == student_id:
            return s
    return {"student_id": student_id, "risk_score": 0, "status": "No Data", "at_risk_cos": []}