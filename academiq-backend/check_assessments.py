from database.connection import SessionLocal
from models.db_models import Assessment, CourseOutcome

db = SessionLocal()
assessments = db.query(Assessment).all()

print("All assessments:")
for a in assessments:
    co = db.query(CourseOutcome).filter(
        CourseOutcome.id == a.mapped_co_id
    ).first()
    co_num = co.co_number if co else "?"
    print(f"  ID:{a.id}  Week:{a.week}  {a.type}  {a.title}  CO:{co_num}")

early = [a for a in assessments if a.week <= 6]
print(f"\nTotal        : {len(assessments)}")
print(f"Early week<=6: {len(early)}")
print(f"Late  week>6 : {len(assessments) - len(early)}")

db.close()