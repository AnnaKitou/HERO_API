from sqlmodel import SQLModel, Field


class Mission(SQLModel, table=True):
    """Mission database model."""

    id: int | None = Field(default=None, primary_key=True)

    title: str = Field(
        min_length=5,
        max_length=200
    )

    difficulty: int = Field(
        ge=1,
        le=10
    )

    completed: bool = False

    hero_id: int = Field(foreign_key="hero.id")
