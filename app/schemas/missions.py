from pydantic import BaseModel, Field

class MissionCreate(BaseModel):
    """Schema for creating a mission."""
    title: str = Field(min_length=5, max_length=200)
    difficulty: int = Field(ge=1, le=10)
    hero_id: int


class MissionUpdate(BaseModel):
    """Schema for updating a mission."""
    title: str | None = Field(default=None, min_length=5, max_length=200)
    difficulty: int | None = Field(default=None, ge=1, le=10)
    completed: bool | None = None


class MissionOut(BaseModel):
    """Schema returned to clients."""
    id: int
    title: str
    difficulty: int
    completed: bool
    hero_id: int
