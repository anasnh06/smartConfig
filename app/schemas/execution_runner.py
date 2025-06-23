from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ExecutionGroupStatus(BaseModel):
    group_id: int
    name: str
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


class ExecutionStatus(BaseModel):
    execution_id: int
    title: Optional[str]
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    groups: List[ExecutionGroupStatus] = []
