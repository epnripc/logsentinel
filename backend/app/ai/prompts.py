# Dueño: Front. Textos de la IA. Se mejora en la fase 3 (guía de Front, F-07).
# NO cambies los nombres de las variables: Backend e Infra los usan.

SYSTEM = "Eres un analista de ciberseguridad. Respondes en español, claro y sin tecnicismos."

PROMPT_ALERTA = "Explica esta alerta en 3 frases: qué pasa, qué riesgo tiene y qué hacer. Datos: {alerta}"

PROMPT_RESUMEN = "Resume en 3 frases el estado de seguridad. Alertas abiertas:\n{alertas}"

FALLBACKS = {
    "default": "Actividad sospechosa desde la IP {ip} ({count} eventos). Recomendamos bloquearla.",
}

RESUMEN_VACIO = "Todo en calma: no hay amenazas abiertas."
RESUMEN_FALLBACK = "Hay {n} amenazas abiertas. Revisa las de gravedad alta primero."
