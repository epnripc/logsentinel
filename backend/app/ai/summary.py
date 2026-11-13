# Dueño: Infra. Resumen ejecutivo con IA. Se completa en la fase 3 (guía de Infra, I-07).
from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
def summary():
    return {"text": "Resumen pendiente: se conectará a la IA en la fase 3."}
