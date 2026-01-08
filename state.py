from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class MusicProfile(BaseModel):
    genre: Optional[str] = Field(None, description="Genere musicale")
    artists: List[str] = Field(default_factory=list, description="Artisti preferiti")
    location: Optional[str] = Field(None, description="Città")

class AgentState(TypedDict):
    messages: Annotated[List[str], "History"]
    profile: MusicProfile
    results: List[str]
    final_response: str  # Campo per la risposta elaborata