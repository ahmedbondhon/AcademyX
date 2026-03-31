from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ── Auth Schemas (unchanged) ──────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ── OBE Schemas ───────────────────────────────

class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True

class CourseOut(BaseModel):
    id: int
    code: str
    name: str
    semester: str
    program_id: int
    faculty_id: int

    class Config:
        from_attributes = True

class CourseOutcomeOut(BaseModel):
    id: int
    course_id: int
    co_number: str
    description: str
    bloom_level: str

    class Config:
        from_attributes = True

class AssessmentOut(BaseModel):
    id: int
    course_id: int
    title: str
    type: str
    max_marks: float
    mapped_co_id: int
    week: int

    class Config:
        from_attributes = True

class StudentMarkOut(BaseModel):
    id: int
    student_id: int
    assessment_id: int
    obtained: float
    submitted_at: datetime

    class Config:
        from_attributes = True

class COAttainmentResult(BaseModel):
    co: str
    description: str
    attainment_pct: float
    level: int
    threshold_met: bool

class RiskResult(BaseModel):
    student_id: int
    student_name: str
    risk_score: float
    risk_level: str
    at_risk_cos: List[str]