import pickle
import os
import pandas as pd
from sqlalchemy.orm import Session
from ml.features import extract_features_for_course, FEATURE_COLUMNS

# Use the same path your train.py used to save the model
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models", "risk_model_v1.pkl"
)

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def predict_course_risk(course_id: int, db: Session):
    """
    Uses the trained model to predict which students are at risk 
    in a specific course.
    """
    model = load_model()
    if not model:
        return {"error": "Model not trained. Run 'python ml/train.py' first."}

    # 1. Use your existing features.py logic to get student data
    student_data = extract_features_for_course(course_id, db) #
    if not student_data:
        return {"message": "No early assessment data (Week 1-6) found for this course."}

    df = pd.DataFrame(student_data)
    
    # 2. Run the prediction
    # We only pass the specific FEATURE_COLUMNS the model was trained on
    X = df[FEATURE_COLUMNS] #
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    # 3. Format the results for the Frontend
    at_risk_students = []
    for i, row in df.iterrows():
        if predictions[i] == 1:
            at_risk_students.append({
                "student_id": int(row["student_id"]),
                "name": row["student_name"],
                "risk_score": round(float(probabilities[i]) * 100, 2),
                "status": "High Risk" if probabilities[i] > 0.7 else "Moderate Risk"
            })

    return {
        "course_id": course_id,
        "total_students": len(df),
        "at_risk_count": len(at_risk_students),
        "at_risk_students": at_risk_students
    }

def predict_single_student(student_id: int, course_id: int, db: Session):
    """
    Predict risk for one specific student (for their personal dashboard).
    """
    results = predict_course_risk(course_id, db)
    if "error" in results: return results
    
    # Find this specific student in the results
    for student in results.get("at_risk_students", []):
        if student["student_id"] == student_id:
            return student
            
    return {"status": "Safe", "risk_score": 0}