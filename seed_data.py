import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Project, Execution, TestCase

# Recreate tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

# Dummy project names
projects = ["Project Alpha", "Project Beta"]

# Create projects
project_objs = []
for name in projects:
    project = Project(name=name)
    db.add(project)
    project_objs.append(project)

db.commit()

# Status pool
statuses = ["PASSED", "FAILED", "SKIPPED"]
status_weights = [0.7, 0.25, 0.05]

# Create executions and test cases over last 100 days
for project in project_objs:
    for i in range(100):  # 100 days
        execution_time = datetime.now() - timedelta(days=99 - i)
        execution = Execution(
            project_id=project.id,
            executed_at=execution_time,
            triggered_by="CI"
        )
        db.add(execution)
        db.flush()  # Get execution.id

        # 5 test cases per execution
        for j in range(5):
            status = random.choices(statuses, weights=status_weights)[0]
            tc = TestCase(
                execution_id=execution.id,
                name=f"{project.name}_TC_{i}_{j}",
                status=status,
                duration_seconds=round(random.uniform(1.0, 15.0), 2),
                error_message=None if status == "PASSED" else f"{status} on step {random.randint(1, 3)}"
            )
            db.add(tc)

db.commit()
db.close()

print("✅ Dummy test execution data seeded for 100 days.")
