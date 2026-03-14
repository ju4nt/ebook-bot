# EBook Bot — Generador con Validación de Tendencias

Proyecto: **EBOOK-BOT**  
Empresa: Colconexus Data Center SAS  
Versión: 1.0.0

## Estructura del proyecto

```
C:\ebook-bot\
├── app\
│   ├── components\       # Módulos reutilizables del bot
│   ├── services\         # Servicios: Anthropic API, búsqueda web
│   └── templates\        # Plantillas HTML para eBooks y mini cursos
├── outputs\
│   ├── ebooks\           # eBooks generados (.html)
│   └── minicursos\       # Mini cursos generados (.html)
├── logs\                 # Registro de generaciones (uso diario)
├── config\               # Configuración y variables de entorno
├── main.py               # Punto de entrada principal
├── bot.py                # Lógica principal del bot
├── requirements.txt      # Dependencias Python
└── .env.example          # Plantilla de variables de entorno
```

## Flujo del bot

1. Usuario ingresa un tema
2. Bot valida tendencia con búsqueda web (Anthropic + web_search tool)
3. Bot sugiere ángulos si el score es bajo
4. Usuario elige tipo: eBook o Mini Curso
5. Bot genera contenido completo con Claude
6. Se guarda en outputs/ con fecha y metadata
7. Límite: 3 generaciones por día (configurable)

## Instalación

```bash
cd C:\ebook-bot
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu API key
python main.py
```
