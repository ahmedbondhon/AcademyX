from sqlalchemy.orm import Session
from collections import defaultdict
from models.db_models import (
    Course, CourseLearningOutcome, Assessment,
    StudentMark, ProgramOutcome, CLOPLOMapping, Program, User
)

# ── Constants ─────────────────────────────────
ATTAINMENT_THRESHOLD   = 0.60   # Student must score >= 60% to "attain" a CLO
CLASS_PASS_THRESHOLD   = 0.60   # 60% of class must attain for CLO to be "met"
LEVEL_3_THRESHOLD      = 70.0   # Attainment % → Level 3 (Excellent)
LEVEL_2_THRESHOLD      = 50.0   # Attainment % → Level 2 (Satisfactory)

# ── Helpers ───────────────────────────────────
def get_level(pct: float) -> int:
    if pct >= LEVEL_3_THRESHOLD: return 3
    elif pct >= LEVEL_2_THRESHOLD: return 2
    return 1

def get_level_label(level: int) -> str:
    return {3: "Excellent", 2: "Satisfactory", 1: "Needs Improvement"}.get(level, "Unknown")

# ── 1. CLO Attainment (Class Level) ───────────
def compute_clo_attainment(course_id: int, db: Session) -> list:
    """Computes overall CLO attainment for a course across all students."""
    clos = db.query(CourseLearningOutcome).filter(CourseLearningOutcome.course_id == course_id).all()
    results = []

    for clo in clos:
        assessments = db.query(Assessment).filter(Assessment.mapped_clo_id == clo.id).all()
        if not assessments:
            continue
            
        assessment_ids = [a.id for a in assessments]
        
        # Split DIU Assessment Patterns: Continuous (CA) vs Summative (SEE)
        ca_marks = sum(a.max_marks for a in assessments if a.type != "final")
        see_marks = sum(a.max_marks for a in assessments if a.type == "final")
        total_max_marks = ca_marks + see_marks

        marks = db.query(StudentMark).filter(StudentMark.assessment_id.in_(assessment_ids)).all()
        
        student_totals = defaultdict(float)
        for m in marks:
            student_totals[m.student_id] += m.obtained

        total_students = len(student_totals)
        if total_students == 0:
            continue

        passed_students = sum(1 for score in student_totals.values() if (score / total_max_marks) >= ATTAINMENT_THRESHOLD)
        
        attainment_pct = (passed_students / total_students) * 100
        level = get_level(attainment_pct)

        results.append({
            "clo_id": clo.id,
            "clo_number": clo.clo_number,
            "description": clo.description,
            "bloom_level": clo.bloom_level,
            "knowledge_profile": clo.knowledge_profile,
            "domain": clo.domain,
            "total_marks": total_max_marks,
            "ca_weight": ca_marks,
            "see_weight": see_marks,
            "total_students": total_students,
            "passed_students": passed_students,
            "attainment_pct": round(attainment_pct, 2),
            "level": level,
            "level_label": get_level_label(level),
            "threshold_met": (passed_students / total_students) >= CLASS_PASS_THRESHOLD
        })

    return results

# ── 2. PLO Attainment (Program Level) ─────────
def compute_plo_attainment(program_id: int, db: Session) -> list:
    """Rolls up CLO attainments into Program Learning Outcomes (PLOs) based on mapping correlation."""
    plos = db.query(ProgramOutcome).filter(ProgramOutcome.program_id == program_id).all()
    courses = db.query(Course).filter(Course.program_id == program_id).all()
    
    # Precompute all CLO attainments in the program
    all_clo_attainments = {}
    for course in courses:
        course_clos = compute_clo_attainment(course.id, db)
        for c in course_clos:
            all_clo_attainments[c["clo_id"]] = c["attainment_pct"]

    results = []
    for plo in plos:
        mappings = db.query(CLOPLOMapping).filter(CLOPLOMapping.po_id == plo.id).all()
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for mapping in mappings:
            clo_pct = all_clo_attainments.get(mapping.clo_id)
            if clo_pct is not None:
                # Weight by correlation: 1 (Low), 2 (Medium), 3 (High)
                correlation_weight = mapping.correlation / 3.0
                total_weighted_score += (clo_pct * correlation_weight)
                total_weight += correlation_weight
                
        plo_attainment = (total_weighted_score / total_weight) if total_weight > 0 else 0.0
        level = get_level(plo_attainment)
        
        results.append({
            "plo_id": plo.id,
            "plo_number": plo.po_number,
            "description": plo.description,
            "attainment_pct": round(plo_attainment, 2),
            "level": level,
            "level_label": get_level_label(level),
            "contributing_clos": len(mappings)
        })
        
    return results

# ── 3. Student-Level Breakdown ────────────────
def get_student_clo_breakdown(course_id: int, student_id: int, db: Session) -> dict:
    """Calculates exact CLO attainment for an individual student (for portfolios)."""
    student = db.query(User).filter(User.id == student_id).first()
    clos = db.query(CourseLearningOutcome).filter(CourseLearningOutcome.course_id == course_id).all()
    
    breakdown = []
    total_course_marks = 0
    total_obtained = 0
    
    for clo in clos:
        assessments = db.query(Assessment).filter(Assessment.mapped_clo_id == clo.id).all()
        assessment_ids = [a.id for a in assessments]
        
        max_marks = sum(a.max_marks for a in assessments)
        marks = db.query(StudentMark).filter(
            StudentMark.assessment_id.in_(assessment_ids),
            StudentMark.student_id == student_id
        ).all()
        
        obtained_marks = sum(m.obtained for m in marks)
        total_course_marks += max_marks
        total_obtained += obtained_marks
        
        pct = (obtained_marks / max_marks * 100) if max_marks > 0 else 0.0
        
        breakdown.append({
            "clo_number": clo.clo_number,
            "description": clo.description,
            "max_marks": max_marks,
            "obtained_marks": round(obtained_marks, 2),
            "percentage": round(pct, 2),
            "status": "Attained" if pct >= (ATTAINMENT_THRESHOLD * 100) else "Not Attained"
        })
        
    return {
        "student_name": student.name,
        "student_id": student.id,
        "total_percentage": round((total_obtained / total_course_marks * 100) if total_course_marks > 0 else 0, 2),
        "clos": breakdown
    }

# ── 4. Course Summary ─────────────────────────
def get_course_summary(course_id: int, db: Session) -> dict:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: return {}

    # 1. Existing Math
    clo_results = compute_clo_attainment(course_id, db)
    total_clos = len(clo_results)
    met_clos = sum(1 for r in clo_results if r["attainment_pct"] >= 60.0)
    avg_attainment = round(sum(r["attainment_pct"] for r in clo_results) / total_clos if total_clos > 0 else 0.0, 2)

    # 2. Get All Assessments (for Table Headers)
    assessments = db.query(Assessment).filter(Assessment.course_id == course_id).order_by(Assessment.id).all()
    assessment_list = [{"id": a.id, "title": a.title, "max_marks": a.max_marks} for a in assessments]

    # 3. Get Students and their Marks (for Table Rows)
    # We find all students who have at least one mark in this course
    student_ids = db.query(StudentMark.student_id).filter(
        StudentMark.assessment_id.in_([a.id for a in assessments])
    ).distinct().all()
    
    student_list = []
    for (s_id,) in student_ids:
        student_user = db.query(User).filter(User.id == s_id).first()
        if not student_user: continue

        # Get marks for this specific student
        marks = db.query(StudentMark).filter(
            StudentMark.student_id == s_id,
            StudentMark.assessment_id.in_([a.id for a in assessments])
        ).all()

        # Create a map of {assessment_id: obtained_marks}
        marks_map = {m.assessment_id: float(m.obtained) for m in marks}
        
        # Calculate total percentage for this student
        total_obtained = sum(marks_map.values())
        total_possible = sum(a.max_marks for a in assessments)
        percentage = (total_obtained / total_possible * 100) if total_possible > 0 else 0

        student_list.append({
            "id": s_id,
            "name": student_user.name,
            "student_id_no": getattr(student_user, 'student_id_no', f"ID-{s_id}"),
            "marks": marks_map,
            "total_percentage": round(percentage, 2)
        })

    return {
        "course_id": course.id,
        "course_code": course.code,
        "course_name": course.name,
        "total_clos": total_clos,
        "met_clos": met_clos,
        "avg_attainment": avg_attainment,
        "student_count": len(student_list),
        "assessments": assessment_list, # The UI needs this for headers!
        "students": student_list        # The UI needs this for rows!
    }