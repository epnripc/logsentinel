import os
from pydantic import NaiveDatetime  # fechas sin zona horaria (hora local)
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine

DB_URL = os.getenv("DB_URL", "sqlite:///./data/logsentinel.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


class LogIn(SQLModel):
    """Lo que nos envían a POST /ingest (no es una tabla)."""
    ip: str
    type: str                      # login_ok | login_failed | ssh_failed | http
    user: Optional[str] = None
    path: Optional[str] = None
    status: int = 200


class Log(LogIn, table=True):
    """Cada evento guardado. Hereda los campos de LogIn y añade id y hora."""
    id: Optional[int] = Field(default=None, primary_key=True)
    ts: NaiveDatetime = Field(index=True)


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ip: str = Field(index=True)
    kind: str                      # bruteforce | scan | ssh | flood
    count: int = 1
    severity: str = "low"          # high | medium | low
    first_seen: NaiveDatetime
    last_seen: NaiveDatetime
    status: str = "open"           # open | mitigated
    explanation: Optional[str] = None


class Blocked(SQLModel, table=True):
    ip: str = Field(primary_key=True)
    blocked_at: NaiveDatetime


def init_db():
    os.makedirs("data", exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
