# EBOOK-BOT — Documentacion Completa

**Proyecto:** EBOOK-BOT  
**Empresa:** Colconexus Data Center SAS  
**Version:** 1.0.0  
**Autor:** ElkinT  

---

## Que es este proyecto?

Bot inteligente que genera eBooks y Mini Cursos de alta calidad usando **Claude AI** de Anthropic.
Antes de generar el contenido, valida si el tema esta en tendencia usando busqueda web en tiempo real,
garantizando que el contenido sea relevante y con demanda actual.

---

## Caracteristicas principales

- Validacion de tendencias en tiempo real (web search + score 1-100)
- Generacion de eBooks con hasta 8 capitulos
- Generacion de Mini Cursos con hasta 8 modulos
- Templates HTML profesionales para eBooks y Mini Cursos
- Limite configurable de 3 generaciones por dia
- Registro de uso con historial por dia
- Sugerencias de angulos alternativos cuando el tema tiene poco volumen
- Salida HTML lista para abrir en navegador o imprimir como PDF
- Interfaz CLI con menus interactivos usando Rich

---

## Arquitectura del proyecto

```
C:\ebook-bot\
|-- main.py                        # Punto de entrada — menu CLI
|-- bot.py                         # Orquestador principal del flujo
|-- requirements.txt               # Dependencias Python
|-- .env.example                   # Plantilla de variables de entorno
|-- run.bat                        # Ejecutar el bot (doble clic)
|-- install.bat                    # Instalar dependencias
|-- config\
|   `-- settings.json              # Configuracion global
|-- app\
|   |-- services\
|   |   |-- trend_service.py       # Claude + web_search: analiza tendencias
|   |   `-- content_service.py     # Claude: genera eBook o mini curso
|   |-- components\
|   |   |-- renderer.py            # Markdown -> HTML con templates
|   |   `-- usage_tracker.py       # Control del limite diario (JSON por dia)
|   `-- templates\
|       |-- ebook.html             # Template visual para eBooks
|       `-- minicurso.html         # Template visual para Mini Cursos
|-- outputs\
|   |-- ebooks\                    # eBooks generados (.html)
|   `-- minicursos\                # Mini Cursos generados (.html)
`-- logs\                          # Registro de uso diario (JSON)
```

---

## Instalacion

### Requisitos previos

- Python 3.10 o superior
- pip actualizado
- API Key de Anthropic (claude.ai)

### Pasos

```bash
# 1. Clonar o descargar el proyecto
cd C:\ebook-bot

# 2. Instalar dependencias (o doble clic en install.bat)
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env
# Editar .env con tu ANTHROPIC_API_KEY

# 4. Ejecutar
python main.py
# o doble clic en run.bat
```

---

## Configuracion (.env)

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
DAILY_LIMIT=3
OUTPUT_DIR=C:\ebook-bot\outputs
LOG_DIR=C:\ebook-bot\logs
DEFAULT_LANG=Espanol
```

---

## Configuracion (config/settings.json)

```json
{
  "project": "ebook-bot",
  "version": "1.0.0",
  "daily_limit": 3,
  "model": "claude-sonnet-4-20250514",
  "max_tokens_trend": 1000,
  "max_tokens_content": 4000,
  "content_types": [
    "ebook-guia-practica",
    "ebook-deep-dive",
    "minicurso-5-modulos",
    "minicurso-email"
  ]
}
```

---

## Flujo de uso

```
Usuario ingresa tema
        |
        v
[trend_service.py]
Claude + web_search
Busca tendencias en internet
Calcula score 1-100
        |
        v
Score >= 50? --NO--> Muestra angulos alternativos
        |
       SI
        v
Usuario configura:
- Tipo (eBook o Mini Curso)
- Audiencia
- Capitulos/Modulos (4, 6 u 8)
- Contexto adicional
        |
        v
[content_service.py]
Claude genera contenido completo
Minimo 1800 palabras
        |
        v
[renderer.py]
Markdown -> HTML
Aplica template (ebook.html o minicurso.html)
        |
        v
Archivo guardado en outputs/
[usage_tracker.py] registra el uso
        |
        v
Usuario abre el HTML en navegador
```

---

## Modulos — descripcion tecnica

### trend_service.py

Usa la API de Anthropic con la herramienta `web_search_20250305` para buscar tendencias
del tema en internet. Retorna un JSON con:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| score | int 1-100 | Que tan trending es el tema |
| momentum | string | Creciendo / Estable / Bajando |
| competition | string | Alta / Media / Baja |
| is_trending | bool | True si score >= 60 |
| summary | string | Resumen de la tendencia |
| why | string | Razon principal |
| suggestions | list | 3 angulos alternativos |
| best_angle | string | Mejor angulo para crear contenido |

### content_service.py

Genera el contenido completo usando Claude. Tiene dos prompts especializados:
- `build_ebook_prompt()` — para eBooks con capitulos
- `build_minicurso_prompt()` — para mini cursos con modulos, objetivos y ejercicios

### renderer.py

Convierte el markdown generado por Claude a HTML usando los templates de `app/templates/`.
Extrae automaticamente titulo y subtitulo, aplica el color de acento segun el tipo
(verde para eBooks, azul para mini cursos) y guarda con slug + timestamp.

### usage_tracker.py

Guarda un archivo JSON por dia en `logs/usage_YYYY-MM-DD.json` con el conteo
de generaciones y el historial de temas, tipos y scores.

---

## Templates HTML

### ebook.html
- Fuente: Georgia (serif) — estilo editorial
- Acento verde: #3B6D11
- Cover con badge, titulo, subtitulo y metadata
- H2 con borde izquierdo verde
- Responsive y optimizado para impresion

### minicurso.html
- Fuente: Arial (sans-serif) — estilo educativo moderno
- Acento azul: #185FA5
- Cover azul oscuro con tagline
- Tarjetas por modulo con numero flotante
- Caja de objetivo (azul claro) y ejercicio (amarillo) por modulo

---

## Limite diario

El limite por defecto es 3 generaciones por dia. Se puede cambiar en:
- `.env` con `DAILY_LIMIT=5`
- `config/settings.json` con `"daily_limit": 5`

El registro se guarda en `logs/usage_YYYY-MM-DD.json` y se resetea automaticamente cada dia.

---

## Roadmap v2.0

- [ ] Exportacion a PDF (weasyprint)
- [ ] Interfaz web con FastAPI
- [ ] Integracion con Google Trends API para score mas preciso
- [ ] Envio por email automatico
- [ ] Generacion de portada con imagen IA
- [ ] Soporte para mas idiomas
- [ ] Publicacion directa en plataformas (Gumroad, Hotmart)

---

## Licencia

MIT License — Colconexus Data Center SAS 2025