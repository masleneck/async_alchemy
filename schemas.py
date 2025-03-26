from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from models import Workload

class WorkersAddDTO(BaseModel): # data transfer obj
    username: str

class WorkersDTO(WorkersAddDTO):
    id: int

class ResumesAddDTO(BaseModel):
    title: str
    compensation: Optional[int]
    workload: Workload
    worker_id: int

class ResumesDTO(ResumesAddDTO):
    id: int
    created_at: datetime
    updated_at: datetime

class ResumesRelDTO(ResumesDTO):
    worker: "WorkersDTO"

class WorkersRelDTO(WorkersDTO):
    resumes: list["ResumesDTO"]