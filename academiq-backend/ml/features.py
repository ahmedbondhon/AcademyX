"""
AcademiQ — Feature Engineering (Early Alert by Week 6)
Extracts features from early continuous assessment marks for the ML model.
"""
from sqlalchemy.orm import Session
from collections import defaultdict
from models.db_models import (
    StudentMark, Assessment, User, CourseLearningOutcome
)

# Using CLOs instead of COs for features
FEATURE_COLUMNS = [
    "early_pct",
    "submission_rate",
    "clo1_early_pct",
    "clo2_early_pct",
    "clo3_early_pct",
    "clo4_early_pct"
]

def extract_features_for_course(course_id: int, db: Session) -> list:
    """
    Extract features from Week 1-6 performance simulating the early alert point.
    """
    assessments = db.query(Assessment).filter(Assessment.course_id == course_id).all()
    if not assessments:
        return []

    # Filter for early alert strictly by Week 6 (DIU mid-semester indicator)
    early_assessments = [a for a in assessments if a.week <= 6]
    all_a_ids         = [a.id for a in assessments]
    early_a_ids       = [a.id for a in early_assessments]

    if not early_a_ids:
        return []

    all_marks   = db.query(StudentMark).filter(StudentMark.assessment_id.in_(all_a_ids)).all()
    early_marks = [m for m in all_marks if m.assessment_id in early_a_ids]

    # Fetch CLOs dynamically to map early marks
    clos = db.query(CourseLearningOutcome).filter(CourseLearningOutcome.course_id == course_id).order_by(CourseLearningOutcome.clo_number).all()

    s_marks_all   = defaultdict(list)
    s_marks_early = defaultdict(list)
    for m in all_marks: s_marks_all[m.student_id].append(m)
    for m in early_marks: s_marks_early[m.student_id].append(m)

    students = db.query(User).filter(User.id.in_(s_marks_all.keys())).all()
    features = []

    for student in students:
        sid     = student.id
        s_early = s_marks_early[sid]
        s_all   = s_marks_all[sid]

        # ── 1. Overall Early Percentage ────────────────
        obtained_early = sum(m.obtained for m in s_early)
        max_early      = sum(a.max_marks for a in early_assessments)
        early_pct      = (obtained_early / max_early * 100) if max_early > 0 else 0.0

        # ── 2. Early Submission Rate ───────────────────
        submission_rate = (len(s_early) / len(early_assessments)) if early_assessments else 0.0

        # ── 3. CLO-specific Early Performance ──────────
        clo_pcts = []
        for clo in clos:
            clo_assessments = [a for a in early_assessments if a.mapped_clo_id == clo.id]
            if not clo_assessments:
                clo_pcts.append(0.0)
                continue
            
            max_clo = sum(a.max_marks for a in clo_assessments)
            obtained_clo = sum(m.obtained for m in s_early if m.assessment_id in [ca.id for ca in clo_assessments])
            pct = (obtained_clo / max_clo * 100) if max_clo > 0 else 0.0
            clo_pcts.append(round(pct, 2))

        # Pad to exactly 4 CLO features for model consistency
        while len(clo_pcts) < 4:
            clo_pcts.append(0.0)
        clo_pcts = clo_pcts[:4]

        # ── 4. Target Label (Actual Final Outcome) ─────
        total_obtained = sum(m.obtained for m in s_all)
        total_max      = sum(a.max_marks for a in assessments if any(x.assessment_id == a.id for x in s_all))
        final_pct      = (total_obtained / total_max * 100) if total_max > 0 else 0.0
        at_risk        = 1 if final_pct < 60.0 else 0

        features.append({
            "student_id":        sid,
            "student_name":      student.name,
            "course_id":         course_id,
            "early_pct":         round(early_pct, 2),
            "submission_rate":   round(submission_rate, 2),
            "clo1_early_pct":    clo_pcts[0],
            "clo2_early_pct":    clo_pcts[1],
            "clo3_early_pct":    clo_pcts[2],
            "clo4_early_pct":    clo_pcts[3],
            "final_pct":         round(final_pct, 2),
            "at_risk":           at_risk
        })

    return features