from datetime import datetime
from typing import Annotated
from sqlalchemy import ForeignKey, func, Index, CheckConstraint
from database import Base, str_256
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(
        server_default=func.now(),
        onupdate=datetime.now
    )]


class Workload(enum.Enum):
    parttime = "parttime"
    fulltime = "fulltime"



class Workers(Base):
    __tablename__ = "workers"

    id: Mapped[intpk]
    username: Mapped[str]

    resumes: Mapped[list["Resumes"]] = relationship(
        back_populates="worker",
    )

    resumes_parttime: Mapped[list["Resumes"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(Workers.id == Resumes.worker_id, Resumes.workload == 'parttime')",
        order_by="Resumes.id.desc()",
        overlaps="resumes",
    )



class Resumes(Base):
    __tablename__ = "resumes"
    
    id: Mapped[intpk]
    title: Mapped[str_256]
    compensation: Mapped[int | None]
    workload: Mapped[Workload]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE")) # удаляется каскадно только при удалении worker
    created_at: Mapped[created_at] 
    updated_at: Mapped[updated_at]

    # many2one
    worker: Mapped["Workers"] = relationship(
        back_populates="resumes",   
    )

    repr_cols_num = 4 # выведем первые 4 колонки
    repr_cols = ("created_at",) # и дополнительно created_at

    __table_args__ = (
    Index("title_index", "title"),
    CheckConstraint("compensation > 0", name="checl_compensation_positive"),
    )





