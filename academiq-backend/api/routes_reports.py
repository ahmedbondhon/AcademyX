from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from core.security import get_current_user
from services.report_service import generate_obe_report
from models.db_models import Course
import io

router = APIRouter()

@router.get("/obe/{course_id}")
def download_obe_report(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate and download a full OBE PDF report for a course.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        pdf_bytes = generate_obe_report(course_id, db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )

    filename = (
        f"OBE_Report_{course.code}_{course.semester.replace(' ', '_')}.pdf"
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )