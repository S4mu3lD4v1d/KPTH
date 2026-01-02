# KindEarth CLI (in-house)

CLI for the KindEarth consulting operating system. Designed to stay internal and aligned with the KindEarth pillars, gates, red flags, and signals.

## Quick start

```bash
cd kindearth
poetry install
poetry run kindearth init
poetry run kindearth status
poetry run kindearth engagement new --name "Pilot" --org "KindPath Collective"
```

## Commands (initial)
- `kindearth init` — create data directories and migrate SQLite schema.
- `kindearth status` — show current paths.
- `kindearth engagement new --name ... --org ...` — create an engagement (uses SQLite).
- `kindearth engagement list` — list engagements.
- `kindearth engagement show --id ...` — show an engagement record.

More commands (gates, red flags, signals, forecasting, compose) land next; AGENTS.md defines guardrails.
