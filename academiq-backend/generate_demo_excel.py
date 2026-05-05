"""
AcademiQ — Demo Excel Data Generator
Run: python generate_demo_excel.py
"""
import sys, os
import pandas as pd
import random

# Add current directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import SessionLocal
from models.db_models import User, Assessment, Course

def generate_demo_files():
    db = SessionLocal()
    
    print("=" * 60)
    print("  AcademiQ — Generating DIU Demo Marks Excel")
    print("=" * 60)

    # 1. Fetch Students
    students = db.query(User).filter(User.role == "student").all()
    if not students:
        print("  Error: No students found. Please run seed_data_diu.py first.")
        db.close()
        return
        
    courses = db.query(Course).all()
    all_rows = []
    
    # 2. Define performance profiles based on the seeded emails
    profiles = {
        "arafat@s.diu.edu.bd": {"base": 0.88, "variance": 0.08},  # Strong (A/A+)
        "imran@s.diu.edu.bd":  {"base": 0.65, "variance": 0.15},  # Average (B/B+)
        "milon@s.diu.edu.bd":  {"base": 0.40, "variance": 0.20}   # Weak / At-Risk (C/F)
    }
    
    # 3. Generate Marks
    for course in courses:
        assessments = db.query(Assessment).filter(Assessment.course_id == course.id).all()
        for student in students:
            # Fallback profile if adding more random students later
            profile = profiles.get(student.email, {"base": 0.7, "variance": 0.1})
            
            for assessment in assessments:
                # Calculate realistic marks with some randomization
                perf = profile["base"] + random.uniform(-profile["variance"], profile["variance"])
                perf = max(0.0, min(1.0, perf)) # Clamp between 0% and 100%
                
                obtained = round(assessment.max_marks * perf, 1)
                
                # The upload_service.py only cares about student_id, assessment_id, and obtained_marks.
                # The (reference) columns are ignored by the backend but help faculty read the Excel file.
                all_rows.append({
                    "course_code (reference)": course.code,
                    "student_id": student.id,
                    "student_name (reference)": student.name,
                    "assessment_id": assessment.id,
                    "assessment_name (reference)": assessment.title,
                    "max_marks (reference)": assessment.max_marks,
                    "obtained_marks": obtained
                })
                
    df = pd.DataFrame(all_rows)
    
    # 4. Save to files
    excel_path = "AcademiQ_DIU_Import_Template.xlsx"
    csv_path = "AcademiQ_DIU_Import_Template.csv"
    
    # Requires openpyxl installed (already in your requirements for the backend)
    df.to_excel(excel_path, index=False)
    df.to_csv(csv_path, index=False)
    
    db.close()
    
    print(f"  Generated {len(all_rows)} mark records.")
    print(f"  Saved Excel to: {excel_path}")
    print(f"  Saved CSV to  : {csv_path}")
    print("=" * 60)
    print("  These files are perfectly formatted and ready to be uploaded")
    print("  via the AcademiQ frontend Upload Marks page!")

if __name__ == "__main__":
    generate_demo_files()