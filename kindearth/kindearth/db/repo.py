from __future__ import annotations

import sqlite3
import uuid
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

from kindearth.config import SETTINGS
from kindearth.db.migrate import migrate
from kindearth.core.gates import GateResponse, get_gate_definition, ordered_gate_names
from kindearth.core.forecasting import ForecastScenario


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Engagement:
    id: str
    name: str
    org_name: str
    created_at: str
    notes: str = ""


class Repository:
    """Thin SQLite repository. Keeps surface small and testable."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path or SETTINGS.db_path)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def ensure_schema(self) -> None:
        migrate(self.db_path)

    # Engagements
    def create_engagement(self, name: str, org_name: str, notes: str = "") -> Engagement:
        engagement = Engagement(
            id=str(uuid.uuid4()),
            name=name,
            org_name=org_name,
            created_at=_utcnow(),
            notes=notes,
        )
        with self.connect() as con:
            con.execute(
                "INSERT INTO engagements (id, name, org_name, created_at, notes) VALUES (?, ?, ?, ?, ?)",
                (engagement.id, engagement.name, engagement.org_name, engagement.created_at, engagement.notes),
            )
            con.commit()
        return engagement

    def list_engagements(self) -> List[Engagement]:
        with self.connect() as con:
            rows = con.execute(
                "SELECT id, name, org_name, created_at, COALESCE(notes, '') AS notes FROM engagements ORDER BY created_at DESC"
            ).fetchall()
        return [Engagement(**dict(row)) for row in rows]

    def get_engagement(self, engagement_id: str) -> Optional[Engagement]:
        with self.connect() as con:
            row = con.execute(
                "SELECT id, name, org_name, created_at, COALESCE(notes, '') AS notes FROM engagements WHERE id = ?",
                (engagement_id,),
            ).fetchone()
        return Engagement(**dict(row)) if row else None

    # Forecasts
    def save_forecasts(self, engagement_id: str, scenarios: Iterable[ForecastScenario]) -> None:
        serialized = json.dumps([scenario.model_dump() for scenario in scenarios])
        with self.connect() as con:
            con.execute(
                """
                INSERT INTO forecasts (id, engagement_id, scenarios_json, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(engagement_id) DO UPDATE SET
                  scenarios_json=excluded.scenarios_json,
                  created_at=excluded.created_at
                """,
                (str(uuid.uuid4()), engagement_id, serialized, _utcnow()),
            )
            con.commit()

    def get_forecasts(self, engagement_id: str) -> Optional[List[ForecastScenario]]:
        with self.connect() as con:
            row = con.execute(
                "SELECT scenarios_json FROM forecasts WHERE engagement_id = ?",
                (engagement_id,),
            ).fetchone()
        if not row:
            return None
        data = json.loads(row["scenarios_json"])
        return [ForecastScenario.model_validate(item) for item in data]

    # Gates
    def save_gate_response(
        self,
        engagement_id: str,
        gate_name: str,
        core_answer: str,
        probes: dict,
        assumptions: str,
        uncertainties: str,
    ) -> GateResponse:
        """Persist a single gate response (creates a new record each time)."""
        response = GateResponse(
            id=str(uuid.uuid4()),
            engagement_id=engagement_id,
            gate_name=gate_name,
            core_answer=core_answer,
            probes=probes,
            assumptions=assumptions,
            uncertainties=uncertainties,
            created_at=_utcnow(),
        )
        serialized_probes = json.dumps(probes)
        with self.connect() as con:
            con.execute(
                """
                INSERT INTO gate_responses (
                    id, engagement_id, gate_name, core_answer, probes_json, assumptions, uncertainties, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response.id,
                    response.engagement_id,
                    response.gate_name,
                    response.core_answer,
                    serialized_probes,
                    response.assumptions,
                    response.uncertainties,
                    response.created_at,
                ),
            )
            con.commit()
        return response

    def get_gate_responses(self, engagement_id: str) -> List[GateResponse]:
        """Return the latest response per gate (ordered by canonical gate order)."""
        with self.connect() as con:
            rows = con.execute(
                """
                SELECT id, engagement_id, gate_name, core_answer, probes_json, assumptions, uncertainties, created_at
                FROM gate_responses
                WHERE engagement_id = ?
                ORDER BY created_at DESC
                """,
                (engagement_id,),
            ).fetchall()

        latest_by_gate: dict[str, GateResponse] = {}
        for row in rows:
            gate_name = row["gate_name"]
            if gate_name in latest_by_gate:
                continue
            latest_by_gate[gate_name] = GateResponse(
                id=row["id"],
                engagement_id=row["engagement_id"],
                gate_name=gate_name,
                core_answer=row["core_answer"],
                probes=json.loads(row["probes_json"]),
                assumptions=row["assumptions"],
                uncertainties=row["uncertainties"],
                created_at=row["created_at"],
            )

        ordered: List[GateResponse] = []
        for gate_name in ordered_gate_names():
            resp = latest_by_gate.get(gate_name)
            if resp:
                ordered.append(resp)
        for gate_name, resp in latest_by_gate.items():
            if gate_name not in ordered_gate_names():
                ordered.append(resp)
        return ordered
