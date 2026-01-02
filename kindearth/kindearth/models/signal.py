from pydantic import BaseModel


class SignalModel(BaseModel):
    id: str
    recommendation_id: str
    signal: str  # GREEN, AMBER, RED
    rationale: str
    created_at: str
