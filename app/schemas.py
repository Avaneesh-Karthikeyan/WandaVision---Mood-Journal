from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


MoodTag = Literal["happy", "sad", "anxious", "stressed", "neutral", "angry", "excited", "grateful", "overwhelmed", "calm"]


class JournalEntryCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Your journal entry text")

    model_config = {"json_schema_extra": {"example": {"text": "Today was a great day! I finished my project and felt really proud of myself."}}}


class JournalEntryResponse(BaseModel):
    id: int
    text: str
    mood: str
    reflection: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    message: str
