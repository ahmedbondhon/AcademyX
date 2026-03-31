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
from services.obe_engine import (
    compute_co_attainment,
    compute_po_attainment,
    get_course_summary
)
from models.db_models import Course, Program, Department
from database.crud import get_students

# ── Colors ────────────────────────────────────
BLUE       = colors.HexColor("#1e40af")
LIGHT_BLUE = colors.HexColor("#dbeafe")
GREEN      = colors.HexColor("#166534")
LIGHT_GREEN= colors.HexColor("#dcfce7")
RED        = colors.HexColor("#dc2626")
LIGHT_RED  = colors.HexColor("#fee2e2")
AMBER      = colors.HexColor("#d97706")
LIGHT_AMBER= colors.HexColor("#fef3c7")
GRAY       = colors.HexColor("#475569")
LIGHT_GRAY = colors.HexColor("#f1f5f9")
WHITE      = colors.white
BLACK      = colors.black


def generate_obe_report(course_id: int, db: Session) -> bytes:
    """
    Generate a full OBE attainment PDF report for a course.
    Returns PDF as bytes.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise ValueError("Course not found")

    program    = db.query(Program).filter(
        Program.id == course.program_id
    ).first()
    department = db.query(Department).filter(
        Department.id == program.department_id
    ).first() if program else None

    co_results  = compute_co_attainment(course_id, db)
    po_results  = compute_po_attainment(
        program.id if program else 1, db
    )
    summary     = get_course_summary(course_id, db)
    students    = get_students(db)

    # ── Setup document ────────────────────────
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles  = getSampleStyleSheet()
    content = []

    # ── Header styles ─────────────────────────
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=18,
        textColor=BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=GRAY,
        spaceAfter=2,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=13,
        textColor=BLUE,
        fontName="Helvetica-Bold",
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BLACK,
        spaceAfter=4,
    )

    # ── Page 1: Header ────────────────────────
    content.append(Paragraph("Daffodil International University", subtitle_style))
    content.append(Paragraph(
        f"{department.name if department else 'Department'}", subtitle_style
    ))
    content.append(Spacer(1, 0.3*cm))
    content.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    content.append(Spacer(1, 0.3*cm))

    content.append(Paragraph(
        "OBE Attainment Report", title_style
    ))
    content.append(Paragraph(
        f"{course.code} — {course.name}", subtitle_style
    ))
    content.append(Paragraph(
        f"Semester: {course.semester} &nbsp;&nbsp; "
        f"Generated: {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    content.append(Spacer(1, 0.5*cm))

    # ── Course Summary Box ────────────────────
    health_color = (
        LIGHT_GREEN if summary["health"] == "Good"    else
        LIGHT_AMBER if summary["health"] == "Warning" else
        LIGHT_RED
    )
    summary_data = [
        ["Course Code",   course.code,
         "Total Students", str(summary["student_count"])],
        ["Program",       program.name if program else "—",
         "COs Met",       f"{summary['cos_met']} / {summary['total_cos']}"],
        ["Semester",      course.semester,
         "Avg Attainment", f"{summary['avg_attainment']}%"],
        ["Health Status", summary["health"], "", ""],
    ]
    summary_table = Table(summary_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 4.5*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BACKGROUND", (0, 3), (1, 3),   health_color),
        ("TEXTCOLOR",  (0, 0), (0, -1),  BLUE),
        ("TEXTCOLOR",  (2, 0), (2, -1),  BLUE),
        ("FONTNAME",   (0, 0), (0, -1),  "Helvetica-Bold"),
        ("FONTNAME",   (2, 0), (2, -1),  "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("PADDING",    (0, 0), (-1, -1), 6),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("SPAN",       (1, 3), (-1, 3)),
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 0.5*cm))

    # ── CO Attainment Table ───────────────────
    content.append(Paragraph("Course Outcome (CO) Attainment", section_style))

    co_header = ["CO", "Description", "Bloom Level",
                 "Attainment %", "Level", "Status"]
    co_rows   = [co_header]
    for r in co_results:
        status = "MET" if r["threshold_met"] else "NOT MET"
        co_rows.append([
            r["co"],
            Paragraph(r["description"][:60], body_style),
            r["bloom_level"],
            f"{r['attainment_pct']:.1f}%",
            f"L{r['level']} — {r['level_label']}",
            status,
        ])

    co_table = Table(
        co_rows,
        colWidths=[1.2*cm, 6*cm, 2.2*cm, 2.2*cm, 3*cm, 2.4*cm]
    )
    co_style = TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0),  BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",   (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("PADDING",    (0, 0), (-1, -1), 5),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("ALIGN",      (3, 0), (3, -1),  "CENTER"),
        ("ALIGN",      (5, 0), (5, -1),  "CENTER"),
    ])
    # Color status column
    for i, r in enumerate(co_results, start=1):
        if r["threshold_met"]:
            co_style.add("BACKGROUND", (5, i), (5, i), LIGHT_GREEN)
            co_style.add("TEXTCOLOR",  (5, i), (5, i), GREEN)
        else:
            co_style.add("BACKGROUND", (5, i), (5, i), LIGHT_RED)
            co_style.add("TEXTCOLOR",  (5, i), (5, i), RED)

    co_table.setStyle(co_style)
    content.append(co_table)
    content.append(Spacer(1, 0.5*cm))

    # ── PO Attainment Table ───────────────────
    content.append(Paragraph("Program Outcome (PO) Attainment", section_style))

    po_header = ["PO", "Description", "Attainment %", "Level", "Status"]
    po_rows   = [po_header]
    for r in po_results:
        status = "MET" if r["threshold_met"] else "NOT MET"
        po_rows.append([
            r["po"],
            Paragraph(r["description"][:70], body_style),
            f"{r['attainment_pct']:.1f}%",
            f"L{r['level']} — {r['level_label']}",
            status,
        ])

    po_table = Table(
        po_rows,
        colWidths=[1.2*cm, 7.5*cm, 2.2*cm, 3*cm, 2.4*cm]
    )
    po_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),  BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",   (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("PADDING",    (0, 0), (-1, -1), 5),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("ALIGN",      (2, 0), (2, -1),  "CENTER"),
        ("ALIGN",      (4, 0), (4, -1),  "CENTER"),
    ])
    for i, r in enumerate(po_results, start=1):
        if r["threshold_met"]:
            po_style.add("BACKGROUND", (4, i), (4, i), LIGHT_GREEN)
            po_style.add("TEXTCOLOR",  (4, i), (4, i), GREEN)
        else:
            po_style.add("BACKGROUND", (4, i), (4, i), LIGHT_RED)
            po_style.add("TEXTCOLOR",  (4, i), (4, i), RED)

    po_table.setStyle(po_style)
    content.append(po_table)
    content.append(Spacer(1, 0.5*cm))

    # ── Footer note ───────────────────────────
    content.append(HRFlowable(width="100%", thickness=1, color=GRAY))
    content.append(Spacer(1, 0.2*cm))
    content.append(Paragraph(
        f"This report was automatically generated by AcademiQ v1.0 on "
        f"{datetime.now().strftime('%B %d, %Y at %I:%M %p')}. "
        f"Attainment threshold: 60%. "
        f"Level 3 ≥ 70% | Level 2 ≥ 50% | Level 1 < 50%.",
        ParagraphStyle("Footer", parent=styles["Normal"],
                       fontSize=7, textColor=GRAY)
    ))

    doc.build(content)
    buffer.seek(0)
    return buffer.read()