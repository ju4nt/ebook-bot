"""
Componente: Gestor de límite diario de uso
Colconexus Data Center SAS
"""
import json
import datetime
from pathlib import Path

LOG_DIR = Path(r"C:\ebook-bot\logs")
DAILY_LIMIT = 3


def _log_path() -> Path:
    return LOG_DIR / f"usage_{datetime.date.today().isoformat()}.json"


def _load() -> dict:
    p = _log_path()
    if not p.exists():
        data = {"date": datetime.date.today().isoformat(), "count": 0, "entries": []}
        _save(data)
        return data
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(_log_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_usage() -> int:
    return _load()["count"]


def get_remaining(limit: int = DAILY_LIMIT) -> int:
    return max(0, limit - get_usage())


def can_generate(limit: int = DAILY_LIMIT) -> bool:
    return get_usage() < limit


def register_generation(topic: str, content_type: str, trend_score: int):
    data = _load()
    data["count"] += 1
    data["entries"].append({
        "time": datetime.datetime.now().isoformat(),
        "topic": topic,
        "type": content_type,
        "trend_score": trend_score
    })
    _save(data)


def get_history() -> list:
    return _load().get("entries", [])


def reset_for_dev():
    """Solo para desarrollo — reinicia el contador del día."""
    data = _load()
    data["count"] = 0
    data["entries"] = []
    _save(data)
