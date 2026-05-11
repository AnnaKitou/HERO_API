from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User database model."""

    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(
        index=True,
        unique=True,
        min_length=3,
        max_length=50
    )

    hashed_password: str

    is_admin: bool = False
