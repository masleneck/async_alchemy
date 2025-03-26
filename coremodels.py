import datetime
import enum
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, MetaData, String, Table, text, Enum

from models import Workload


metadata_obj = MetaData()

class Workload(enum.Enum):
    parttime = "parttime"
    fulltime = "fulltime"

    
workers_table = Table(
    "workers",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String),
)

resumes_table = Table(
    "resumes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String(256)),
    Column("compensation", Integer, nullable=True),
    Column("workload", Enum(Workload)),
    Column("worker_id", ForeignKey("workers.id", ondelete="CASCADE")),
    Column("created_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP,server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now),
)
