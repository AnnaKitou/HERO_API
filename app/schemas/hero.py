from sqlmodel import SQLModel, Field

# HERO MODELS

class HeroBase(SQLModel):
    name: str = Field(min_length=3, max_length=100)
    power: str = Field(min_length=3, max_length=100)
    level: int = Field(default=1, ge=1, le=100)
    active: bool = True


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class HeroCreate(HeroBase):
    pass


class HeroUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=3)
    power: str | None = Field(default=None, min_length=3)
    level: int | None = Field(default=None, ge=1, le=100)
    active: bool | None = None


class HeroRead(HeroBase):
    id: int


