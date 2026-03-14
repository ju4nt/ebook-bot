"""
Servicio de generación de contenido con Claude
Colconexus Data Center SAS
"""
import datetime
import anthropic


def build_ebook_prompt(topic, best_angle, audience, content_type,
                       chapters, lang, trend_score, momentum, ctx):
    chapters_text = "\n\n".join([
        f"## Capítulo {i+1}: [Título del capítulo orientado a beneficio]\n\n"
        f"[3-4 párrafos con contenido rico, ejemplos concretos y valor real para {audience}. "
        f"Mínimo 200 palabras por capítulo.]\n\n"
        f"**Puntos clave:**\n- Punto 1\n- Punto 2\n- Punto 3\n\n---"
        for i in range(chapters)
    ])

    return f"""Eres un experto escritor de eBooks de alto valor comercial. Crea un eBook completo en {lang}.

TEMA TRENDING: {topic}
ÁNGULO ÓPTIMO DETECTADO: {best_angle}
AUDIENCIA OBJETIVO: {audience}
TIPO: {content_type}
CAPÍTULOS: {chapters}
SCORE TENDENCIA: {trend_score}/100 — MOMENTUM: {momentum}
{('CONTEXTO ADICIONAL: ' + ctx) if ctx else ''}

INSTRUCCIONES:
- Escribe con autoridad y valor real, no genérico
- Usa ejemplos concretos y accionables
- Mínimo 1800 palabras en total
- El título debe ser impactante y orientado a resultado

ESTRUCTURA EXACTA:

# [TÍTULO PODEROSO DEL EBOOK]
## Subtítulo: [complementa y amplía el título]

---

### Por qué este tema importa ahora
[2-3 párrafos sobre la oportunidad actual basada en el score de tendencia {trend_score}/100]

---

{chapters_text}

### Conclusión y llamado a la acción
[Cierre motivador de 2 párrafos con pasos concretos a seguir]

---

*© {datetime.date.today().year} — Tendencia: {trend_score}/100 | Momentum: {momentum}*"""


def build_minicurso_prompt(topic, best_angle, audience, content_type,
                            chapters, lang, trend_score, momentum, ctx):
    modules_text = "\n\n".join([
        f"## Módulo {i+1}: [Título orientado a resultado concreto]\n\n"
        f"**Objetivo del módulo:** [qué logrará el estudiante al terminar este módulo]\n\n"
        f"**Contenido principal:**\n[3-4 párrafos de contenido rico, práctico y accionable. "
        f"Mínimo 180 palabras.]\n\n"
        f"**Ejercicio práctico:**\n[Ejercicio concreto que el estudiante puede hacer hoy, "
        f"con pasos específicos]\n\n"
        f"**Recursos recomendados:**\n- Recurso o herramienta 1\n- Recurso o herramienta 2\n\n---"
        for i in range(chapters)
    ])

    return f"""Eres un experto en diseño instruccional y marketing de contenidos. Crea un mini curso completo en {lang}.

TEMA TRENDING: {topic}
ÁNGULO ÓPTIMO DETECTADO: {best_angle}
AUDIENCIA OBJETIVO: {audience}
TIPO: {content_type}
MÓDULOS: {chapters}
SCORE TENDENCIA: {trend_score}/100 — MOMENTUM: {momentum}
{('CONTEXTO ADICIONAL: ' + ctx) if ctx else ''}

INSTRUCCIONES:
- Diseño instruccional real: cada módulo tiene objetivo, contenido, ejercicio
- Lenguaje directo, motivador y práctico
- Mínimo 1600 palabras en total
- El nombre del curso debe ser memorable y orientado a transformación

ESTRUCTURA EXACTA:

# [NOMBRE DEL MINI CURSO: impactante, orientado a transformación]
## Tagline: [frase que describe el beneficio principal en menos de 15 palabras]

---

### ¿Por qué este curso ahora?
[2 párrafos explicando la oportunidad y relevancia actual del tema con score {trend_score}/100]

---

{modules_text}

### Próximos pasos y comunidad
[Cómo el estudiante continúa su aprendizaje después del curso]

---

*Score de tendencia: {trend_score}/100 — Momentum: {momentum} | {datetime.date.today().year}*"""


def generate_content(client: anthropic.Anthropic, model: str, max_tokens: int,
                     topic: str, best_angle: str, audience: str, content_type: str,
                     chapters: int, lang: str, trend_score: int, momentum: str, ctx: str) -> str:
    """Genera el contenido completo del eBook o mini curso."""

    is_minicurso = "minicurso" in content_type

    if is_minicurso:
        prompt = build_minicurso_prompt(
            topic, best_angle, audience, content_type,
            chapters, lang, trend_score, momentum, ctx
        )
    else:
        prompt = build_ebook_prompt(
            topic, best_angle, audience, content_type,
            chapters, lang, trend_score, momentum, ctx
        )

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )

    return "".join(b.text for b in response.content if b.type == "text")
