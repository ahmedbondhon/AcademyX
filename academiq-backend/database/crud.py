from sqlalchemy.orm import Session
from models.db_models import (
    User, Department, Program, Course,
    CourseOutcome, Assessment, StudentMark,
    ProgramOutcome, COPOMapping
)
import bcrypt

# ── User CRUD (unchanged) ─────────────────────

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, name: str, email: str, password: str, role: str = "student"):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(name=name, email=email, hashed_password=hashed, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(User).all()

def get_students(db: Session):
    return db.query(User).filter(User.role == "student").all()

# ── Department CRUD ───────────────────────────

def get_all_departments(db: Session):
    return db.query(Department).all()

def get_department_by_id(db: Session, dept_id: int):
    return db.query(Department).filter(Department.id == dept_id).first()

# ── Course CRUD ───────────────────────────────

def get_all_courses(db: Session):
    return db.query(Course).all()

def get_course_by_id(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()

def get_courses_by_faculty(db: Session, faculty_id: int):
    return db.query(Course).filter(Course.faculty_id == faculty_id).all()

# ── Course Outcome CRUD ───────────────────────

def get_cos_by_course(db: Session, course_id: int):
    return db.query(CourseOutcome).filter(
        CourseOutcome.course_id == course_id
    ).all()

# ── Assessment CRUD ───────────────────────────

def get_assessments_by_course(db: Session, course_id: int):
    return db.query(Assessment).filter(
        Assessment.course_id == course_id
    ).all()

def get_assessments_by_co(db: Session, co_id: int):
    return db.query(Assessment).filter(
        Assessment.mapped_co_id == co_id
    ).all()

# ── Student Marks CRUD ────────────────────────

def get_marks_by_assessment(db: Session, assessment_id: int):
    return db.query(StudentMark).filter(
        StudentMark.assessment_id == assessment_id
    ).all()

def get_marks_by_student_course(db: Session, student_id: int, course_id: int):
    assessments = get_assessments_by_course(db, course_id)
    a_ids = [a.id for a in assessments]
    return db.query(StudentMark).filter(
        StudentMark.student_id == student_id,
        StudentMark.assessment_id.in_(a_ids)
    ).all()

def create_mark(db: Session, student_id: int, assessment_id: int, obtained: float):
    mark = StudentMark(
        student_id=student_id,
        assessment_id=assessment_id,
        obtained=obtained
    )
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark