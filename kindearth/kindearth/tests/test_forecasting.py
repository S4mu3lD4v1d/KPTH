from pathlib import Path

from typer.testing import CliRunner

from kindearth import cli
from kindearth.config import Settings
from kindearth.core.forecasting import V0ForecastEngine, ScenarioType
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


def test_schema_has_forecasts_table(tmp_path):
    repo = Repository(db_path=tmp_path / "db.sqlite3")
    repo.ensure_schema()

    with repo.connect() as con:
        row = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='forecasts'"
        ).fetchone()

    assert row is not None


def test_save_and_get_forecasts(tmp_path):
    repo = Repository(db_path=tmp_path / "db.sqlite3")
    repo.ensure_schema()
    engagement = repo.create_engagement(name="Forecast Test", org_name="Org", notes="")

    engine = V0ForecastEngine()
    scenarios = engine.generate(engagement.name)

    repo.save_forecasts(engagement.id, scenarios)
    fetched = repo.get_forecasts(engagement.id)

    assert fetched is not None
    assert len(fetched) == len(scenarios)
    assert {s.name for s in fetched} == {s.name for s in scenarios}


def test_cli_forecast_run(tmp_path, monkeypatch):
    settings = _patch_settings(tmp_path, monkeypatch)
    runner = CliRunner()
    init_result = runner.invoke(cli.app, ["init"])
    assert init_result.exit_code == 0

    repo = Repository(db_path=settings.db_path)
    engagement = repo.create_engagement(name="CLI Forecast", org_name="Org", notes="")

    result = runner.invoke(cli.app, ["forecast", "run", "--engagement-id", engagement.id])
    assert result.exit_code == 0

    scenarios = repo.get_forecasts(engagement.id)
    assert scenarios is not None
    assert len(scenarios) == 3
    assert {scenario.name for scenario in scenarios} == {
        ScenarioType.BASELINE,
        ScenarioType.REGENERATIVE,
        ScenarioType.FAILURE,
    }
