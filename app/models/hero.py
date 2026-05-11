from sqlmodel import SQLModel, Field


class Hero(SQLModel, table=True):
    """Hero database model."""

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(
        index=True,
        min_length=3,
        max_length=100
    )

    power: str = Field(
        min_length=3,
        max_length=100
    )

    level: int = Field(
        default=1,
        ge=1,
        le=100
    )

    active: bool = True