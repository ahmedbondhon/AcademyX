from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from database.connection import Base
from datetime import datetime

# ── Existing Table (unchanged) ────────────────
class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="student")
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

# ── NEW: OBE Tables ───────────────────────────

class Department(Base):
    __tablename__ = "departments"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)

class Program(Base):
    __tablename__ = "programs"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))

class Course(Base):
    __tablename__ = "courses"
    id            = Column(Integer, primary_key=True, index=True)
    code          = Column(String, unique=True, nullable=False)
    name          = Column(String, nullable=False)
    semester      = Column(String, nullable=False)   # "Spring 2026"
    program_id    = Column(Integer, ForeignKey("programs.id"))
    faculty_id    = Column(Integer, ForeignKey("users.id"))

class CourseOutcome(Base):
    __tablename__ = "course_outcomes"
    id          = Column(Integer, primary_key=True, index=True)
    course_id   = Column(Integer, ForeignKey("courses.id"))
    co_number   = Column(String, nullable=False)     # "CO1", "CO2"
    description = Column(Text, nullable=False)
    bloom_level = Column(String, nullable=False)     # "Remember", "Analyze"

class Assessment(Base):
    __tablename__ = "assessments"
    id           = Column(Integer, primary_key=True, index=True)
    course_id    = Column(Integer, ForeignKey("courses.id"))
    title        = Column(String, nullable=False)
    type         = Column(String, nullable=False)    # "quiz","midterm","assignment","final"
    max_marks    = Column(Float, nullable=False)
    mapped_co_id = Column(Integer, ForeignKey("course_outcomes.id"))
    week         = Column(Integer, default=1)        # which week of semester

class StudentMark(Base):
    __tablename__ = "student_marks"
    id            = Column(Integer, primary_key=True, index=True)
    student_id    = Column(Integer, ForeignKey("users.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    obtained      = Column(Float, nullable=False)
    submitted_at  = Column(DateTime, default=datetime.utcnow)

class ProgramOutcome(Base):
    __tablename__ = "program_outcomes"
    id          = Column(Integer, primary_key=True, index=True)
    program_id  = Column(Integer, ForeignKey("programs.id"))
    po_number   = Column(String, nullable=False)     # "PO1", "PO2"
    description = Column(Text, nullable=False)

class COPOMapping(Base):
    __tablename__ = "co_po_mappings"
    id        = Column(Integer, primary_key=True, index=True)
    co_id     = Column(Integer, ForeignKey("course_outcomes.id"))
    po_id     = Column(Integer, ForeignKey("program_outcomes.id"))
    weight    = Column(Float, default=1.0)