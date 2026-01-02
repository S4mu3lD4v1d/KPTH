"""Canonical Five Gates definitions and response models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

# Gate definitions are intentionally explicit to keep the Five Gates legible and testable.


@dataclass(frozen=True)
class GateDefinition:
    name: str
    core_question: str
    required_probes: Dict[str, str]
    pillar: str


@dataclass
class GateResponse:
    id: str
    engagement_id: str
    gate_name: str
    core_answer: str
    probes: Dict[str, str]
    assumptions: str
    uncertainties: str
    created_at: str

    def has_required_fields(self, definition: GateDefinition) -> bool:
        """True when the core answer and all required probes are present."""
        if not self.core_answer or not self.core_answer.strip():
            return False
        for key in definition.required_probes:
            value = self.probes.get(key, "")
            if not value or not value.strip():
                return False
        return True


GATE_DEFINITIONS: List[GateDefinition] = [
    GateDefinition(
        name="Relational Mapping",
        pillar="Relational Accountability",
        core_question="Who is most affected by this work and how are they participating in decisions?",
        required_probes={
            "affected_partners": "Name the communities/partners most affected.",
            "consent_pathways": "How are consent and dissent heard and honored?",
            "accountability_lines": "Where do accountability and repair pathways live?",
        },
    ),
    GateDefinition(
        name="Regenerative Intent",
        pillar="Regenerative Impact",
        core_question="What regenerative outcomes are sought and how will they sustain beyond this effort?",
        required_probes={
            "intended_outcomes": "List the intended ecological/social outcomes.",
            "local_stewards": "Who holds and maintains these outcomes locally?",
            "measurement": "What measures or signals will evidence regenerative impact?",
        },
    ),
    GateDefinition(
        name="Ethical Guardrails",
        pillar="Ethical Grounding",
        core_question="What ethical boundaries prevent harm or extraction in this engagement?",
        required_probes={
            "non_negotiables": "State the non-negotiable ethical guardrails.",
            "data_practices": "How are data/knowledge handled with consent and reciprocity?",
            "appeal_path": "What is the appeal/escalation path when harm is signaled?",
        },
    ),
    GateDefinition(
        name="Stewardship Capacity",
        pillar="Practical Stewardship",
        core_question="What capacity, pacing, and resourcing exist to carry commitments responsibly?",
        required_probes={
            "resourcing": "What resourcing (people/time/funds) is secured?",
            "pace": "How will pace be managed to avoid burnout or extraction?",
            "maintenance": "What maintenance/operational plan keeps commitments alive?",
        },
    ),
    GateDefinition(
        name="Reflective Continuity",
        pillar="Reflective Continuity",
        core_question="How will learning, feedback, and repair be practiced over time?",
        required_probes={
            "feedback_loops": "What feedback loops are in place with affected partners?",
            "repair_triggers": "When do we pause or repair, and who decides?",
            "learning_cadence": "What cadence keeps reflection and adaptation on track?",
        },
    ),
]


def get_gate_definition(name: str) -> Optional[GateDefinition]:
    for gate in GATE_DEFINITIONS:
        if gate.name == name:
            return gate
    return None


def ordered_gate_names() -> List[str]:
    return [gate.name for gate in GATE_DEFINITIONS]
