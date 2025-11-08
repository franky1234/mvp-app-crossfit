from pydantic import BaseModel
from typing import List, Optional, Union

class Exercise(BaseModel):
    name: str
    sets: int
    reps_or_time: Union[str, int]
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
    warmup: List[Union[str, dict]]
    exercises: List[Exercise]
    cooldown: List[Union[str, dict]]
    modifications: dict
    raw_text: Optional[str] = None
