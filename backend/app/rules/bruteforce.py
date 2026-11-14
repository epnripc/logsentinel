from app.db import Log
from app.rules.common import count_recent, upsert_alert

THRESHOLD = 10  # intentos fallidos en 60 segundos


def check(log, db):
    if log.type == "login_failed":
        kind = "bruteforce"
    elif log.type == "ssh_failed":
        kind = "ssh"
    else:
        return
    n = count_recent(db, log.ip, 60, Log.type == log.type)
    if n >= THRESHOLD:
        upsert_alert(db, log.ip, kind, "high", n)
