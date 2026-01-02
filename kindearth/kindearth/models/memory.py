from typing import List

from pydantic import BaseModel


class MemoryEntryModel(BaseModel):
    id: str
    engagement_id: str
    tags: List[str]
    content: str
    created_at: str
