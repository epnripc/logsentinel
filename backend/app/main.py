from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()  # lee el .env de la raíz del repo

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, func, select

from app.db import Alert, Blocked, Log, LogIn, get_session, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # crea las tablas al arrancar
    yield


app = FastAPI(title="LogSentinel", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/ingest")
def ingest(data: LogIn, db: Session = Depends(get_session)):
    log = Log(**data.model_dump(), ts=datetime.now())
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"accepted": True, "id": log.id}


@app.get("/logs")
def logs(db: Session = Depends(get_session)):
    return db.exec(select(Log).order_by(Log.id.desc()).limit(20)).all()
