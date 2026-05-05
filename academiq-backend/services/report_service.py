"""
AcademiQ — PDF Report Generator (UGC/DIU Standard)
Generates Accreditation-ready OBE Reports.
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from sqlalchemy.orm import Session
from services.obe_engine import compute_clo_attainment
from models.db_models import Course, Program, Department, CourseLearningOutcome, Assessment

# ── Colors ────────────────────────────────────
BLUE       = colors.HexColor("#1e40af")
LIGHT_BLUE = colors.HexColor("#dbeafe")
GREEN      = colors.HexColor("#166534")
LIGHT_GREEN= colors.HexColor("#dcfce7")
RED        = colors.HexColor("#dc2626")
LIGHT_RED  = colors.HexColor("#fee2e2")
GRAY       = colors.HexColor("#475569")
LIGHT_GRAY = colors.HexColor("#f1f5f9")
WHITE      = colors.white
BLACK      = colors.black

def generate_obe_report(course_id: int, db: Session) -> bytes:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise ValueError("Course not found")
        
    program = db.query(Program).filter(Program.id == course.program_id).first()
    dept = db.query(Department).filter(Department.id == program.department_id).first() if program else None

    # Fetch Data
    clo_results = compute_clo_attainment(course_id, db)
    clos = db.query(CourseLearningOutcome).filter(CourseLearningOutcome.course_id == course_id).all()
    assessments = db.query(Assessment).filter(Assessment.course_id == course_id).all()

    # Calculate Assessment Split
    ca_marks = sum(a.max_marks for a in assessments if a.type != "final")
    see_marks = sum(a.max_marks for a in assessments if a.type == "final")
    total_marks = ca_marks + see_marks

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], alignment=1, textColor=BLUE, fontSize=16, spaceAfter=14)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], textColor=BLACK, fontSize=12, spaceAfter=8, spaceBefore=12)
    normal_style = styles["Normal"]

    content = []

    # ── Header ────────────────────────────────────
    content.append(Paragraph("<b>UNIVERSITY GRANTS COMMISSION OF BANGLADESH</b>", title_style))
    content.append(Paragraph("Template of Outcome Based Education (OBE) Curriculum", ParagraphStyle("SubTitle", alignment=1, fontSize=12, spaceAfter=10)))
    content.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=15))

    # ── Part A: Basic Info ────────────────────────
    content.append(Paragraph("<b>Part A: General Information</b>", heading_style))
    
    info_data = [
        ["Course Code:", course.code, "Course Title:", course.name],
        ["Semester:", course.semester, "Department:", dept.name if dept else "N/A"],
        ["Program:", program.name if program else "N/A", "Report Date:", datetime.now().strftime("%d %b %Y")]
    ]
    
    info_table = Table(info_data, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), BLACK),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    content.append(info_table)
    content.append(Spacer(1, 0.5*cm))

    # ── Part B: CLOs ─────────────────────────────
    content.append(Paragraph("<b>Part B: Course Learning Outcomes (CLOs)</b>", heading_style))
    
    clo_data = [["CLO", "Description", "Bloom's Level", "Knowledge Profile", "Domain"]]
    for clo in clos:
        clo_data.append([
            clo.clo_number,
            Paragraph(clo.description, normal_style),
            clo.bloom_level or "N/A",
            clo.knowledge_profile or "N/A",
            clo.domain or "Cognitive"
        ])

    clo_table = Table(clo_data, colWidths=[1.5*cm, 8.5*cm, 2.5*cm, 2.5*cm, 2*cm])
    clo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY])
    ]))
    content.append(clo_table)
    content.append(Spacer(1, 0.5*cm))

    # ── Part C: Assessment Strategy ──────────────
    content.append(Paragraph("<b>Part C: Assessment and Evaluation</b>", heading_style))
    
    ca_pct = (ca_marks / total_marks * 100) if total_marks > 0 else 0
    see_pct = (see_marks / total_marks * 100) if total_marks > 0 else 0
    
    assess_data = [
        ["Component", "Marks", "Weightage"],
        ["Continuous Assessment (CA)", f"{ca_marks:.1f}", f"{ca_pct:.1f}%"],
        ["Summative / Semester End Exam (SEE)", f"{see_marks:.1f}", f"{see_pct:.1f}%"],
        ["Total", f"{total_marks:.1f}", "100%"]
    ]
    
    assess_table = Table(assess_data, colWidths=[8*cm, 4*cm, 4*cm])
    assess_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), # Bold Total Row
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    content.append(assess_table)
    content.append(Spacer(1, 0.5*cm))

    # ── Attainment Results ───────────────────────
    content.append(Paragraph("<b>Attainment Summary</b>", heading_style))
    content.append(Paragraph("<i>* Benchmark: 60% of students must achieve ≥ 60% marks in respective CLOs.</i>", ParagraphStyle("Note", fontSize=9, textColor=GRAY, spaceAfter=8)))
    
    result_data = [["CLO", "Total Marks", "Total Students", "Passed (≥60%)", "Attainment %", "Status"]]
    
    result_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN",      (1, 0), (-1, -1), "CENTER"),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING",    (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY])
    ])

    for i, r in enumerate(clo_results, start=1):
        status = "Met" if r["threshold_met"] else "Not Met"
        result_data.append([
            r["clo_number"], 
            f"{r['total_marks']:.1f}", 
            str(r["total_students"]), 
            str(r["passed_students"]), 
            f"{r['attainment_pct']}%", 
            status
        ])
        
        # Color code status column
        if r["threshold_met"]:
            result_style.add("BACKGROUND", (5, i), (5, i), LIGHT_GREEN)
            result_style.add("TEXTCOLOR", (5, i), (5, i), GREEN)
        else:
            result_style.add("BACKGROUND", (5, i), (5, i), LIGHT_RED)
            result_style.add("TEXTCOLOR", (5, i), (5, i), RED)

    res_table = Table(result_data, colWidths=[2.5*cm, 2.5*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    res_table.setStyle(result_style)
    content.append(res_table)

    # ── Footer ───────────────────────────────────
    content.append(Spacer(1, 2*cm))
    content.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY, spaceAfter=5))
    content.append(Paragraph("Generated automatically by AcademiQ OBE Intelligence Platform", ParagraphStyle("Footer", alignment=1, fontSize=8, textColor=GRAY)))

    # Build PDF
    doc.build(content)
    return buffer.getvalue()