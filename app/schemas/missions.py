from sqlmodel import SQLModel, Field
 
# MISSION MODELS

class MissionBase(SQLModel):
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False


class Mission(MissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hero_id: int = Field(foreign_key="hero.id")


class MissionCreate(MissionBase):
    hero_id: int


class MissionUpdate(SQLModel):
    title: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=10)
    completed: bool | None = None


class MissionRead(MissionBase):
    id: int
    hero_id: int