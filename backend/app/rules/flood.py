from app.rules.common import count_recent, upsert_alert

THRESHOLD = 200  # peticiones en 60 segundos desde la misma IP


def check(log, db):
    n = count_recent(db, log.ip, 60)
    if n >= THRESHOLD:
        upsert_alert(db, log.ip, "flood", "medium", n)
