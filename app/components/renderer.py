"""
Componente: Renderizador HTML con templates
Colconexus Data Center SAS
"""
import re
import datetime
from pathlib import Path


TEMPLATES_DIR = Path(r"C:\ebook-bot\app\templates")
OUTPUT_DIR = Path(r"C:\ebook-bot\outputs")


def markdown_to_html(text: str) -> str:
    """Convierte markdown básico a HTML."""
    lines = text.split("\n")
    html_lines = []
    in_ul = False
    in_p = False

    for line in lines:
        stripped = line.strip()

        # Headers
        if stripped.startswith("### "):
            if in_p: html_lines.append("</p>"); in_p = False
            if in_ul: html_lines.append("</ul>"); in_ul = False
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            if in_p: html_lines.append("</p>"); in_p = False
            if in_ul: html_lines.append("</ul>"); in_ul = False
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            if in_p: html_lines.append("</p>"); in_p = False
            if in_ul: html_lines.append("</ul>"); in_ul = False
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        # HR
        elif stripped == "---":
            if in_p: html_lines.append("</p>"); in_p = False
            if in_ul: html_lines.append("</ul>"); in_ul = False
            html_lines.append("<hr/>")
        # List items
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if in_p: html_lines.append("</p>"); in_p = False
            if not in_ul:
                html_lines.append("<ul>"); in_ul = True
            item = stripped[2:]
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            item = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item)
            html_lines.append(f"<li>{item}</li>")
        # Empty line
        elif stripped == "":
            if in_ul: html_lines.append("</ul>"); in_ul = False
            if in_p: html_lines.append("</p>"); in_p = False
        # Paragraph
        else:
            if in_ul: html_lines.append("</ul>"); in_ul = False
            line_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            line_html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line_html)
            if not in_p:
                html_lines.append(f"<p>{line_html}")
                in_p = True
            else:
                html_lines.append(f" {line_html}")

    if in_p: html_lines.append("</p>")
    if in_ul: html_lines.append("</ul>")

    return "\n".join(html_lines)


def extract_title_subtitle(markdown: str):
    """Extrae título y subtítulo del markdown generado."""
    title = "Sin título"
    subtitle = ""
    for line in markdown.splitlines():
        if line.startswith("# ") and title == "Sin título":
            title = line[2:].strip()
        elif line.startswith("## Subtítulo:") or line.startswith("## Tagline:"):
            subtitle = line.split(":", 1)[1].strip() if ":" in line else ""
        elif line.startswith("## ") and not subtitle:
            subtitle = line[3:].strip()
    return title, subtitle


def render_and_save(markdown: str, content_type: str, audience: str,
                    chapters: int, trend_score: int, momentum: str, lang: str) -> Path:
    """Renderiza el markdown con el template HTML y guarda el archivo."""

    is_minicurso = "minicurso" in content_type
    template_name = "minicurso.html" if is_minicurso else "ebook.html"
    template_path = TEMPLATES_DIR / template_name

    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    title, subtitle = extract_title_subtitle(markdown)
    body_html = markdown_to_html(markdown)
    today = datetime.date.today().strftime("%d/%m/%Y")

    # Reemplazar variables del template
    html = template
    replacements = {
        "{{ lang }}": lang[:2].lower(),
        "{{ title }}": title,
        "{{ subtitle }}": subtitle,
        "{{ content_type }}": content_type.replace("-", " ").title(),
        "{{ audience }}": audience,
        "{{ chapters }}": str(chapters),
        "{{ trend_score }}": str(trend_score),
        "{{ momentum }}": momentum,
        "{{ date }}": today,
        "{{ body_html }}": body_html,
    }
    for k, v in replacements.items():
        html = html.replace(k, v)

    # Determinar carpeta de salida
    folder = "minicursos" if is_minicurso else "ebooks"
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-')
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / folder / f"{slug}_{ts}.html"
    out_path.write_text(html, encoding="utf-8")

    return out_path
