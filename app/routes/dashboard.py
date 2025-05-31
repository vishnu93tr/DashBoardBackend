from datetime import date
from typing import Union

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..services.dashboard_service import (
    get_pass_fail_trend,
    get_executions_per_project,
    get_test_cases_for_project, get_all_projects, get_average_execution_durations_trend,
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard/executions-per-project")
def executions_per_project(
    project_name: str = Query(..., description="Project name"),
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    return get_executions_per_project(db, project_name, from_date, to_date)


@router.get("/dashboard/pass-fail-trend")
def pass_fail_trend(
    project_name: str = Query(..., description="Project name"),
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    return get_pass_fail_trend(db, project_name, from_date, to_date)


@router.get("/dashboard/average-execution-durations-trend")
def average_execution_durations_trend(
    project_name: str = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
):
    return get_average_execution_durations_trend(db, project_name, from_date, to_date)


@router.get("/dashboard/test-cases")
def test_cases_by_project(
    project_name: str = Query(..., description="Project name"),
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    return get_test_cases_for_project(db, project_name, from_date, to_date)

@router.get("/dashboard/projects")
def list_projects(db: Session = Depends(get_db)):
    project_names = get_all_projects(db)
    return {"projects": project_names}

