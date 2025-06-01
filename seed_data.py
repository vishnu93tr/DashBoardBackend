import random
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from app.models import Project, Execution, TestCase
from app.database import Base

# Configure PostgreSQL DB URL
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Using DB: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
fake = Faker()

# Step 1: Drop and recreate tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Dropped and recreated all tables.")

# Step 2: Seed 3 Projects
projects = []
for _ in range(3):
    project = Project(name=fake.unique.company())
    session.add(project)
    projects.append(project)
session.commit()
print("✅ Inserted 3 projects.")

# Step 3: Seed Executions and TestCases for last 100 days
statuses = ["passed", "failed", "skipped"]
weights = [0.7, 0.2, 0.1]  # 70% pass, 20% fail, 10% skipped
start_date = datetime.now() - timedelta(days=100)

for day_offset in range(100):
    print(day_offset)
    current_date = start_date + timedelta(days=day_offset)
    print(f"📅 Seeding data for {current_date.date()}")

    for project in projects:
        for _ in range(random.randint(1, 3)):  # 1–3 executions/day/project
            execution = Execution(
                project_id=project.id,
                executed_at=current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                triggered_by=fake.first_name()
            )
            session.add(execution)
            session.flush()  # Required to use execution.id

            for i in range(random.randint(10, 30)):  # 10–30 test cases
                status = random.choices(statuses, weights=weights, k=1)[0]
                test_case = TestCase(
                    execution_id=execution.id,
                    name=f"TestCase_{i+1}",
                    status=status,
                    duration_seconds=round(random.uniform(0.5, 10.0), 2),
                    error_message=fake.sentence() if status == "failed" else None
                )
                session.add(test_case)

session.commit()
session.close()
print("✅ Database seeded successfully with 3 projects over 100 days.")
