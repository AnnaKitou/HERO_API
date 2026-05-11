from pydantic import BaseModel, Field


class HeroCreate(BaseModel):
    """Schema for creating a hero."""

    name: str = Field(min_length=3, max_length=100)
    power: str = Field(min_length=3, max_length=100)
    level: int = Field(default=1, ge=1, le=100)
    active: bool = True


class HeroUpdate(BaseModel):
    """Schema for updating a hero."""

    name: str | None = Field(default=None, min_length=3, max_length=100)
    power: str | None = Field(default=None, min_length=3, max_length=100)
    level: int | None = Field(default=None, ge=1, le=100)
    active: bool | None = None


class HeroOut(BaseModel):
    """Schema returned to clients."""

    id: int
    name: str
    power: str
    level: int
    active: bool