from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case, and_
from ..models import Project, Execution, TestCase


def get_executions_per_project(db: Session, project_name: str, from_date: date, to_date: date):
    stmt = (
        select(
            func.date(Execution.executed_at).label("date"),
            func.count(Execution.id).label("execution_count")
        )
        .join(Project, Execution.project_id == Project.id)
        .where(
            Project.name == project_name,
            Execution.executed_at.between(from_date, to_date)
        )
        .group_by(func.date(Execution.executed_at))
        .order_by(func.date(Execution.executed_at))
    )

    results = db.execute(stmt).all()

    return [
        {
            "date": str(row.date),
            "execution_count": row.execution_count
        }
        for row in results
    ]


def get_pass_fail_trend(db: Session, project_name: str, from_date: date, to_date: date):
    passed_case = case((func.lower(TestCase.status) == 'passed', 1), else_=0)
    failed_case = case((func.lower(TestCase.status) == 'failed', 1), else_=0)

    stmt = (
        select(
            func.date(Execution.executed_at).label("date"),
            func.sum(passed_case).label("passed"),
            func.sum(failed_case).label("failed")
        )
        .select_from(Execution)
        .join(TestCase, TestCase.execution_id == Execution.id)
        .join(Project, Execution.project_id == Project.id)
        .where(and_(
            Project.name == project_name,
            Execution.executed_at.between(from_date, to_date)
        ))
        .group_by(func.date(Execution.executed_at))
        .order_by(func.date(Execution.executed_at))
    )

    rows = db.execute(stmt).all()
    result = []

    for row in rows:
        mapped = row._mapping
        passed = mapped["passed"] or 0
        failed = mapped["failed"] or 0
        total = passed + failed
        pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0

        result.append({
            "date": str(mapped["date"]),
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate
        })

    return result

def get_average_execution_durations_trend(db: Session, project_name: str, from_date: date, to_date: date):
    stmt = (
        select(
            func.date(Execution.executed_at).label("date"),
            func.avg(TestCase.duration_seconds).label("avg_duration_seconds")
        )
        .join(Project, Execution.project_id == Project.id)
        .join(TestCase, TestCase.execution_id == Execution.id)
        .where(Project.name == project_name)
        .where(Execution.executed_at.between(from_date, to_date))
        .group_by(func.date(Execution.executed_at))
        .order_by(func.date(Execution.executed_at))
    )
    results = db.execute(stmt).all()
    return [
        {
            "date": str(row.date),
            "avg_duration_seconds": round(row.avg_duration_seconds or 0.0, 2)
        }
        for row in results
    ]


def get_test_cases_for_project(
    db: Session,
    project_name: str,
    from_date: date,
    to_date: date
):
    # Get latest execution ID for given project within the date range
    latest_execution_id = db.execute(
        select(Execution.id)
        .join(Project)
        .where(
            Project.name == project_name,
            Execution.project_id == Project.id,
            Execution.executed_at.between(from_date, to_date)
        )
        .order_by(Execution.executed_at.desc())
        .limit(1)
    ).scalar()

    if not latest_execution_id:
        return []

    # Fetch test cases for that latest execution
    test_cases = db.execute(
        select(TestCase.name, TestCase.duration_seconds, TestCase.status)
        .where(TestCase.execution_id == latest_execution_id)
        .order_by(TestCase.duration_seconds.desc())
    ).all()

    return [
        {
            "name": tc[0],
            "duration_seconds": tc[1],
            "status": tc[2],
            "execution_id": latest_execution_id
        } for tc in test_cases
    ]

def get_all_projects(db: Session):
    stmt = select(Project.name).order_by(Project.name)
    return db.execute(stmt).scalars().all()
