"""
EBook Bot — Lógica principal refactorizada
Usa servicios y componentes modulares
Colconexus Data Center SAS
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

load_dotenv(dotenv_path=r"C:\ebook-bot\.env")

# Agregar app al path
sys.path.insert(0, r"C:\ebook-bot")

from app.services.trend_service import validate_trend
from app.services.content_service import generate_content
from app.components.renderer import render_and_save
from app.components.usage_tracker import (
    get_usage, get_remaining, can_generate,
    register_generation, get_history, reset_for_dev
)

console = Console()

import json
with open(r"C:\ebook-bot\config\settings.json", encoding="utf-8") as f:
    SETTINGS = json.load(f)

DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", SETTINGS["daily_limit"]))
MODEL = SETTINGS["model"]
MAX_TOKENS_TREND = SETTINGS["max_tokens_trend"]
MAX_TOKENS_CONTENT = SETTINGS["max_tokens_content"]


class EbookBot:

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            console.print("[red]ERROR: ANTHROPIC_API_KEY no encontrada en .env[/red]")
            raise SystemExit(1)
        self.client = anthropic.Anthropic(api_key=api_key)

    # ------------------------------------------------------------------ #
    # MOSTRAR USO
    # ------------------------------------------------------------------ #
    def show_usage(self):
        used = get_usage()
        rem = get_remaining(DAILY_LIMIT)
        console.print(f"\n[bold]Uso hoy:[/bold] {used}/{DAILY_LIMIT} — Disponibles: [green]{rem}[/green]")
        history = get_history()
        if history:
            t = Table(show_header=True, header_style="bold cyan")
            t.add_column("Hora", style="dim")
            t.add_column("Tema")
            t.add_column("Tipo")
            t.add_column("Score", justify="right")
            for e in history:
                t.add_row(
                    e["time"][11:19],
                    e["topic"][:45],
                    e["type"],
                    str(e.get("trend_score", "—"))
                )
            console.print(t)

    # ------------------------------------------------------------------ #
    # LISTAR OUTPUTS
    # ------------------------------------------------------------------ #
    def list_outputs(self):
        output_dir = Path(r"C:\ebook-bot\outputs")
        files = sorted(output_dir.rglob("*.html"), reverse=True)[:20]
        if not files:
            console.print("[dim]No hay archivos generados aún.[/dim]")
            return
        t = Table(show_header=True, header_style="bold cyan")
        t.add_column("Archivo")
        t.add_column("Tipo")
        t.add_column("Tamaño", justify="right")
        for f in files:
            size = f"{f.stat().st_size // 1024} KB"
            t.add_row(f.name[:55], f.parent.name, size)
        console.print(t)

    # ------------------------------------------------------------------ #
    # FLUJO PRINCIPAL
    # ------------------------------------------------------------------ #
    def run(self):
        # 1. Verificar límite diario
        if not can_generate(DAILY_LIMIT):
            console.print(
                f"[red]Límite diario alcanzado ({DAILY_LIMIT}/día). "
                f"Vuelve mañana o ajusta DAILY_LIMIT en .env[/red]"
            )
            return

        rem = get_remaining(DAILY_LIMIT)
        console.print(f"\n[dim]Usos disponibles hoy: {rem}/{DAILY_LIMIT}[/dim]")

        # 2. Ingresar tema
        topic = console.input("\n[bold]Tema:[/bold] ").strip()
        if not topic:
            console.print("[red]Tema vacío, cancelando.[/red]")
            return

        lang_opts = {"1": "Español", "2": "English", "3": "Português"}
        console.print("[bold]Idioma:[/bold]  1) Español  2) English  3) Português")
        lang = lang_opts.get(console.input("> ").strip(), "Español")

        # 3. Validar tendencia
        with Progress(SpinnerColumn(), TextColumn("[green]{task.description}"), console=console) as p:
            task = p.add_task("Buscando tendencias en internet...", total=None)
            trend = validate_trend(self.client, topic, lang, MODEL)
            p.stop()

        score = trend.get("score", 50)
        is_trending = trend.get("is_trending", True)
        momentum = trend.get("momentum", "Estable")

        # Mostrar resultado tendencia
        color = "green" if is_trending else ("yellow" if score > 40 else "red")
        status_label = (
            "[green]EN TENDENCIA[/green]" if is_trending
            else ("[yellow]POTENCIAL MODERADO[/yellow]" if score > 40
                  else "[red]POCA TENDENCIA[/red]")
        )
        console.print(Panel(
            f"{status_label}  |  Score: [bold]{score}/100[/bold]  |  "
            f"Momentum: {momentum}  |  Competencia: {trend.get('competition','—')}\n\n"
            f"{trend.get('summary','')}\n\n"
            f"[dim]{trend.get('why','')}[/dim]"
            + (f"\n\n[italic]Mejor ángulo: {trend['best_angle']}[/italic]"
               if trend.get('best_angle') else ""),
            title="Análisis de tendencia",
            border_style=color
        ))

        # 4. Sugerencias de ángulos si no está en tendencia
        suggestions = trend.get("suggestions", [])
        if suggestions and not is_trending:
            console.print("\n[bold]Ángulos alternativos sugeridos:[/bold]")
            for i, s in enumerate(suggestions, 1):
                console.print(f"  [cyan]{i}[/cyan]  {s}")
            pick = console.input(
                "Elige un ángulo (1-3) o Enter para continuar con el tema original: "
            ).strip()
            if pick in ["1", "2", "3"] and int(pick) <= len(suggestions):
                topic = suggestions[int(pick) - 1]
                console.print(f"[dim]Nuevo tema: {topic}[/dim]")

        best_angle = trend.get("best_angle", topic)

        # 5. Configurar contenido
        console.print("\n[bold]Tipo de contenido:[/bold]")
        types = SETTINGS["content_types"]
        for i, t in enumerate(types, 1):
            console.print(f"  [cyan]{i}[/cyan]  {t}")
        t_pick = console.input("> ").strip()
        content_type = types[int(t_pick) - 1] if t_pick in ["1", "2", "3", "4"] else types[0]

        audience = console.input("[bold]Audiencia objetivo:[/bold] ").strip() or "profesionales"
        ch_raw = console.input("[bold]Capítulos/Módulos[/bold] (4/6/8) [6]: ").strip() or "6"
        chapters = int(ch_raw) if ch_raw in ["4", "6", "8"] else 6
        ctx = console.input("[bold]Contexto adicional[/bold] (Enter para omitir): ").strip()

        # 6. Generar contenido
        with Progress(SpinnerColumn(), TextColumn("[green]{task.description}"), console=console) as p:
            tipo_label = "mini curso" if "minicurso" in content_type else "eBook"
            p.add_task(f"Generando {tipo_label} con Claude...", total=None)
            markdown = generate_content(
                client=self.client,
                model=MODEL,
                max_tokens=MAX_TOKENS_CONTENT,
                topic=topic,
                best_angle=best_angle,
                audience=audience,
                content_type=content_type,
                chapters=chapters,
                lang=lang,
                trend_score=score,
                momentum=momentum,
                ctx=ctx
            )

        # 7. Renderizar y guardar con template
        out_path = render_and_save(
            markdown=markdown,
            content_type=content_type,
            audience=audience,
            chapters=chapters,
            trend_score=score,
            momentum=momentum,
            lang=lang
        )

        # 8. Registrar uso
        register_generation(topic, content_type, score)

        # 9. Resultado
        console.print(Panel(
            f"[green]Generado exitosamente[/green]\n\n"
            f"Archivo: [cyan]{out_path}[/cyan]\n"
            f"Usos restantes hoy: [bold]{get_remaining(DAILY_LIMIT)}[/bold]",
            border_style="green",
            title="Listo"
        ))
        console.print(f"\n[dim]Abre en navegador:[/dim] [cyan]{out_path}[/cyan]")
