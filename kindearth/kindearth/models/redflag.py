from pydantic import BaseModel


class RedFlagModel(BaseModel):
    id: str
    engagement_id: str
    category: str
    description: str
    escalation_note: str
    created_at: str
