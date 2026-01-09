from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class EventInfo(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None  # Formato YYYY-MM-DD
    location: Optional[str] = None

class MusicProfile(BaseModel):
    genre: Optional[str] = None
    artists: List[str] = []
    location: Optional[str] = None
    budget: Optional[float] = None

class AgentState(TypedDict):
    messages: Annotated[List[str], "History"]
    profile: MusicProfile
    results: List[str]
    final_response: str
    event_details: Optional[EventInfo] # Per l'azione di scrittura