from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for creating a user."""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: str | None = Field(default=None, min_length=3, max_length=50)
    password: str | None = Field(default=None, min_length=6)
    is_admin: bool | None = None


class UserOut(BaseModel):
    """Schema returned to clients."""
    id: int
    username: str
    is_admin: bool
