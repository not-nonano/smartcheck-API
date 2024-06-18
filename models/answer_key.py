from pydantic import BaseModel, Field
from typing import List, Optional

class Answer_Key(BaseModel):
    id: str 
    english: List[str]
    science: List[str]
    mathematics: List[str]
    aptitude: List[str]
    date: float

class Post_Answer_Key(BaseModel):
    status: int = Field(..., description="The HTTP status code of the response")
    message: Optional[str] = Field(None, description="The response message")
