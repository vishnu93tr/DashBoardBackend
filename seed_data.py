import random ,os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from app.models import Project, Execution, TestCase
from app.database import Base

# Configure PostgreSQL DB URL here
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
fake = Faker()

# Step 1: Drop all and recreate tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Step 2: Seed Projects
projects = []
for i in range(10):
    project = Project(name=fake.unique.company())
    session.add(project)
    projects.append(project)
session.commit()

# Step 3: Seed Executions and TestCases (100 days back, multiple executions/day)
statuses = ["passed", "failed", "skipped"]
start_date = datetime.now() - timedelta(days=100)

for day in range(100):
    print('started for loop')
    for _ in range(random.randint(1, 3)):  # 1-3 executions per day
        print(day)
        for project in random.sample(projects, k=random.randint(1, len(projects))):
            execution = Execution(
                project_id=project.id,
                executed_at=start_date + timedelta(days=day, hours=random.randint(0, 23)),
                triggered_by=fake.first_name()
            )
            session.add(execution)
            session.flush()  # Get execution.id before adding test cases

            for i in range(random.randint(5, 20)):  # 5-20 test cases per execution
                status = random.choices(statuses, weights=[0.7, 0.2, 0.1])[0]
                test_case = TestCase(
                    execution_id=execution.id,
                    name=f"TestCase_{i+1}",
                    status=status,
                    duration_seconds=round(random.uniform(0.5, 5.0), 2),
                    error_message=fake.sentence() if status == "failed" else None
                )
                session.add(test_case)

session.commit()
session.close()

print("✅ Database seeded with sample data.")
