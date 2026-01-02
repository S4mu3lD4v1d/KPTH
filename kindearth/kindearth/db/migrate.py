from __future__ import annotations

import sqlite3
from pathlib import Path

from kindearth.config import SETTINGS


def migrate(db_path: Path | None = None) -> None:
    """Apply schema.sql to the SQLite database."""
    path = db_path or SETTINGS.db_path
    path.parent.mkdir(parents=True, exist_ok=True)

    schema_path = Path(__file__).resolve().parent / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")

    with sqlite3.connect(path) as con:
        con.executescript(schema)
        con.commit()
