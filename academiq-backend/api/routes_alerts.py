from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from core.security import get_current_user
from services.alert_service import trigger_course_alerts

router = APIRouter()

@router.post("/trigger/{course_id}")
def trigger_alerts(
    course_id: int,
    dry_run: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger alerts for at-risk students in a course.
    dry_run=true  → preview alerts without sending emails
    dry_run=false → send real emails (needs SMTP config)
    Faculty and dean only.
    """
    if current_user["role"] not in ["faculty", "dean", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Faculty access required"
        )

    result = trigger_course_alerts(
        course_id=course_id,
        db=db,
        dry_run=dry_run
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/preview/{course_id}")
def preview_alerts(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Preview who would receive alerts without sending anything.
    Always safe to call.
    """
    if current_user["role"] not in ["faculty", "dean", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Faculty access required"
        )

    result = trigger_course_alerts(
        course_id=course_id,
        db=db,
        dry_run=True
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result