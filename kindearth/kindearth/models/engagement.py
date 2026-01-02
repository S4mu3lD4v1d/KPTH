from pydantic import BaseModel


class EngagementModel(BaseModel):
    id: str
    name: str
    org_name: str
    created_at: str
    notes: str = ""
