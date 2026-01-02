from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Paths for local, in-house storage."""

    data_dir: Path = Path("data")
    db_path: Path = Path("data") / "kindearth.sqlite3"
    templates_dir: Path = Path(__file__).resolve().parent / "templates"
    exports_dir: Path = Path("data") / "exports"


SETTINGS = Settings()
