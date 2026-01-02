from pathlib import Path
import uuid

from typer.testing import CliRunner

from kindearth import cli
from kindearth.config import Settings
from kindearth.core.forecasting import ScenarioType, V0ForecastEngine
from kindearth.core.gates import GATE_DEFINITIONS, GateResponse
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


def _gate_response(gate_def, core_answer: str, engagement_id: str = "eng") -> GateResponse:
    probes = {key: f"{gate_def.name} {key}" for key in gate_def.required_probes}
    return GateResponse(
        id=str(uuid.uuid4()),
        engagement_id=engagement_id,
        gate_name=gate_def.name,
        core_answer=core_answer,
        probes=probes,
        assumptions=f"{gate_def.name} assumption",
        uncertainties="",
        created_at="2024-01-01T00:00:00Z",
    )


def test_cli_gate_run_persists_all_gates(tmp_path, monkeypatch):
    settings = _patch_settings(tmp_path, monkeypatch)
    runner = CliRunner()
    assert runner.invoke(cli.app, ["init"]).exit_code == 0

    repo = Repository(db_path=settings.db_path)
    engagement = repo.create_engagement(name="Gate Run", org_name="Org", notes="")

    answers = []
    for gate in GATE_DEFINITIONS:
        answers.append(f"{gate.name} core")
        for key in gate.required_probes:
            answers.append(f"{gate.name} {key}")
        answers.append("assumption")
        answers.append("uncertainty")
    input_text = "\n".join(answers) + "\n"

    result = runner.invoke(
        cli.app,
        ["gate", "run", "--engagement-id", engagement.id],
        input=input_text,
    )

    assert result.exit_code == 0
    responses = repo.get_gate_responses(engagement.id)
    assert len(responses) == 5
    assert {resp.gate_name for resp in responses} == {gate.name for gate in GATE_DEFINITIONS}


def test_forecast_changes_with_gate_response_change():
    engine = V0ForecastEngine()
    gates_a = [_gate_response(gate, f"{gate.name} answer A") for gate in GATE_DEFINITIONS]
    gates_b = [
        _gate_response(gate, "Relational Mapping shifted answer" if idx == 0 else f"{gate.name} answer A")
        for idx, gate in enumerate(GATE_DEFINITIONS)
    ]

    failure_a = next(s for s in engine.run("Engagement", gates_a) if s.name == ScenarioType.FAILURE)
    failure_b = next(s for s in engine.run("Engagement", gates_b) if s.name == ScenarioType.FAILURE)

    risk_texts_a = {r.description for r in failure_a.risks}
    risk_texts_b = {r.description for r in failure_b.risks}

    assert risk_texts_a != risk_texts_b
    assert any("Relational Mapping shifted answer" in r.description for r in failure_b.risks)


def test_cli_forecast_run_uses_saved_gates(tmp_path, monkeypatch):
    settings = _patch_settings(tmp_path, monkeypatch)
    runner = CliRunner()
    assert runner.invoke(cli.app, ["init"]).exit_code == 0

    repo = Repository(db_path=settings.db_path)
    engagement = repo.create_engagement(name="Forecast Gates", org_name="Org", notes="")
    for gate in GATE_DEFINITIONS:
        repo.save_gate_response(
            engagement_id=engagement.id,
            gate_name=gate.name,
            core_answer=f"{gate.name} core detail",
            probes={key: "ok" for key in gate.required_probes},
            assumptions="assumption",
            uncertainties="",
        )

    result = runner.invoke(cli.app, ["forecast", "run", "--engagement-id", engagement.id])
    assert result.exit_code == 0

    scenarios = repo.get_forecasts(engagement.id)
    assert scenarios is not None
    failure = next(s for s in scenarios if s.name == ScenarioType.FAILURE)
    assert "Relational Mapping indicates" in failure.narrative
    assert any("Relational Mapping" in risk.description for risk in failure.risks)
