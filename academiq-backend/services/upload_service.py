import io
import pandas as pd
from sqlalchemy.orm import Session
from models.db_models import StudentMark, Assessment, User, Course

REQUIRED_COLUMNS = {"student_id", "assessment_id", "obtained_marks"}

def parse_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """
    Parse uploaded CSV or Excel file into a DataFrame.
    Supports .csv, .xlsx, .xls
    """
    ext = filename.lower().split(".")[-1]

    if ext == "csv":
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Use .csv, .xlsx or .xls")

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def validate_dataframe(df: pd.DataFrame, db: Session) -> dict:
    """
    Validate the uploaded dataframe.
    Returns dict with valid rows, errors, and summary.
    """
    errors  = []
    valid   = []

    # Check required columns exist
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return {
            "valid":   False,
            "errors":  [f"Missing columns: {', '.join(missing)}"],
            "rows":    [],
            "summary": {}
        }

    for i, row in df.iterrows():
        row_num = i + 2  # +2 because row 1 is header
        row_errors = []

        # Validate student_id
        try:
            sid = int(row["student_id"])
            student = db.query(User).filter(
                User.id == sid, User.role == "student"
            ).first()
            if not student:
                row_errors.append(f"Student ID {sid} not found")
        except (ValueError, TypeError):
            row_errors.append(f"Invalid student_id: {row['student_id']}")
            sid = None

        # Validate assessment_id
        try:
            aid = int(row["assessment_id"])
            assessment = db.query(Assessment).filter(
                Assessment.id == aid
            ).first()
            if not assessment:
                row_errors.append(f"Assessment ID {aid} not found")
        except (ValueError, TypeError):
            row_errors.append(f"Invalid assessment_id: {row['assessment_id']}")
            assessment = None
            aid = None

        # Validate obtained_marks
        try:
            obtained = float(row["obtained_marks"])
            if assessment and obtained > assessment.max_marks:
                row_errors.append(
                    f"Marks {obtained} exceeds max {assessment.max_marks}"
                )
            if obtained < 0:
                row_errors.append("Marks cannot be negative")
        except (ValueError, TypeError):
            row_errors.append(f"Invalid marks: {row['obtained_marks']}")
            obtained = None

        if row_errors:
            errors.append({
                "row": row_num,
                "errors": row_errors
            })
        else:
            valid.append({
                "student_id":    sid,
                "assessment_id": aid,
                "obtained":      obtained,
            })

    return {
        "valid":   len(errors) == 0,
        "errors":  errors,
        "rows":    valid,
        "summary": {
            "total_rows":   len(df),
            "valid_rows":   len(valid),
            "error_rows":   len(errors),
        }
    }


def save_marks(validated_rows: list, db: Session) -> dict:
    """
    Save validated marks to database.
    Skips duplicates (same student + assessment).
    """
    inserted  = 0
    skipped   = 0

    for row in validated_rows:
        # Check if mark already exists
        existing = db.query(StudentMark).filter(
            StudentMark.student_id    == row["student_id"],
            StudentMark.assessment_id == row["assessment_id"]
        ).first()

        if existing:
            # Update existing mark
            existing.obtained = row["obtained"]
            skipped += 1
        else:
            mark = StudentMark(
                student_id    = row["student_id"],
                assessment_id = row["assessment_id"],
                obtained      = row["obtained"]
            )
            db.add(mark)
            inserted += 1

    db.commit()
    return {"inserted": inserted, "updated": skipped}


def generate_template(course_id: int, db: Session) -> bytes:
    """
    Generate a downloadable Excel template for a course.
    Pre-filled with student IDs and assessment IDs
    so faculty just need to fill in the marks.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise ValueError("Course not found")

    assessments = db.query(Assessment).filter(
        Assessment.course_id == course_id
    ).all()

    students = db.query(User).filter(User.role == "student").all()

    rows = []
    for student in students:
        for assessment in assessments:
            existing = db.query(StudentMark).filter(
                StudentMark.student_id    == student.id,
                StudentMark.assessment_id == assessment.id
            ).first()
            rows.append({
                "student_id":    student.id,
                "student_name":  student.name,
                "assessment_id": assessment.id,
                "assessment":    assessment.title,
                "max_marks":     assessment.max_marks,
                "obtained_marks": existing.obtained if existing else "",
            })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Marks")

        # Style the header row
        ws = writer.sheets["Marks"]
        for cell in ws[1]:
            cell.font = __import__(
                "openpyxl.styles", fromlist=["Font"]
            ).Font(bold=True)

    output.seek(0)
    return output.read()