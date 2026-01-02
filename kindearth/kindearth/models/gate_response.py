from typing import Dict

from pydantic import BaseModel


class GateResponseModel(BaseModel):
    id: str
    engagement_id: str
    gate_name: str
    core_answer: str
    probes: Dict[str, str]
    assumptions: str
    uncertainties: str
    created_at: str
