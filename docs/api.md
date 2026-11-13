# Contrato de la API de LogSentinel

- URL base en local: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs
- Si algo cambia, se avisa al equipo y se actualiza este fichero PRIMERO.

## GET /health
Respuesta: `{"ok": true}`

## POST /ingest
Recibe un evento. La hora la pone el backend.

Body:
```json
{"ip": "45.13.2.9", "type": "login_failed", "user": "admin", "path": "/login", "status": 401}
```
- `type`: `login_ok` | `login_failed` | `ssh_failed` | `http`
- `user` y `path` son opcionales

Respuesta: `{"accepted": true, "id": 123}`
Si la IP está bloqueada: `{"accepted": false, "reason": "blocked"}`

## GET /stats
```json
{
  "total": 1240,
  "attacks": 2,
  "blocked": 1,
  "timeline": [{"t": "10:02:10", "normal": 14, "suspicious": 3}]
}
```
- `timeline`: últimos 5 minutos en tramos de 10 segundos

## GET /alerts
```json
[
  {"id": 7, "ip": "45.13.2.9", "kind": "bruteforce", "count": 48, "severity": "high",
   "first_seen": "2026-11-13T10:01:02", "last_seen": "2026-11-13T10:03:40",
   "status": "open", "explanation": null}
]
```
- `kind`: `bruteforce` | `scan` | `ssh` | `flood`
- `severity`: `high` | `medium` | `low`
- `status`: `open` | `mitigated`
- Orden: abiertas primero, luego por gravedad y por la más reciente

## GET /alerts/{id}/explain
`{"text": "Alguien desde la IP 45.13.2.9 está intentando adivinar contraseñas..."}`

## POST /alerts/{id}/mitigate
`{"ok": true, "ip": "45.13.2.9"}`
Bloquea la IP: desde ese momento `/ingest` rechaza sus eventos.

## GET /summary
`{"text": "Hay 2 amenazas abiertas..."}`

## POST /reset (solo para la demo)
`{"ok": true}`
