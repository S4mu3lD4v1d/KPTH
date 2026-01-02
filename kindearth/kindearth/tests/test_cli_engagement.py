from pathlib import Path

from typer.testing import CliRunner

from kindearth import cli
from kindearth.config import Settings
from kindearth.db.repo import Repository


def _patch_settings(tmp_path: Path, monkeypatch) -> Settings:
    data_dir = tmp_path / "data"
    settings = Settings(
        data_dir=data_dir,
        db_path=data_dir / "kindearth.sqlite3",
        templates_dir=tmp_path / "templates",
        exports_dir=data_dir / "exports",
    )
    monkeypatch.setattr(cli, "SETTINGS", settings)
    import kindearth.config as cfg

    monkeypatch.setattr(cfg, "SETTINGS", settings)
    import kindearth.db.repo as repo_mod

    monkeypatch.setattr(repo_mod, "SETTINGS", settings)
    import kindearth.db.migrate as migrate_mod

    monkeypatch.setattr(migrate_mod, "SETTINGS", settings)
    return settings


def test_engagement_new_positional(tmp_path, monkeypatch):
    settings = _patch_settings(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(cli.app, ["init"])
    assert result.exit_code == 0

    result = runner.invoke(cli.app, ["engagement", "new", "Positional Name", "Org Co"])
    assert result.exit_code == 0

    repo = Repository(db_path=settings.db_path)
    rows = repo.list_engagements()
    assert any(r.name == "Positional Name" and r.org_name == "Org Co" for r in rows)


def test_engagement_new_with_options(tmp_path, monkeypatch):
    settings = _patch_settings(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(cli.app, ["init"])
    assert result.exit_code == 0

    result = runner.invoke(
        cli.app,
        ["engagement", "new", "--name", "Option Name", "--org", "Option Org", "--notes", "note"],
    )
    assert result.exit_code == 0

    repo = Repository(db_path=settings.db_path)
    rows = repo.list_engagements()
    assert any(r.name == "Option Name" and r.org_name == "Option Org" for r in rows)
