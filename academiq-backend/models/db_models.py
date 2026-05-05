from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from database.connection import Base
from datetime import datetime

# ── Auth Tables ──────────────────────────────
class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="student")
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

# ── NEW: DIU/UGC OBE Tables ──────────────────

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
    code          = Column(String, nullable=False)
    name          = Column(String, nullable=False)
    semester      = Column(String, nullable=False)
    program_id    = Column(Integer, ForeignKey("programs.id"))
    faculty_id    = Column(Integer, ForeignKey("users.id"))

class CourseLearningOutcome(Base):  # Renamed from CourseLearningOutcome
    __tablename__ = "course_learning_outcomes"
    id                = Column(Integer, primary_key=True, index=True)
    course_id         = Column(Integer, ForeignKey("courses.id"))
    clo_number        = Column(String, nullable=False)     # e.g., "CLO1"
    description       = Column(Text, nullable=False)
    bloom_level       = Column(String, nullable=True)      # e.g., "C4-Analyze"
    knowledge_profile = Column(String, nullable=True)      # e.g., "K3", "K4"
    domain            = Column(String, default="Cognitive") # Cognitive, Affective, Psychomotor

class Assessment(Base):
    __tablename__ = "assessments"
    id            = Column(Integer, primary_key=True, index=True)
    course_id     = Column(Integer, ForeignKey("courses.id"))
    title         = Column(String, nullable=False)
    type          = Column(String, nullable=False)         # "quiz", "midterm", "assignment", "final", "lab_project"
    max_marks     = Column(Float, nullable=False)
    mapped_clo_id = Column(Integer, ForeignKey("course_learning_outcomes.id")) # Renamed Foreign Key
    week          = Column(Integer, default=1)

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
    po_number   = Column(String, nullable=False)           # e.g., "PO1"
    description = Column(Text, nullable=False)

class CLOPLOMapping(Base): # Renamed from CLOPLOMapping
    __tablename__ = "clo_plo_mappings"
    id            = Column(Integer, primary_key=True, index=True)
    clo_id        = Column(Integer, ForeignKey("course_learning_outcomes.id"))
    po_id         = Column(Integer, ForeignKey("program_outcomes.id"))
    correlation   = Column(Integer, default=3)             # 1=Low, 2=Medium, 3=High
    