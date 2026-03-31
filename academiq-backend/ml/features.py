"""
Feature engineering — converts raw marks data
into features the ML model can learn from.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
from models.db_models import (
    StudentMark, Assessment, User, Course
)

def extract_features_for_course(course_id: int, db: Session) -> list:
    """
    For every student in a course, extract features
    from their Week 1-6 performance only.
    This simulates what we know at the early alert point.
    Returns list of dicts — one per student.
    """
    # Get all assessments for this course
    assessments = db.query(Assessment).filter(
        Assessment.course_id == course_id
    ).all()

    if not assessments:
        return []

    # Split into early (week <= 6) and all assessments
    early_assessments = [a for a in assessments if a.week <= 9]
    all_a_ids         = [a.id for a in assessments]
    early_a_ids       = [a.id for a in early_assessments]

    if not early_a_ids:
        return []

    # Get all marks
    all_marks   = db.query(StudentMark).filter(
        StudentMark.assessment_id.in_(all_a_ids)
    ).all()
    early_marks = [m for m in all_marks if m.assessment_id in early_a_ids]

    # Find all students
    student_ids = list(set(m.student_id for m in all_marks))

    features = []

    for sid in student_ids:
        student = db.query(User).filter(User.id == sid).first()
        if not student:
            continue

        # ── Early marks features ──────────────────
        s_early = [m for m in early_marks if m.student_id == sid]
        s_all   = [m for m in all_marks   if m.student_id == sid]

        # Week 1-6 performance %
        early_obtained = sum(m.obtained for m in s_early)
        early_max      = sum(
            a.max_marks for a in early_assessments
            if any(m.assessment_id == a.id for m in s_early)
        )
        early_pct = round(
            (early_obtained / early_max * 100) if early_max > 0 else 0.0, 2
        )

        # Assignment submission rate (week 1-6)
        early_assignments = [
            a for a in early_assessments if a.type == "assignment"
        ]
        submitted = sum(
            1 for a in early_assignments
            if any(m.assessment_id == a.id and m.student_id == sid
                   for m in early_marks)
        )
        submission_rate = round(
            (submitted / len(early_assignments) * 100)
            if early_assignments else 100.0,
            2
        )

        # ── CO-level early scores ─────────────────
        # Group early marks by CO
        co_scores = defaultdict(lambda: {"obtained": 0.0, "max": 0.0})
        for mark in s_early:
            assessment = next(
                (a for a in early_assessments if a.id == mark.assessment_id),
                None
            )
            if assessment and assessment.mapped_co_id:
                co_scores[assessment.mapped_co_id]["obtained"] += mark.obtained
                co_scores[assessment.mapped_co_id]["max"]      += assessment.max_marks

        # Get CO scores as percentages (up to 4 COs)
        co_pcts = []
        for co_id, vals in sorted(co_scores.items()):
            pct = (vals["obtained"] / vals["max"] * 100) if vals["max"] > 0 else 0.0
            co_pcts.append(round(pct, 2))

        # Pad to always have 4 CO features
        while len(co_pcts) < 4:
            co_pcts.append(0.0)
        co_pcts = co_pcts[:4]

        # ── Final outcome (label) ─────────────────
        # Did student score >= 60% overall? (what we're trying to predict)
        total_obtained = sum(m.obtained for m in s_all)
        total_max      = sum(
            a.max_marks for a in assessments
            if any(m.assessment_id == a.id for m in s_all)
        )
        final_pct = (total_obtained / total_max * 100) if total_max > 0 else 0.0
        at_risk   = 1 if final_pct < 60.0 else 0

        features.append({
            "student_id":        sid,
            "student_name":      student.name,
            "course_id":         course_id,
            # Features (inputs to the model)
            "early_pct":         early_pct,
            "submission_rate":   submission_rate,
            "co1_early_pct":     co_pcts[0],
            "co2_early_pct":     co_pcts[1],
            "co3_early_pct":     co_pcts[2],
            "co4_early_pct":     co_pcts[3],
            # Label (what we want to predict)
            "at_risk":           at_risk,
            "final_pct":         round(final_pct, 2),
        })

    return features


FEATURE_COLUMNS = [
    "early_pct",
    "submission_rate",
    "co1_early_pct",
    "co2_early_pct",
    "co3_early_pct",
    "co4_early_pct",
]