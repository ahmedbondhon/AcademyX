"""
AcademiQ — Seed Data based on REAL DIU Course Structure
Source: CSE311 (Theory) and CSE312 (Lab) course outlines — DIU Version 2.0
UGC OBE Template Bangladesh

Run: python seed_data.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import bcrypt
import random
from database.connection import SessionLocal, engine
from models.db_models import (
    Base, User, Department, Program, Course,
    CourseLearningOutcome, Assessment, StudentMark,
    ProgramOutcome, CLOPLOMapping
)

def hash_pw(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("=" * 60)
    print("  AcademiQ — Seeding Real DIU OBE Data")
    print("  Based on CSE311 & CSE312 Course Outlines")
    print("=" * 60)

    # ── 1. Department ─────────────────────────────────────────
    dept = db.query(Department).filter_by(code="CSE").first()
    if not dept:
        dept = Department(
            name="Computer Science & Engineering",
            code="CSE"
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)
    print(f"\n  Dept : {dept.name} ({dept.code})")

    # ── 2. Program ────────────────────────────────────────────
    prog = db.query(Program).filter_by(name="BSc in CSE").first()
    if not prog:
        prog = Program(
            name="BSc in CSE",
            department_id=dept.id
        )
        db.add(prog)
        db.commit()
        db.refresh(prog)
    print(f"  Prog : {prog.name}")

    # ── 3. Program Outcomes (PLOs) — based on UGC/DIU standard ──
    # CSE311 maps to PO1, PO3, PO5 | CSE312 maps to PO3, PO5, PO9, PO10
    po_data = [
        ("PO1",  "Engineering Knowledge — Apply knowledge of mathematics, natural science, engineering fundamentals and specialized CSE knowledge to solve complex engineering problems."),
        ("PO2",  "Problem Analysis — Identify, formulate, research literature and analyze complex engineering problems."),
        ("PO3",  "Design/Development of Solutions — Design solutions for complex engineering problems and system components meeting specified needs."),
        ("PO4",  "Investigation — Conduct investigations of complex problems using research-based knowledge."),
        ("PO5",  "Modern Tool Usage — Create, select, and apply appropriate techniques, resources and modern engineering tools including IT tools."),
        ("PO6",  "The Engineer and Society — Apply reasoning informed by contextual knowledge to assess societal, health, safety and cultural issues."),
        ("PO7",  "Environment and Sustainability — Understand the impact of professional engineering solutions in societal and environmental contexts."),
        ("PO8",  "Ethics — Apply ethical principles and commit to professional ethics and responsibilities."),
        ("PO9",  "Individual and Team Work — Function effectively as an individual, and as a member or leader in diverse teams."),
        ("PO10", "Communication — Communicate effectively on complex engineering activities with the engineering community and society at large."),
        ("PO11", "Project Management — Demonstrate knowledge and understanding of engineering and management principles."),
        ("PO12", "Life-long Learning — Recognize the need for and ability to engage in independent and life-long learning."),
    ]
    pos = {}
    for po_num, desc in po_data:
        po = db.query(ProgramOutcome).filter_by(
            program_id=prog.id, po_number=po_num
        ).first()
        if not po:
            po = ProgramOutcome(
                program_id=prog.id,
                po_number=po_num,
                description=desc
            )
            db.add(po)
        pos[po_num] = po
    db.commit()
    for k in pos: db.refresh(pos[k])
    print(f"  PLOs : {len(pos)} Program Outcomes created (PO1–PO12)")

    # ── 4. Courses ────────────────────────────────────────────
    # CSE311: Theory — 3 credits, 14 weeks, 100 marks
    # CSE312: Lab    — 1.5 credits, 14 weeks, 100 marks
    courses_info = [
        ("CSE311", "Database Management System",     3.0, "Summer 2025", "CSE134, CSE221"),
        ("CSE312", "Database Management System Lab", 1.5, "Summer 2025", "CSE134"),
    ]
    courses = {}
    for code, name, credits, sem, prereq in courses_info:
        c = db.query(Course).filter_by(code=code).first()
        if not c:
            c = Course(
                code=code, name=name,
                semester=sem,
                program_id=prog.id,
                faculty_id=None
            )
            db.add(c)
        courses[code] = c
    db.commit()
    for k in courses: db.refresh(courses[k])
    print(f"  Courses: CSE311 (Theory 3cr) + CSE312 (Lab 1.5cr)")

    # ── 5. CLOs / Course Outcomes ─────────────────────────────
    # CSE311 CLOs — from real course outline (3 COs)
    cse311_clos = [
        ("CO1", "Relate and apply fundamental database concepts including relational data models, normalization, and basic SQL to design and manage structured data systems.", "Apply",    "PO1"),
        ("CO2", "Implement and optimize relational databases, incorporating advanced SQL queries, indexing techniques and query optimization strategies.",                   "Evaluate",  "PO3"),
        ("CO3", "Apply and Analyze security techniques, distributed database architectures, and emerging tools and technologies in database management using appropriate modern database tools while addressing real-world challenges.", "Analyze", "PO5"),
    ]
    # CSE312 CLOs — from real lab course outline (4 COs)
    cse312_clos = [
        ("CO1", "Implement and optimize relational databases using basic to advanced SQL queries, indexing techniques, and query optimization strategies.",                                                                                  "Apply",   "PO3"),
        ("CO2", "Analyze and apply security techniques, distributed database architectures, and emerging tools in database management to address real-world challenges.",                                                                    "Analyze", "PO5"),
        ("CO3", "Perform effectively as an individual or a member or a leader of diverse teams through proper documentation and initialization of project work.",                                                                            "Apply",   "PO9"),
        ("CO4", "Create a project by explaining complex computer engineering activities with the computer engineering community by performing effective communication through demonstration and presentation.",                               "Create",  "PO10"),
    ]

    cos = {"CSE311": {}, "CSE312": {}}
    for co_num, desc, bloom, po_num in cse311_clos:
        co = db.query(CourseLearningOutcome).filter_by(
            course_id=courses["CSE311"].id, clo_number=co_num
        ).first()
        if not co:
            co = CourseLearningOutcome(
                course_id=courses["CSE311"].id,
                clo_number=co_num, description=desc, bloom_level=bloom
            )
            db.add(co)
        cos["CSE311"][co_num] = (co, po_num)

    for co_num, desc, bloom, po_num in cse312_clos:
        co = db.query(CourseLearningOutcome).filter_by(
            course_id=courses["CSE312"].id, clo_number=co_num
        ).first()
        if not co:
            co = CourseLearningOutcome(
                course_id=courses["CSE312"].id,
                clo_number=co_num, description=desc, bloom_level=bloom
            )
            db.add(co)
        cos["CSE312"][co_num] = (co, po_num)
    db.commit()
    for k in cos:
        for v in cos[k].values(): db.refresh(v[0])
    print(f"  CLOs : CSE311→3 CLOs | CSE312→4 CLOs")

    # ── 6. CO-PO Mappings ─────────────────────────────────────
    for course_key, co_dict in cos.items():
        for co_num, (co, po_num) in co_dict.items():
            po = pos[po_num]
            exists = db.query(CLOPLOMapping).filter_by(
                clo_id=co.id, po_id=po.id
            ).first()
            if not exists:
                db.add(CLOPLOMapping(clo_id=co.id, po_id=po.id, correlation=1.0))
    db.commit()
    print(f"  CO-PO Mappings created")

    # ── 7. Assessments ────────────────────────────────────────
    # CSE311 Assessment Pattern (Total=100):
    # Attendance 7 | Quiz 15 | Presentation 8 | Assignment 5 | Mid 25 | Final 40
    # CLO-wise Mid: CO1=17, CO2=8  | Final: CO1=10, CO2=20, CO3=10
    cse311_assessments = [
        # (title, type, max_marks, clo_number, week)
        ("Attendance",              "attendance",   7,  "CO1", 14),
        ("Quiz 1 — SQL Basics",     "quiz",         5,  "CO1",  3),
        ("Quiz 2 — ER Modeling",    "quiz",         5,  "CO1",  5),
        ("Quiz 3 — Joins & Subq",   "quiz",         5,  "CO2",  7),
        ("Presentation",            "presentation", 8,  "CO2",  9),
        ("Assignment — Norm",       "assignment",   5,  "CO1",  6),
        ("Mid-Term Exam",           "midterm",      25, "CO1", 8),
        ("Final Exam",              "final",        40, "CO3", 14),
    ]
    # CSE312 Assessment Pattern (Total=100):
    # Attendance 10 | Lab Performance 25 | Lab Report 25 | Lab Project 40
    # CO-wise Project: CO1=10, CO2=20, CO3=10
    cse312_assessments = [
        ("Attendance",                      "attendance",     10, "CO1", 14),
        ("Lab Performance — SQL Basics",    "lab_perf",        5, "CO1",  3),
        ("Lab Performance — CRUD Ops",      "lab_perf",        5, "CO1",  6),
        ("Lab Performance — Joins",         "lab_perf",        5, "CO2",  7),
        ("Lab Performance — Security",      "lab_perf",        5, "CO2",  8),
        ("Lab Performance — NoSQL",         "lab_perf",        5, "CO2",  9),
        ("Lab Report 1",                    "lab_report",     12, "CO1",  8),
        ("Lab Report 2",                    "lab_report",     13, "CO2", 10),
        ("Lab Project — Implementation",    "lab_project",    10, "CO1", 12),
        ("Lab Project — Security & Dist",   "lab_project",    20, "CO2", 13),
        ("Lab Project — Team & Docs",       "lab_project",    10, "CO3", 14),
    ]

    assessments = {"CSE311": {}, "CSE312": {}}
    for title, atype, max_m, co_num, week in cse311_assessments:
        co_obj = cos["CSE311"][co_num][0]
        a = db.query(Assessment).filter_by(
            course_id=courses["CSE311"].id, title=title
        ).first()
        if not a:
            a = Assessment(
                course_id=courses["CSE311"].id,
                title=title, type=atype,
                max_marks=max_m, mapped_clo_id=co_obj.id, week=week
            )
            db.add(a)
        assessments["CSE311"][title] = a

    for title, atype, max_m, co_num, week in cse312_assessments:
        co_obj = cos["CSE312"][co_num][0]
        a = db.query(Assessment).filter_by(
            course_id=courses["CSE312"].id, title=title
        ).first()
        if not a:
            a = Assessment(
                course_id=courses["CSE312"].id,
                title=title, type=atype,
                max_marks=max_m, mapped_clo_id=co_obj.id, week=week
            )
            db.add(a)
        assessments["CSE312"][title] = a
    db.commit()
    for k in assessments:
        for v in assessments[k].values():
            if v.id: db.refresh(v)
    cse311_count = len(assessments["CSE311"])
    cse312_count = len(assessments["CSE312"])
    print(f"  Assessments: CSE311→{cse311_count} | CSE312→{cse312_count}")

    # ── 8. Faculty & Dean ─────────────────────────────────────
    staff = [
        ("Mohammad Jahangir Alam", "jahangir@diu.edu.bd", "faculty"),
        ("Dr. Shafiqul Islam",     "shafiq@diu.edu.bd",   "faculty"),
        ("Prof. Touhid Bhuiyan",   "touhid@diu.edu.bd",   "dean"),
    ]
    staff_users = []
    for name, email, role in staff:
        u = db.query(User).filter_by(email=email).first()
        if not u:
            u = User(
                name=name, email=email,
                hashed_password=hash_pw("diu2025"),
                role=role, is_active=True
            )
            db.add(u)
        staff_users.append(u)
    db.commit()
    for u in staff_users: db.refresh(u)

    # Assign faculty to courses
    courses["CSE311"].faculty_id = staff_users[0].id
    courses["CSE312"].faculty_id = staff_users[0].id
    db.commit()
    print(f"  Faculty: {staff_users[0].name} assigned to both courses")

    # ── 9. Students — 30 students, realistic DIU profile ─────
    # Three performance groups based on real grade distributions
    student_profiles = [
        # Strong students (A/A+) — 8 students
        ("Arafat Hossain",      "arafat@s.diu.edu.bd",   "strong"),
        ("Nusrat Jahan",        "nusrat@s.diu.edu.bd",   "strong"),
        ("Mahmudul Hasan",      "mahmudul@s.diu.edu.bd", "strong"),
        ("Fatema Akter",        "fatema@s.diu.edu.bd",   "strong"),
        ("Tanvir Ahmed",        "tanvir@s.diu.edu.bd",   "strong"),
        ("Sadia Islam",         "sadia@s.diu.edu.bd",    "strong"),
        ("Rakibul Islam",       "rakib@s.diu.edu.bd",    "strong"),
        ("Moriom Begum",        "moriom@s.diu.edu.bd",   "strong"),
        # Average students (B/B+) — 12 students
        ("Imran Khan",          "imran@s.diu.edu.bd",    "average"),
        ("Sharmin Akter",       "sharmin@s.diu.edu.bd",  "average"),
        ("Nazmul Huda",         "nazmul@s.diu.edu.bd",   "average"),
        ("Puja Rani",           "puja@s.diu.edu.bd",     "average"),
        ("Sabbir Rahman",       "sabbir@s.diu.edu.bd",   "average"),
        ("Tania Sultana",       "tania@s.diu.edu.bd",    "average"),
        ("Arif Billah",         "arif@s.diu.edu.bd",     "average"),
        ("Roksana Parvin",      "roksana@s.diu.edu.bd",  "average"),
        ("Jakir Hossain",       "jakir@s.diu.edu.bd",    "average"),
        ("Masum Billah",        "masum@s.diu.edu.bd",    "average"),
        ("Sumaiya Akter",       "sumaiya@s.diu.edu.bd",  "average"),
        ("Rafiqul Islam",       "rafiq@s.diu.edu.bd",    "average"),
        # Weak students (C/D/F risk) — 10 students
        ("Milon Chandra",       "milon@s.diu.edu.bd",    "weak"),
        ("Ritu Akter",          "ritu@s.diu.edu.bd",     "weak"),
        ("Sagor Mia",           "sagor@s.diu.edu.bd",    "weak"),
        ("Lipi Begum",          "lipi@s.diu.edu.bd",     "weak"),
        ("Sujon Ahmed",         "sujon@s.diu.edu.bd",    "weak"),
        ("Mithun Das",          "mithun@s.diu.edu.bd",   "weak"),
        ("Pinky Akter",         "pinky@s.diu.edu.bd",    "weak"),
        ("Karim Uddin",         "karim@s.diu.edu.bd",    "weak"),
        ("Nasrin Akter",        "nasrin@s.diu.edu.bd",   "weak"),
        ("Belal Hossain",       "belal@s.diu.edu.bd",    "weak"),
    ]

    # Score ranges — calibrated to DIU grading scale
    # A+ = 80-100 | A = 75-79 | A- = 70-74 | B+ = 65-69 | B = 60-64 | C = 50-59 | F < 50
    score_ranges = {
        "strong":  (0.78, 0.97),   # A to A+
        "average": (0.58, 0.76),   # B- to B+
        "weak":    (0.25, 0.55),   # D to C
    }

    students = []
    for name, email, stype in student_profiles:
        u = db.query(User).filter_by(email=email).first()
        if not u:
            u = User(
                name=name, email=email,
                hashed_password=hash_pw("student123"),
                role="student", is_active=True
            )
            db.add(u)
        students.append((u, stype))
    db.commit()
    for u, _ in students: db.refresh(u)
    print(f"  Students: {len(students)} created (8 strong | 12 average | 10 weak)")

    # ── 10. Generate Marks ────────────────────────────────────
    random.seed(2025)
    marks_created = 0

    for student, stype in students:
        lo, hi = score_ranges[stype]
        for course_key in ["CSE311", "CSE312"]:
            for title, assessment in assessments[course_key].items():
                # Check if mark already exists
                existing = db.query(StudentMark).filter_by(
                    student_id=student.id,
                    assessment_id=assessment.id
                ).first()
                if existing:
                    continue

                # Attendance: strong=near full, weak=lower
                if assessment.type == "attendance":
                    if stype == "strong":
                        pct = random.uniform(0.85, 1.0)
                    elif stype == "average":
                        pct = random.uniform(0.70, 0.88)
                    else:
                        pct = random.uniform(0.45, 0.72)
                else:
                    pct = random.uniform(lo, hi)
                    # Add some variation per CO
                    # Weak students struggle more with higher-order COs
                    co = db.query(CourseLearningOutcome).filter_by(
                        id=assessment.mapped_clo_id
                    ).first()
                    if co and stype == "weak":
                        if co.bloom_level in ["Analyze", "Evaluate", "Create"]:
                            pct *= 0.85  # Extra penalty for higher bloom levels

                obtained = round(assessment.max_marks * min(pct, 1.0), 1)
                db.add(StudentMark(
                    student_id=student.id,
                    assessment_id=assessment.id,
                    obtained=obtained
                ))
                marks_created += 1

    db.commit()
    db.close()
    print(f"  Marks : {marks_created} records created")
    print("\n" + "=" * 60)
    print("  Database seeded successfully!")
    print("=" * 60)
    print("\n  Login Credentials:")
    print("  ─────────────────────────────────────────────")
    print("  Role     | Email                    | Pass")
    print("  ─────────────────────────────────────────────")
    print("  Dean     | touhid@diu.edu.bd        | diu2025")
    print("  Faculty  | jahangir@diu.edu.bd      | diu2025")
    print("  Student  | arafat@s.diu.edu.bd      | student123  (strong)")
    print("  Student  | imran@s.diu.edu.bd       | student123  (average)")
    print("  Student  | milon@s.diu.edu.bd       | student123  (weak/at-risk)")
    print("  ─────────────────────────────────────────────")
    print("\n  Courses seeded:")
    print("  CSE311 — Database Management System (Theory, 3cr)")
    print("    CLOs: CO1→PO1 | CO2→PO3 | CO3→PO5")
    print("    Assessment: Attendance 7 | Quiz 15 | Pres 8 | Assign 5 | Mid 25 | Final 40")
    print("  CSE312 — Database Management System Lab (1.5cr)")
    print("    CLOs: CO1→PO3 | CO2→PO5 | CO3→PO9 | CO4→PO10")
    print("    Assessment: Attendance 10 | Lab Perf 25 | Lab Report 25 | Project 40")

if __name__ == "__main__":
    seed()
