"""
EBook Bot — Colconexus Data Center SAS
Punto de entrada principal
"""
import sys
from bot import EbookBot
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "[bold green]EBook Bot v1.0[/bold green]\n"
        "[dim]Generador de eBooks y Mini Cursos con validación de tendencias[/dim]\n"
        "[dim]Colconexus Data Center SAS[/dim]",
        border_style="green"
    ))

    bot = EbookBot()

    while True:
        console.print("\n[bold]¿Qué deseas hacer?[/bold]")
        console.print("  [cyan]1[/cyan] Generar eBook o Mini Curso")
        console.print("  [cyan]2[/cyan] Ver uso del día")
        console.print("  [cyan]3[/cyan] Ver archivos generados")
        console.print("  [cyan]q[/cyan] Salir")

        choice = console.input("\n> ").strip().lower()

        if choice == '1':
            bot.run()
        elif choice == '2':
            bot.show_usage()
        elif choice == '3':
            bot.list_outputs()
        elif choice == 'q':
            console.print("[dim]Hasta luego.[/dim]")
            sys.exit(0)
        else:
            console.print("[red]Opción no válida.[/red]")

if __name__ == "__main__":
    main()
