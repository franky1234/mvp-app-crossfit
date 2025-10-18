from pydantic import BaseModel
from typing import List, Optional

class Exercise(BaseModel):
    name: str
    sets: int
    reps_or_time: str
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None

class RoutineRequest(BaseModel):
    level: str
    duration_minutes: int
    goals: str

class RoutineResponse(BaseModel):
    title: str
    duration_minutes: int
    level: str
    warmup: List[str]
    exercises: List[Exercise]
    cooldown: List[str]
    modifications: dict
    raw_text: Optional[str] = None
