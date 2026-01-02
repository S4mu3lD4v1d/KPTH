from pydantic import BaseModel


class RecommendationModel(BaseModel):
    id: str
    engagement_id: str
    title: str
    created_at: str
