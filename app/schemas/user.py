from sqlmodel import SQLModel, Field


# USER MODELS

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_admin: bool

