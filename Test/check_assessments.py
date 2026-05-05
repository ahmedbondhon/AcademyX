import sys
sys.path.append("academiq-backend")

from database.connection import SessionLocal
from models.db_models import Assessment, CourseLearningOutcome

db = SessionLocal()

print("All assessments in database:")
assessments = db.query(Assessment).all()
for a in assessments:
    co = db.query(CourseLearningOutcome).filter(CourseLearningOutcome.id == a.mapped_clo_id).first()
    print(f"  ID:{a.id} | Week:{a.week:2d} | {a.type:10s} | "
          f"{a.title:30s} | Max:{a.max_marks:4.0f} | CO:{co.clo_number if co else '?'}")

early = [a for a in assessments if a.week <= 6]
print(f"\nTotal assessments : {len(assessments)}")
print(f"Early (week<=6)   : {len(early)}")
print(f"Late  (week>6)    : {len(assessments) - len(early)}")

db.close()