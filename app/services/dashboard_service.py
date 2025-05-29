from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import select, func, case
from ..models import Project, Execution, TestCase


def get_executions_per_project(db: Session):
    stmt = (
        select(Project.name, func.count(Execution.id).label("execution_count"))
        .join(Execution, Execution.project_id == Project.id)
        .group_by(Project.name)
        .order_by(Project.name)
    )
    results = db.execute(stmt).all()
    return [{"project": name, "execution_count": count} for name, count in results]


def get_pass_fail_trend(db: Session, from_date: date, to_date: date):
    passed_case = case((TestCase.status == 'PASSED', 1), else_=0)
    failed_case = case((TestCase.status == 'FAILED', 1), else_=0)

    stmt = (
        select(
            func.date(Execution.executed_at).label("date"),
            func.sum(passed_case).label("passed"),
            func.sum(failed_case).label("failed")
        )
        .join(TestCase, TestCase.execution_id == Execution.id)
        .where(Execution.executed_at.between(from_date, to_date))
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


def get_average_execution_durations(db: Session):
    stmt = (
        select(
            Project.name,
            func.avg(TestCase.duration_seconds).label("avg_duration_seconds")
        )
        .join(Execution, Execution.project_id == Project.id)
        .join(TestCase, TestCase.execution_id == Execution.id)
        .group_by(Project.name)
        .order_by(Project.name)
    )
    results = db.execute(stmt).all()
    return [
        {
            "project": name,
            "avg_duration_seconds": round(avg_duration, 2)
        } for name, avg_duration in results
    ]

