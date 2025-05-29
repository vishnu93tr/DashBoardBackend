from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..services.dashboard_service import get_pass_fail_trend, get_executions_per_project, \
    get_average_execution_durations

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard/executions-per-project")
def executions_per_project(db: Session = Depends(get_db)):
    return get_executions_per_project(db)


@router.get("/dashboard/pass-fail-trend")
def pass_fail_trend(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    return get_pass_fail_trend(db, from_date, to_date)


@router.get("/dashboard/average-execution-durations")
def average_execution_durations(db: Session = Depends(get_db)):
    return get_average_execution_durations(db)
