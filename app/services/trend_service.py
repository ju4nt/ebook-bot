"""
Servicio de validación de tendencias
Colconexus Data Center SAS
"""
import json
import anthropic


def validate_trend(client: anthropic.Anthropic, topic: str, lang: str, model: str) -> dict:
    """
    Usa Claude + web_search para analizar si un tema está en tendencia.
    Retorna dict con: score, momentum, competition, is_trending,
                      summary, why, suggestions, best_angle
    """
    prompt = f"""Busca en internet tendencias actuales sobre: "{topic}".
Analiza: volumen de búsqueda, noticias recientes 2024-2025, interés en redes sociales,
crecimiento del tema, competencia de contenido existente.

Responde SOLO con este JSON (sin markdown, sin texto adicional):
{{
  "score": <número 1-100 de qué tan trending es>,
  "momentum": "<Creciendo|Estable|Bajando>",
  "competition": "<Alta|Media|Baja>",
  "is_trending": <true|false>,
  "summary": "<2-3 oraciones en {lang} sobre la tendencia del tema>",
  "why": "<razón principal por la que es o no es tendencia>",
  "suggestions": ["ángulo alternativo 1", "ángulo alternativo 2", "ángulo alternativo 3"],
  "best_angle": "<el mejor ángulo específico para crear contenido sobre este tema>"
}}"""

    response = client.messages.create(
        model=model,
        max_tokens=1200,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text
            break

    raw = text.strip().replace("```json", "").replace("```", "").strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]

    try:
        return json.loads(raw)
    except Exception:
        return {
            "score": 50,
            "momentum": "Estable",
            "competition": "Media",
            "is_trending": True,
            "summary": f"No se pudo analizar la tendencia de '{topic}' automáticamente.",
            "why": "Error al parsear respuesta de búsqueda.",
            "suggestions": [],
            "best_angle": topic
        }
