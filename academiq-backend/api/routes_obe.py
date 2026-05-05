from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from core.security import get_current_user
from services.obe_engine import (
    compute_clo_attainment,
    compute_plo_attainment,
    get_student_clo_breakdown,
    get_course_summary,
)
# Import your predictor to fix the 404 for Risk routes
from ml.ml_predictor import predict_course_risk, predict_single_student
from models.db_models import Course, Program

router = APIRouter()

# ── CLO/CO Attainment ─────────────────────────────
# Support both 'clo' and 'co' for frontend compatibility
@router.get("/clo-attainment/{course_id}")
@router.get("/co-attainment/{course_id}")
def get_clo_attainment(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return {
        "course_id": course_id,
        "course_code": course.code,
        "course_name": course.name,
        "semester": course.semester,
        "results": compute_clo_attainment(course_id, db)
    }

# ── PLO/PO Attainment ─────────────────────────────
@router.get("/plo-attainment/{program_id}")
@router.get("/po-attainment/{program_id}")
def get_plo_attainment(program_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    return {
        "program_id": program_id,
        "program_name": program.name,
        "results": compute_plo_attainment(program_id, db)
    }

# ── Risk Prediction Routes ─────────────────────
# Frontend is calling /api/obe/risk/ and /api/obe/my-risk/
@router.get("/risk/{course_id}")
def get_course_risk(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return predict_course_risk(course_id, db)

@router.get("/my-risk/{course_id}")
def get_my_risk(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return predict_single_student(current_user["user_id"], course_id, db)

# ── Student Portfolios ─────────────────────────
@router.get("/student-breakdown/{course_id}/{student_id}")
@router.get("/student-breakdown/{course_id}") # Alias for student's own view
def get_specific_student_breakdown(course_id: int, student_id: int = None, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # If student_id isn't provided, use the logged-in user (for student dashboard)
    target_id = student_id if student_id else current_user["user_id"]
    
    if current_user["role"] not in ["faculty", "dean", "admin"] and current_user["user_id"] != target_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return get_student_clo_breakdown(course_id, target_id, db)

@router.get("/my-breakdown/{course_id}")
def get_my_breakdown(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return get_student_clo_breakdown(course_id, current_user["user_id"], db)

# ── Course Summaries ──────────────────────────
@router.get("/course-summary/all/")
@router.get("/all-courses") # Direct fix for "Failed to load courses"
def get_all_course_summaries(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    courses = db.query(Course).all()
    return [get_course_summary(course.id, db) for course in courses]

@router.get("/course-summary/{course_id}")
def get_single_course_summary(course_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    summary = get_course_summary(course_id, db)
    if not summary:
        raise HTTPException(status_code=404, detail="Course not found")
    return summary