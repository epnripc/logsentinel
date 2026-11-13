# LogSentinel – Backend (FastAPI + IA)

Monitor SOC minimalista para pymes. Recibe logs **simulados** de un generador, detecta ataques con reglas por umbral, pide a un LLM (Groq) que explique cada alerta en lenguaje humano y permite "Mitigar con 1 clic" (bloquear la IP).

Equipo de 3: **Backend** (yo), **Infra** (generador + Docker) y **Front** (dashboard). Proyecto de hackathon: prima que la demo funcione siempre sobre la arquitectura perfecta.

## Stack y comandos
- Python 3.11 (venv en `backend/.venv`), FastAPI, SQLModel + SQLite, Groq SDK, python-dotenv.
- Terminal: Git Bash en Windows. Todo se ejecuta **desde `backend/`** con el venv activo:
  - Activar: `source .venv/Scripts/activate`
  - Instalar: `pip install -r requirements.txt`
  - Arrancar: `uvicorn app.main:app --reload` → pruebas en http://localhost:8000/docs
  - Todo junto (desde la raíz): `docker compose up --build`
  - Ataque de prueba: `docker compose run --rm generator --attack bruteforce`
- No hay tests todavía. Para verificar un cambio: arrancar uvicorn y probar con `curl` o `/docs`.
- Si se añade una dependencia, añadirla a `requirements.txt` (Infra lo usa para Docker).

## Estructura
```
backend/app/
  main.py          endpoints (MÍO)
  db.py            tablas Log, Alert, Blocked + LogIn (MÍO)
  rules/common.py  count_recent(), upsert_alert() (MÍO)
  rules/bruteforce.py, rules/flood.py (MÍO)
  rules/scan.py    (INFRA) expone check() y SUSPICIOUS
  ai/explain.py    ask_llm(), explain_alert() (MÍO)
  ai/summary.py    (INFRA) router de GET /summary
  ai/prompts.py    (FRONT) SYSTEM, PROMPT_ALERTA, FALLBACKS
```
Referencias: `../docs/api.md` (contrato de la API) y `../guias/backend.html` (guía paso a paso por tareas B-00…B-11).

## Propiedad de ficheros (regla de oro)
- Solo edito: `main.py`, `db.py`, `rules/common.py`, `rules/bruteforce.py`, `rules/flood.py`, `ai/explain.py`.
- **No modificar** `rules/scan.py`, `ai/summary.py`, `ai/prompts.py` ni nada fuera de `backend/`. Si hace falta un cambio ahí, proponerlo y yo se lo paso a su dueño.
- **No renombrar ni cambiar la firma** de `count_recent`, `upsert_alert` ni `ask_llm`: Infra las usa.

## Contrato de la API
- Las respuestas deben coincidir **exactamente** con `docs/api.md` (nombres de campos y tipos), porque el front depende de ello. Si un cambio altera una respuesta, avisarme antes; no "mejorar" el formato por iniciativa propia.
- Endpoints: `GET /health`, `POST /ingest`, `GET /logs`, `GET /stats`, `GET /alerts`, `GET /alerts/{id}/explain`, `POST /alerts/{id}/mitigate`, `GET /summary`, `POST /reset` (solo demo).

## Reglas de dominio
- Pipeline: `POST /ingest` → si la IP está en `Blocked` devuelve `{"accepted": false, "reason": "blocked"}` → guarda `Log` → pasa por `RULES` → cada regla `check(log, db)` crea o actualiza una `Alert`.
- Tipos de evento (`Log.type`): `login_ok | login_failed | ssh_failed | http`.
- Tipos de alerta (`Alert.kind`): `bruteforce | ssh | flood | scan`. Severidad: `high | medium | low`. Estado: `open | mitigated`.
- Umbrales, definidos como constante `THRESHOLD` en cada regla:
  - bruteforce / ssh: ≥10 `login_failed` / `ssh_failed` en 60 s por IP → `high`
  - flood: ≥200 eventos en 60 s por IP → `medium`
  - scan: lo define Infra en `scan.py`
- Una sola alerta `open` por (ip, kind): se actualiza con `upsert_alert`, no se duplica.
- Mitigar = insertar la IP en la tabla `Blocked` y marcar como `mitigated` todas sus alertas. **El bloqueo es solo lógico, dentro de la app.** Nunca ejecutar iptables, netsh, firewall del sistema ni nada que toque la red real.
- Fechas: `datetime.now()` naive (hora local); el servidor ignora el `ts` del payload.

## IA (Groq)
- Al LLM se le manda un **resumen** de la alerta (ip, tipo, nº eventos, gravedad, desde), nunca los logs en bruto.
- `ask_llm` devuelve `None` si no hay clave o falla, y entonces se usa `FALLBACKS`: la demo nunca debe quedarse en blanco ni dar error 500 por culpa de la IA.
- La explicación se cachea en `Alert.explanation`: solo se llama al LLM una vez por alerta.
- Modelo en `GROQ_MODEL` (por defecto `llama-3.1-8b-instant`), `timeout=10`, `temperature=0.3`, `max_tokens=300`.

## Seguridad y secretos
- `GROQ_API_KEY` vive en el `.env` de la raíz. **No leer, imprimir ni commitear `.env`**; tampoco escribir claves en el código ni en logs.
- Los campos de los logs (`user`, `path`, `ip`) son entrada no confiable: no meterlos sin control en prompts ni en SQL crudo (usar siempre SQLModel).
- `CORS *` y `/reset` sin autenticación son decisiones aceptadas **solo para la demo**; no "arreglarlas" sin pedírmelo, pero mencionarlas si se habla de producción.

## Git
- Una rama por tarea con prefijo `back/` (`back/rules`, `back/stats`, `back/ai`…), partiendo de `main` actualizado, y PR a `main`.
- No hacer commit, push ni merge sin que lo pida.
