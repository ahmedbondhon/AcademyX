"""
Run this once to populate the database with demo data.
Command: python seed_data.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import SessionLocal, engine
from models.db_models import (
    Base, User, Department, Program, Course,
    CourseOutcome, Assessment, StudentMark,
    ProgramOutcome, COPOMapping
)
import bcrypt
import random

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Seeding database...")

    # ── 1. Department ─────────────────────────
    dept = Department(name="Computer Science & Engineering", code="CSE")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    print(f"  ✓ Department: {dept.name}")

    # ── 2. Program ────────────────────────────
    program = Program(name="BSc in CSE", department_id=dept.id)
    db.add(program)
    db.commit()
    db.refresh(program)
    print(f"  ✓ Program: {program.name}")

    # ── 3. Program Outcomes ───────────────────
    pos = [
        ProgramOutcome(program_id=program.id, po_number="PO1",
            description="Apply knowledge of computing to solve real-world problems"),
        ProgramOutcome(program_id=program.id, po_number="PO2",
            description="Design and implement software systems effectively"),
        ProgramOutcome(program_id=program.id, po_number="PO3",
            description="Analyze and evaluate computing systems for quality"),
    ]
    for po in pos:
        db.add(po)
    db.commit()
    print(f"  ✓ Program Outcomes: {len(pos)} created")

    # ── 4. Faculty user ───────────────────────
    faculty = User(
        name="Dr. Rahman",
        email="faculty@diu.edu.bd",
        hashed_password=hash_pw("test1234"),
        role="faculty"
    )
    db.add(faculty)

    dean = User(
        name="Dean Abdullah",
        email="dean@diu.edu.bd",
        hashed_password=hash_pw("test1234"),
        role="dean"
    )
    db.add(dean)
    db.commit()
    db.refresh(faculty)
    print(f"  ✓ Faculty: {faculty.name}")
    print(f"  ✓ Dean: {dean.name}")

    # ── 5. Course ─────────────────────────────
    course = Course(
        code="CSE301",
        name="Data Structures & Algorithms",
        semester="Spring 2026",
        program_id=program.id,
        faculty_id=faculty.id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    print(f"  ✓ Course: {course.name}")

    # ── 6. Course Outcomes ────────────────────
    co_data = [
        ("CO1", "Understand and implement fundamental data structures", "Remember"),
        ("CO2", "Analyze algorithm complexity using Big-O notation",    "Analyze"),
        ("CO3", "Design efficient algorithms for real-world problems",  "Create"),
        ("CO4", "Evaluate trade-offs between different data structures","Evaluate"),
    ]
    cos = []
    for co_num, desc, bloom in co_data:
        co = CourseOutcome(
            course_id=course.id,
            co_number=co_num,
            description=desc,
            bloom_level=bloom
        )
        db.add(co)
        cos.append(co)
    db.commit()
    for co in cos:
        db.refresh(co)
    print(f"  ✓ Course Outcomes: {len(cos)} created")

    # ── 7. CO-PO Mappings ─────────────────────
    mappings = [
        (cos[0].id, pos[0].id, 1.0),
        (cos[1].id, pos[2].id, 1.0),
        (cos[2].id, pos[1].id, 1.0),
        (cos[3].id, pos[2].id, 0.5),
    ]
    for co_id, po_id, weight in mappings:
        db.add(COPOMapping(co_id=co_id, po_id=po_id, weight=weight))
    db.commit()
    print(f"  ✓ CO-PO Mappings: {len(mappings)} created")

    # ── 8. Assessments ────────────────────────
    assessment_data = [
        ("Quiz 1 - Arrays",          "quiz",       10, cos[0].id, 3),
        ("Quiz 2 - Linked Lists",     "quiz",       10, cos[0].id, 5),
        ("Assignment 1 - Big-O",      "assignment", 20, cos[1].id, 4),
        ("Midterm Exam",              "midterm",    30, cos[1].id, 8),
        ("Assignment 2 - Sorting",    "assignment", 20, cos[2].id, 9),
        ("Quiz 3 - Trees",            "quiz",       10, cos[2].id, 11),
        ("Final Exam",                "final",      40, cos[3].id, 16),
    ]
    assessments = []
    for title, atype, max_m, co_id, week in assessment_data:
        a = Assessment(
            course_id=course.id,
            title=title,
            type=atype,
            max_marks=max_m,
            mapped_co_id=co_id,
            week=week
        )
        db.add(a)
        assessments.append(a)
    db.commit()
    for a in assessments:
        db.refresh(a)
    print(f"  ✓ Assessments: {len(assessments)} created")

    # ── 9. Students + Marks ───────────────────
    students_data = [
        ("Alice Ahmed",    "alice@diu.edu.bd",   "strong"),
        ("Bob Hassan",     "bob@diu.edu.bd",     "average"),
        ("Carol Islam",    "carol@diu.edu.bd",   "strong"),
        ("David Khan",     "david@diu.edu.bd",   "weak"),
        ("Eva Rahman",     "eva@diu.edu.bd",     "average"),
        ("Farhan Uddin",   "farhan@diu.edu.bd",  "weak"),
        ("Gita Begum",     "gita@diu.edu.bd",    "strong"),
        ("Hasan Ali",      "hasan@diu.edu.bd",   "average"),
        ("Irfan Molla",    "irfan@diu.edu.bd",   "weak"),
        ("Joya Sultana",   "joya@diu.edu.bd",    "strong"),
    ]

    # Score ranges per student type
    score_range = {
        "strong":  (0.78, 0.98),
        "average": (0.55, 0.75),
        "weak":    (0.25, 0.52),
    }

    students = []
    for name, email, stype in students_data:
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            students.append((existing, stype))
            continue
        s = User(
            name=name,
            email=email,
            hashed_password=hash_pw("test1234"),
            role="student"
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        students.append((s, stype))

    print(f"  ✓ Students: {len(students)} created")

    # Generate marks for each student
    random.seed(42)  # fixed seed = reproducible demo data
    marks_created = 0
    for student, stype in students:
        lo, hi = score_range[stype]
        for assessment in assessments:
            pct = random.uniform(lo, hi)
            obtained = round(assessment.max_marks * pct, 1)
            mark = StudentMark(
                student_id=student.id,
                assessment_id=assessment.id,
                obtained=obtained
            )
            db.add(mark)
            marks_created += 1
    db.commit()
    print(f"  ✓ Marks: {marks_created} records created")

    db.close()
    print("\n Database seeded successfully!")
    print("\n Login credentials:")
    print("  Faculty  → faculty@diu.edu.bd  / test1234")
    print("  Dean     → dean@diu.edu.bd     / test1234")
    print("  Student  → alice@diu.edu.bd    / test1234")
    print("  At-risk  → david@diu.edu.bd    / test1234")

if __name__ == "__main__":
    seed()