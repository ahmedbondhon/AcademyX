from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from core.security import get_current_user
from services.upload_service import (
    parse_file, validate_dataframe,
    save_marks, generate_template
)
import io

router = APIRouter()

@router.post("/marksheet")
async def upload_marksheet(
    file: UploadFile = File(...),
    save: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a CSV or Excel marksheet.
    save=false → validate and preview only
    save=true  → validate and save to database
    """
    if current_user["role"] not in ["faculty", "dean", "admin"]:
        raise HTTPException(status_code=403, detail="Faculty access required")

    # Read file
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # Parse
    try:
        df = parse_file(contents, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Validate
    result = validate_dataframe(df, db)

    if save and result["valid"]:
        saved = save_marks(result["rows"], db)
        return {
            "status":  "saved",
            "summary": result["summary"],
            "saved":   saved,
            "errors":  result["errors"],
        }

    return {
        "status":  "preview" if not save else "validation_failed",
        "summary": result["summary"],
        "valid":   result["valid"],
        "errors":  result["errors"][:10],  # show max 10 errors
        "preview": result["rows"][:5],     # show first 5 valid rows
    }


@router.get("/template/{course_id}")
def download_template(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Download a pre-filled Excel template for a course.
    Faculty fills in obtained_marks column and uploads it back.
    """
    try:
        excel_bytes = generate_template(course_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=marks_template_course_{course_id}.xlsx"
        }
    )