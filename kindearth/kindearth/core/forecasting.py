from __future__ import annotations

from enum import Enum
from typing import Dict, List, Protocol

from pydantic import BaseModel

from kindearth.core.gates import GateResponse, GATE_DEFINITIONS
from kindearth.core.pillars import PILLARS


class ScenarioType(str, Enum):
    BASELINE = "BASELINE"
    REGENERATIVE = "REGENERATIVE"
    FAILURE = "FAILURE"


class Indicator(BaseModel):
    pillar: str
    description: str
    outlook: str


class RiskVector(BaseModel):
    pillar: str
    description: str
    likelihood: str


class Intervention(BaseModel):
    pillar: str
    action: str
    intent: str


class ForecastScenario(BaseModel):
    name: ScenarioType
    narrative: str
    indicators: List[Indicator]
    risks: List[RiskVector]
    interventions: List[Intervention]


class ForecastEngine(Protocol):
    def generate(self, engagement_name: str, gates: List[GateResponse] | None = None) -> List[ForecastScenario]:
        ...


GATE_IMPACTS: Dict[str, Dict[str, str]] = {
    "Relational Mapping": {
        "pillar": "Relational Accountability",
        "risk_vector": "relationship gaps or thin consent pathways create drift",
        "intervention": "map accountability, consent, and repair with named partners",
    },
    "Regenerative Intent": {
        "pillar": "Regenerative Impact",
        "risk_vector": "impact claims detach from regenerative anchors or local stewards",
        "intervention": "tie commitments to steward-led regenerative measures and resourcing",
    },
    "Ethical Guardrails": {
        "pillar": "Ethical Grounding",
        "risk_vector": "ethical boundaries are bypassed when pressure or ambiguity rises",
        "intervention": "publish guardrails, escalation paths, and shared stopping conditions",
    },
    "Stewardship Capacity": {
        "pillar": "Practical Stewardship",
        "risk_vector": "capacity or pacing gaps cause commitments to slip or overreach",
        "intervention": "stage delivery with resourcing checks and breathable pacing agreements",
    },
    "Reflective Continuity": {
        "pillar": "Reflective Continuity",
        "risk_vector": "learning loops stall, hiding early warnings or needed repair",
        "intervention": "protect time for reflection, publish learning cadences, and rehearse pause triggers",
    },
}


class V0ForecastEngine:
    """Conservative defaults aligned to the five pillars. Gates temper confidence and risks."""

    def run(self, engagement_name: str, gates: List[GateResponse] | None = None) -> List[ForecastScenario]:
        gates = gates or []
        gate_lookup = {gate.gate_name: gate for gate in gates}
        incomplete_gates = self._incomplete_gates(gate_lookup)
        gate_citations = self._gate_citations(gates, incomplete_gates)

        return [
            self._baseline(engagement_name, gate_lookup, incomplete_gates, gate_citations),
            self._regenerative(engagement_name, gate_lookup, incomplete_gates, gate_citations),
            self._failure(engagement_name, gate_lookup, incomplete_gates, gate_citations),
        ]

    def generate(self, engagement_name: str, gates: List[GateResponse] | None = None) -> List[ForecastScenario]:
        """Backward compatibility alias for run."""
        return self.run(engagement_name, gates)

    def _baseline(
        self,
        engagement_name: str,
        gate_lookup: Dict[str, GateResponse],
        incomplete_gates: List[str],
        gate_citations: str,
    ) -> ForecastScenario:
        narrative = (
            f"{engagement_name} maintains steady commitments to the five pillars with modest, observable progress. "
            "Stakeholders stay engaged through routine check-ins and basic stewardship practices."
        )
        narrative = self._scenario_narrative(narrative, gate_citations, incomplete_gates)
        return ForecastScenario(
            name=ScenarioType.BASELINE,
            narrative=narrative,
            indicators=self._indicators(
                "incremental practice is visible and maintained", gate_lookup, incomplete_gates
            ),
            risks=self._risks(
                "incrementalism leads to drift without periodic recalibration or shared reflection",
                gate_lookup,
                incomplete_gates,
                ScenarioType.BASELINE,
            ),
            interventions=self._interventions(
                "reinforce reliable routines and schedule reflective pauses to guard against quiet regression",
                gate_lookup,
                incomplete_gates,
            ),
        )

    def _regenerative(
        self,
        engagement_name: str,
        gate_lookup: Dict[str, GateResponse],
        incomplete_gates: List[str],
        gate_citations: str,
    ) -> ForecastScenario:
        narrative = (
            f"{engagement_name} leans into co-creation, resourcing community leadership and regenerative loops. "
            "New stewardship habits emerge that connect daily choices to longer-horizon repair."
        )
        narrative = self._scenario_narrative(narrative, gate_citations, incomplete_gates)
        return ForecastScenario(
            name=ScenarioType.REGENERATIVE,
            narrative=narrative,
            indicators=self._indicators(
                "regenerative practices are co-owned and iterated with local wisdom",
                gate_lookup,
                incomplete_gates,
            ),
            risks=self._risks(
                "ambition outpaces capacity, creating burnout or uneven benefit without deliberate pacing",
                gate_lookup,
                incomplete_gates,
                ScenarioType.REGENERATIVE,
            ),
            interventions=self._interventions(
                "sequence commitments, share decision rights transparently, and invest in care rhythms",
                gate_lookup,
                incomplete_gates,
            ),
        )

    def _failure(
        self,
        engagement_name: str,
        gate_lookup: Dict[str, GateResponse],
        incomplete_gates: List[str],
        gate_citations: str,
    ) -> ForecastScenario:
        narrative = (
            f"{engagement_name} stalls as trust thins and stewardship actions fragment. "
            "Operational shortcuts undermine ethical grounding and reflective practice."
        )
        narrative = self._scenario_narrative(narrative, gate_citations, incomplete_gates)
        return ForecastScenario(
            name=ScenarioType.FAILURE,
            narrative=narrative,
            indicators=self._indicators(
                "signals of erosion or misalignment surface without being named", gate_lookup, incomplete_gates
            ),
            risks=self._risks(
                "compounding harms arise from unaddressed power imbalances, extractive habits, or unchecked pace",
                gate_lookup,
                incomplete_gates,
                ScenarioType.FAILURE,
            ),
            interventions=self._interventions(
                "pause, repair relationships, and reset commitments with accountable checkpoints",
                gate_lookup,
                incomplete_gates,
            ),
        )

    def _scenario_narrative(
        self, base: str, gate_citations: str, incomplete_gates: List[str]
    ) -> str:
        parts = [base]
        if gate_citations:
            parts.append(f"{gate_citations}.")
        if incomplete_gates:
            parts.append(f"Gate gaps ({', '.join(incomplete_gates)}) lower confidence until addressed.")
        return " ".join(parts)

    def _indicators(
        self,
        description_suffix: str,
        gate_lookup: Dict[str, GateResponse],
        incomplete_gates: List[str],
    ) -> List[Indicator]:
        indicators: List[Indicator] = []
        for pillar in PILLARS:
            gate = self._gate_for_pillar(pillar, gate_lookup)
            gate_note = ""
            gate_name = gate.gate_name if gate else None
            if gate:
                gate_note = f" {gate_name} indicates {self._shorten(self._first_non_empty([gate.core_answer, gate.assumptions, gate.uncertainties]), 90)}"
            elif gate_name in incomplete_gates:
                gate_note = f" {gate_name} remains uncertain"

            outlook = self._outlook_for_pillar(pillar, gate_name, incomplete_gates, gate is not None)
            indicators.append(
                Indicator(
                    pillar=pillar,
                    description=f"{pillar}: {description_suffix}.{gate_note}".strip(),
                    outlook=outlook,
                )
            )
        return indicators

    def _risks(
        self,
        description_suffix: str,
        gate_lookup: Dict[str, GateResponse],
        incomplete_gates: List[str],
        scenario: ScenarioType,
    ) -> List[RiskVector]:
        risks: List[RiskVector] = []
        for pillar in PILLARS:
            likelihood = "medium" if pillar != "Regenerative Impact" else "high"
            gate = self._gate_for_pillar(pillar, gate_lookup)
            gate_name = gate.gate_name if gate else None
            gate_suffix = ""
            if gate:
                gate_suffix = f" ({gate.gate_name}: {self._shorten(self._first_non_empty([gate.core_answer, gate.uncertainties]), 90)})"
                if scenario == ScenarioType.REGENERATIVE:
                    likelihood = "medium"
            if gate_name in incomplete_gates:
                likelihood = "high"
                gate_suffix = f" ({gate_name}: missing or thin evidence)"

            risks.append(
                RiskVector(
                    pillar=pillar,
                    description=f"{pillar}: {description_suffix}.{gate_suffix}",
                    likelihood=likelihood,
                )
            )

        if incomplete_gates:
            risks.append(
                RiskVector(
                    pillar="Reflective Continuity",
                    description=f"Incomplete gates ({', '.join(incomplete_gates)}) reduce confidence in scenario integrity.",
                    likelihood="high",
                )
            )

        risks.extend(self._gate_specific_risks(gate_lookup, scenario))
        return risks

    def _interventions(
        self,
        intent_suffix: str,
        gate_lookup: Dict[str, GateResponse],
        incomplete_gates: List[str],
    ) -> List[Intervention]:
        interventions: List[Intervention] = []
        for pillar in PILLARS:
            gate = self._gate_for_pillar(pillar, gate_lookup)
            gate_name = gate.gate_name if gate else None
            action = f"{pillar}: co-create next-step practice with affected partners."
            intent = f"{intent_suffix} through {pillar.lower()}"
            if gate:
                action = f"{pillar}: co-create next-step practice with affected partners; {gate.gate_name} surfaces {self._shorten(self._first_non_empty([gate.assumptions, gate.core_answer]), 90)}."
            elif gate_name in incomplete_gates:
                action = f"{pillar}: establish a quick gate check-in; {gate_name} needs completion before escalating commitments."

            interventions.append(
                Intervention(
                    pillar=pillar,
                    action=action,
                    intent=intent,
                )
            )

        interventions.extend(self._gate_specific_interventions(gate_lookup, incomplete_gates))
        return interventions

    def _gate_for_pillar(self, pillar: str, gate_lookup: Dict[str, GateResponse]) -> GateResponse | None:
        for gate_def in GATE_DEFINITIONS:
            if gate_def.pillar == pillar:
                return gate_lookup.get(gate_def.name)
        return None

    def _incomplete_gates(self, gate_lookup: Dict[str, GateResponse]) -> List[str]:
        missing = []
        for gate_def in GATE_DEFINITIONS:
            response = gate_lookup.get(gate_def.name)
            if not response or not response.has_required_fields(gate_def):
                missing.append(gate_def.name)
        return missing

    def _gate_citations(self, gates: List[GateResponse], incomplete_gates: List[str]) -> str:
        citations = []
        for gate in gates:
            note = self._shorten(self._first_non_empty([gate.core_answer, gate.assumptions, gate.uncertainties]), 100)
            if note:
                citations.append(f"{gate.gate_name} indicates {note}")
            else:
                citations.append(f"{gate.gate_name} indicates uncertainty")
        for missing in incomplete_gates:
            if missing not in [gate.gate_name for gate in gates]:
                citations.append(f"{missing} is unaddressed")
        return "; ".join(citations)

    def _outlook_for_pillar(
        self,
        pillar: str,
        gate_name: str | None,
        incomplete_gates: List[str],
        has_gate: bool,
    ) -> str:
        baseline_outlook = "steady" if pillar in ("Practical Stewardship", "Reflective Continuity") else "emerging"
        if gate_name in incomplete_gates:
            return "uncertain"
        if has_gate:
            return "grounded"
        return baseline_outlook

    def _gate_specific_risks(
        self, gate_lookup: Dict[str, GateResponse], scenario: ScenarioType
    ) -> List[RiskVector]:
        risks: List[RiskVector] = []
        for gate_name, impact in GATE_IMPACTS.items():
            response = gate_lookup.get(gate_name)
            if not response:
                continue
            likelihood = "high" if scenario == ScenarioType.FAILURE else "medium"
            summary = self._shorten(self._first_non_empty([response.core_answer, response.uncertainties]), 100)
            risks.append(
                RiskVector(
                    pillar=impact["pillar"],
                    description=f"{impact['pillar']}: {impact['risk_vector']} ({gate_name} indicates {summary}).",
                    likelihood=likelihood,
                )
            )
        return risks

    def _gate_specific_interventions(
        self, gate_lookup: Dict[str, GateResponse], incomplete_gates: List[str]
    ) -> List[Intervention]:
        interventions: List[Intervention] = []
        for gate_name, impact in GATE_IMPACTS.items():
            response = gate_lookup.get(gate_name)
            if response:
                assumption_note = self._shorten(
                    self._first_non_empty([response.assumptions, response.core_answer, response.uncertainties]), 100
                )
                interventions.append(
                    Intervention(
                        pillar=impact["pillar"],
                        action=f"{impact['pillar']}: {impact['intervention']} ({gate_name} notes {assumption_note}).",
                        intent="stabilize commitments through gate-driven practice",
                    )
                )
            elif gate_name in incomplete_gates:
                interventions.append(
                    Intervention(
                        pillar=impact["pillar"],
                        action=f"{impact['pillar']}: complete {gate_name} to unblock confident action.",
                        intent="restore confidence through completed gate evidence",
                    )
                )
        return interventions

    def _shorten(self, text: str | None, length: int) -> str:
        if not text:
            return ""
        text = text.strip()
        if len(text) <= length:
            return text
        return text[: length - 3] + "..."

    def _first_non_empty(self, values: List[str | None]) -> str:
        for value in values:
            if value and value.strip():
                return value.strip()
        return ""
