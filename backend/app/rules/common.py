from datetime import datetime, timedelta

from sqlmodel import Session, func, select

from app.db import Alert, Log


def count_recent(db: Session, ip: str, seconds: int, *conditions) -> int:
    """Cuenta los eventos de una IP en los últimos N segundos (con filtros extra opcionales)."""
    since = datetime.now() - timedelta(seconds=seconds)
    query = select(func.count()).select_from(Log).where(Log.ip == ip, Log.ts >= since, *conditions)
    return db.exec(query).one()


def upsert_alert(db: Session, ip: str, kind: str, severity: str, count: int) -> Alert:
    """Crea una alerta nueva o actualiza la que ya está abierta para esa IP y ese tipo."""
    alert = db.exec(
        select(Alert).where(Alert.ip == ip, Alert.kind == kind, Alert.status == "open")
    ).first()
    now = datetime.now()
    if alert:
        alert.count = max(alert.count + 1, count)
        alert.last_seen = now
    else:
        alert = Alert(ip=ip, kind=kind, severity=severity, count=count, first_seen=now, last_seen=now)
    db.add(alert)
    return alert
