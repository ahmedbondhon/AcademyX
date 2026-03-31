from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from core.security import get_current_user
from services.obe_engine import (
    compute_co_attainment,
    compute_po_attainment,
    get_student_co_breakdown,
    get_course_summary,
)
from models.db_models import Course, Program
from database.crud import get_courses_by_faculty
from services.ml_predictor import predict_course_risk, predict_single_student


router = APIRouter()

# ── CO Attainment ─────────────────────────────

@router.get("/co-attainment/{course_id}")
def get_co_attainment(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    results = compute_co_attainment(course_id, db)
    return {
        "course_id":   course_id,
        "course_name": course.name,
        "semester":    course.semester,
        "results":     results
    }

# ── PO Attainment ─────────────────────────────

@router.get("/po-attainment/{program_id}")
def get_po_attainment(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    results = compute_po_attainment(program_id, db)
    return {
        "program_id":   program_id,
        "program_name": program.name,
        "results":      results
    }

# ── Student CO Breakdown ──────────────────────

@router.get("/student-breakdown/{course_id}")
def get_student_breakdown(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    student_id = current_user["user_id"]
    results    = get_student_co_breakdown(student_id, course_id, db)
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No data found for this student in this course"
        )
    return {
        "student_id": student_id,
        "course_id":  course_id,
        "breakdown":  results
    }

# ── Course Summary ────────────────────────────

@router.get("/course-summary/{course_id}")
def get_course_summary_endpoint(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    summary = get_course_summary(course_id, db)
    if not summary:
        raise HTTPException(status_code=404, detail="Course not found")
    return summary

# ── Faculty — all their courses ───────────────

@router.get("/my-courses")
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    courses = get_courses_by_faculty(db, current_user["user_id"])
    result  = []
    for course in courses:
        summary = get_course_summary(course.id, db)
        result.append(summary)
    return result

# ── All courses overview (dean only) ──────────

@router.get("/all-courses")
def get_all_courses_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["dean", "admin"]:
        raise HTTPException(status_code=403, detail="Dean access required")

    courses = db.query(Course).all()
    result  = []
    for course in courses:
        summary = get_course_summary(course.id, db)
        result.append(summary)
    return result

@router.get("/risk/{course_id}")
def get_course_risk(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get risk scores for all students in a course.
    Faculty and dean only.
    """
    if current_user["role"] not in ["faculty", "dean", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Faculty access required"
        )
    results = predict_course_risk(course_id, db)
    high    = [r for r in results if r.get("risk_level") == "high"]
    medium  = [r for r in results if r.get("risk_level") == "medium"]
    low     = [r for r in results if r.get("risk_level") == "low"]
    return {
        "course_id":    course_id,
        "total":        len(results),
        "high_risk":    len(high),
        "medium_risk":  len(medium),
        "low_risk":     len(low),
        "students":     results
    }

@router.get("/my-risk/{course_id}")
def get_my_risk(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Student sees their own risk score.
    """
    result = predict_single_student(
        current_user["user_id"], course_id, db
    )
    return result