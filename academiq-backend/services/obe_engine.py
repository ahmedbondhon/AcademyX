from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
from models.db_models import (
    Course, CourseOutcome, Assessment,
    StudentMark, User, ProgramOutcome,
    COPOMapping, Program
)

# ── Constants ─────────────────────────────────
ATTAINMENT_THRESHOLD   = 0.60   # student must score >= 60% to "attain" a CO
CLASS_PASS_THRESHOLD   = 0.60   # 60% of class must attain for CO to be "met"
LEVEL_3_THRESHOLD      = 70.0   # attainment % → Level 3 (Excellent)
LEVEL_2_THRESHOLD      = 50.0   # attainment % → Level 2 (Satisfactory)
                                 # below 50%   → Level 1 (Needs Improvement)

# ── Helper ────────────────────────────────────

def get_level(pct: float) -> int:
    if pct >= LEVEL_3_THRESHOLD:
        return 3
    elif pct >= LEVEL_2_THRESHOLD:
        return 2
    return 1

def get_level_label(level: int) -> str:
    return {3: "Excellent", 2: "Satisfactory", 1: "Needs Improvement"}.get(level, "Unknown")

# ── Core Engine ───────────────────────────────

def compute_co_attainment(course_id: int, db: Session) -> list:
    """
    For each CO in a course:
    1. Find all assessments mapped to that CO
    2. For each student, sum their obtained vs max marks across those assessments
    3. Count how many students scored >= 60%
    4. Attainment % = (passing students / total students) * 100
    """
    cos = db.query(CourseOutcome).filter(
        CourseOutcome.course_id == course_id
    ).all()

    if not cos:
        return []

    results = []

    for co in cos:
        # Get all assessments mapped to this CO
        assessments = db.query(Assessment).filter(
            Assessment.course_id   == course_id,
            Assessment.mapped_co_id == co.id
        ).all()

        if not assessments:
            results.append({
                "co":             co.co_number,
                "co_id":          co.id,
                "description":    co.description,
                "bloom_level":    co.bloom_level,
                "attainment_pct": 0.0,
                "level":          1,
                "level_label":    "Needs Improvement",
                "threshold_met":  False,
                "total_students": 0,
                "passing_students": 0,
            })
            continue

        a_ids = [a.id for a in assessments]

        # Get all marks for these assessments
        all_marks = db.query(StudentMark).filter(
            StudentMark.assessment_id.in_(a_ids)
        ).all()

        if not all_marks:
            continue

        # Group marks by student
        student_obtained = defaultdict(float)
        student_max      = defaultdict(float)

        for mark in all_marks:
            assessment = next(a for a in assessments if a.id == mark.assessment_id)
            student_obtained[mark.student_id] += mark.obtained
            student_max[mark.student_id]      += assessment.max_marks

        total_students  = len(student_obtained)
        passing_students = sum(
            1 for sid in student_obtained
            if student_max[sid] > 0 and
               (student_obtained[sid] / student_max[sid]) >= ATTAINMENT_THRESHOLD
        )

        attainment_pct = round(
            (passing_students / total_students * 100) if total_students > 0 else 0.0,
            2
        )
        level = get_level(attainment_pct)

        results.append({
            "co":               co.co_number,
            "co_id":            co.id,
            "description":      co.description,
            "bloom_level":      co.bloom_level,
            "attainment_pct":   attainment_pct,
            "level":            level,
            "level_label":      get_level_label(level),
            "threshold_met":    attainment_pct >= (CLASS_PASS_THRESHOLD * 100),
            "total_students":   total_students,
            "passing_students": passing_students,
        })

    return results


def compute_po_attainment(program_id: int, db: Session) -> list:
    """
    For each PO in a program:
    Aggregate attainment from all COs mapped to it,
    weighted by the CO-PO mapping weight.
    """
    pos = db.query(ProgramOutcome).filter(
        ProgramOutcome.program_id == program_id
    ).all()

    if not pos:
        return []

    # Get all courses in this program
    courses = db.query(Course).filter(
        Course.program_id == program_id
    ).all()

    results = []

    for po in pos:
        # Get all CO-PO mappings for this PO
        mappings = db.query(COPOMapping).filter(
            COPOMapping.po_id == po.id
        ).all()

        if not mappings:
            results.append({
                "po":             po.po_number,
                "po_id":          po.id,
                "description":    po.description,
                "attainment_pct": 0.0,
                "level":          1,
                "level_label":    "Needs Improvement",
                "threshold_met":  False,
            })
            continue

        weighted_sum  = 0.0
        total_weight  = 0.0

        for mapping in mappings:
            co = db.query(CourseOutcome).filter(
                CourseOutcome.id == mapping.co_id
            ).first()
            if not co:
                continue

            # Get CO attainment for the course this CO belongs to
            co_results = compute_co_attainment(co.course_id, db)
            co_result  = next(
                (r for r in co_results if r["co_id"] == co.id), None
            )
            if co_result:
                weighted_sum  += co_result["attainment_pct"] * mapping.weight
                total_weight  += mapping.weight

        attainment_pct = round(
            weighted_sum / total_weight if total_weight > 0 else 0.0,
            2
        )
        level = get_level(attainment_pct)

        results.append({
            "po":             po.po_number,
            "po_id":          po.id,
            "description":    po.description,
            "attainment_pct": attainment_pct,
            "level":          level,
            "level_label":    get_level_label(level),
            "threshold_met":  attainment_pct >= (CLASS_PASS_THRESHOLD * 100),
        })

    return results


def get_student_co_breakdown(student_id: int, course_id: int, db: Session) -> list:
    """
    For a single student — show their score on each CO
    so they can see exactly where they are weak.
    """
    cos = db.query(CourseOutcome).filter(
        CourseOutcome.course_id == course_id
    ).all()

    results = []

    for co in cos:
        assessments = db.query(Assessment).filter(
            Assessment.course_id    == course_id,
            Assessment.mapped_co_id == co.id
        ).all()

        if not assessments:
            continue

        a_ids = [a.id for a in assessments]
        marks = db.query(StudentMark).filter(
            StudentMark.student_id.in_([student_id]),
            StudentMark.assessment_id.in_(a_ids)
        ).all()

        obtained = sum(m.obtained for m in marks)
        max_marks = sum(a.max_marks for a in assessments)
        pct = round((obtained / max_marks * 100) if max_marks > 0 else 0.0, 2)

        results.append({
            "co":          co.co_number,
            "description": co.description,
            "bloom_level": co.bloom_level,
            "obtained":    obtained,
            "max_marks":   max_marks,
            "percentage":  pct,
            "attained":    pct >= (ATTAINMENT_THRESHOLD * 100),
        })

    return results


def get_course_summary(course_id: int, db: Session) -> dict:
    """
    High level summary of a course —
    used for the dean dashboard overview card.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return {}

    co_results     = compute_co_attainment(course_id, db)
    total_cos      = len(co_results)
    met_cos        = sum(1 for r in co_results if r["threshold_met"])
    avg_attainment = round(
        sum(r["attainment_pct"] for r in co_results) / total_cos
        if total_cos > 0 else 0.0,
        2
    )

    # Count students enrolled
    assessments = db.query(Assessment).filter(
        Assessment.course_id == course_id
    ).first()
    student_count = 0
    if assessments:
        student_count = db.query(StudentMark.student_id).filter(
            StudentMark.assessment_id == assessments.id
        ).distinct().count()

    return {
        "course_id":       course.id,
        "course_code":     course.code,
        "course_name":     course.name,
        "semester":        course.semester,
        "total_cos":       total_cos,
        "cos_met":         met_cos,
        "cos_not_met":     total_cos - met_cos,
        "avg_attainment":  avg_attainment,
        "student_count":   student_count,
        "health":          "Good" if met_cos == total_cos
                           else ("Warning" if met_cos >= total_cos / 2
                           else "Critical"),
    }