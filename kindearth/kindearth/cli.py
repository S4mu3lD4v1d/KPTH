from __future__ import annotations

import json
from typing import Optional

import typer
from rich import print
from rich.table import Table

from kindearth.config import SETTINGS
from kindearth.db.migrate import migrate
from kindearth.db.repo import Engagement, Repository
from kindearth.core.forecasting import V0ForecastEngine, ScenarioType
from kindearth.core.gates import GATE_DEFINITIONS

app = typer.Typer(add_completion=False, help="KindEarth (in-house) suite — CLI")
engagement = typer.Typer(help="Engagement operations")
forecast = typer.Typer(help="Forecasting operations")
gate = typer.Typer(help="Gate responses")
app.add_typer(engagement, name="engagement")
app.add_typer(forecast, name="forecast")
app.add_typer(gate, name="gate")


def _repo() -> Repository:
    return Repository()


def ensure_ready() -> None:
    """Prepare local folders and apply schema idempotently."""
    SETTINGS.data_dir.mkdir(parents=True, exist_ok=True)
    SETTINGS.exports_dir.mkdir(parents=True, exist_ok=True)
    migrate()


@app.command()
def init() -> None:
    """Initialize local data folders and database."""
    ensure_ready()
    print("[green]KindEarth initialized.[/green]")
    print(f"DB: {SETTINGS.db_path}")


@app.command()
def status() -> None:
    """Show current local KindEarth paths."""
    info = {
        "data_dir": str(SETTINGS.data_dir),
        "db_path": str(SETTINGS.db_path),
        "exports_dir": str(SETTINGS.exports_dir),
        "templates_dir": str(SETTINGS.templates_dir),
    }
    print(json.dumps(info, indent=2))


@engagement.command("new")
def engagement_new(
    name_arg: Optional[str] = typer.Argument(
        None, help="Engagement name (positional or use --name/-n)"
    ),
    org_arg: Optional[str] = typer.Argument(
        None, help="Organisation name (positional or use --org/-o)"
    ),
    name_opt: Optional[str] = typer.Option(
        None, "--name", "-n", help="Engagement name (alternative to positional)"
    ),
    org_opt: Optional[str] = typer.Option(
        None, "--org", "-o", help="Organisation name (alternative to positional)"
    ),
    notes: str = typer.Option("", "--notes", "-t", help="Optional notes"),
) -> None:
    """Create a new engagement (supports positional or --name/--org aliases)."""
    name = name_opt or name_arg
    org = org_opt or org_arg
    if not name or not org:
        typer.echo("Engagement name and org are required (positional or --name/--org).")
        raise typer.Exit(code=1)
    ensure_ready()
    repo = _repo()
    engagement = repo.create_engagement(name=name, org_name=org, notes=notes)
    print("[green]Engagement created.[/green]")
    print(json.dumps(engagement.__dict__, indent=2))


@engagement.command("list")
def engagement_list() -> None:
    """List engagements."""
    repo = _repo()
    engagements = repo.list_engagements()
    if not engagements:
        print("[yellow]No engagements found.[/yellow]")
        return
    table = Table(title="Engagements")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Org")
    table.add_column("Created At")
    for e in engagements:
        table.add_row(e.id, e.name, e.org_name, e.created_at)
    print(table)


@engagement.command("show")
def engagement_show(
    id: str = typer.Option(..., "--id", "-i", help="Engagement ID"),
) -> None:
    """Show a single engagement."""
    repo = _repo()
    engagement: Optional[Engagement] = repo.get_engagement(id)
    if not engagement:
        typer.echo(f"Engagement not found: {id}")
        raise typer.Exit(code=1)
    print(json.dumps(engagement.__dict__, indent=2))


@forecast.command("run")
def forecast_run(
    engagement_id: str = typer.Option(..., "--engagement-id", help="Engagement ID to forecast"),
) -> None:
    """Generate V0 forecasts for an engagement and persist them."""
    repo = _repo()
    ensure_ready()
    engagement = repo.get_engagement(engagement_id)
    if not engagement:
        typer.echo(f"Engagement not found: {engagement_id}")
        raise typer.Exit(code=1)

    engine = V0ForecastEngine()
    gates = repo.get_gate_responses(engagement_id)
    scenarios = engine.run(engagement.name, gates)
    repo.save_forecasts(engagement_id, scenarios)
    print(f"[green]{len(scenarios)} scenarios saved for engagement {engagement_id}.[/green]")


@forecast.command("show")
def forecast_show(
    engagement_id: str = typer.Option(..., "--engagement-id", help="Engagement ID to display forecasts for"),
) -> None:
    """Show stored forecasts for an engagement."""
    ensure_ready()
    repo = _repo()
    engagement = repo.get_engagement(engagement_id)
    if not engagement:
        typer.echo(f"Engagement not found: {engagement_id}")
        raise typer.Exit(code=1)

    scenarios = repo.get_forecasts(engagement_id)
    if not scenarios:
        typer.echo(f"No forecasts found for engagement: {engagement_id}")
        raise typer.Exit(code=1)

    table = Table(title=f"Forecasts for {engagement.name}")
    table.add_column("Scenario")
    table.add_column("Narrative")
    table.add_column("Indicators")
    table.add_column("Risks")
    table.add_column("Interventions")

    for scenario in scenarios:
        indicators_text = "\n".join(f"- {i.pillar}: {i.outlook}" for i in scenario.indicators)
        risks_text = "\n".join(f"- {r.pillar}: {r.likelihood}" for r in scenario.risks)
        interventions_text = "\n".join(f"- {iv.pillar}: {iv.action}" for iv in scenario.interventions)
        table.add_row(
            scenario.name.value if isinstance(scenario.name, ScenarioType) else str(scenario.name),
            scenario.narrative,
            indicators_text,
            risks_text,
            interventions_text,
        )

    print(table)


@gate.command("run")
def gate_run(
    engagement_id: str = typer.Option(..., "--engagement-id", "-e", help="Engagement ID to capture gates for"),
) -> None:
    """Collect Five Gate responses interactively and persist them."""
    ensure_ready()
    repo = _repo()
    engagement = repo.get_engagement(engagement_id)
    if not engagement:
        typer.echo(f"Engagement not found: {engagement_id}")
        raise typer.Exit(code=1)

    saved_count = 0
    typer.echo(f"Recording gates for engagement: {engagement.name}")
    for gate_def in GATE_DEFINITIONS:
        typer.echo(f"\n[{gate_def.name}] {gate_def.core_question}")
        core_answer = typer.prompt("Core answer", default="").strip()
        probes: dict[str, str] = {}
        for key, prompt_text in gate_def.required_probes.items():
            probes[key] = typer.prompt(f"{gate_def.name} — {prompt_text}", default="").strip()
        assumptions = typer.prompt("Assumptions (optional)", default="").strip()
        uncertainties = typer.prompt("Uncertainties / risks (optional)", default="").strip()
        repo.save_gate_response(
            engagement_id=engagement_id,
            gate_name=gate_def.name,
            core_answer=core_answer,
            probes=probes,
            assumptions=assumptions,
            uncertainties=uncertainties,
        )
        saved_count += 1

    print(f"[green]{saved_count} gate responses saved.[/green]")


@gate.command("show")
def gate_show(
    engagement_id: str = typer.Option(..., "--engagement-id", "-e", help="Engagement ID to display gates for"),
) -> None:
    """Show stored gate responses for an engagement."""
    ensure_ready()
    repo = _repo()
    engagement = repo.get_engagement(engagement_id)
    if not engagement:
        typer.echo(f"Engagement not found: {engagement_id}")
        raise typer.Exit(code=1)

    responses = repo.get_gate_responses(engagement_id)
    if not responses:
        typer.echo(f"No gate responses found for engagement: {engagement_id}")
        raise typer.Exit(code=1)

    table = Table(title=f"Gates for {engagement.name}")
    table.add_column("Gate")
    table.add_column("Core Answer")
    table.add_column("Probes")
    table.add_column("Assumptions")
    table.add_column("Uncertainties")
    table.add_column("Created")

    for response in responses:
        probes_text = "\n".join(f"- {k}: {v}" for k, v in response.probes.items())
        table.add_row(
            response.gate_name,
            response.core_answer or "",
            probes_text,
            response.assumptions or "",
            response.uncertainties or "",
            response.created_at,
        )

    print(table)
