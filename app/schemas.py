from pydantic import BaseModel

class ExecutionStats(BaseModel):
    project: str
    executions: int
    avg_duration: float
    pass_rate: float
