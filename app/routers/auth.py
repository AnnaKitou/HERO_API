from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.dependencies import CurrentUser, SessionDep
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/register")
def register(data: UserCreate, session: SessionDep):
    """Register a new user. Username 'admin' gets admin rights."""
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(400, "Username already taken")
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        is_admin=(data.username == "admin"),
    )
    session.add(user)
    session.commit()
    return {"ok": True, "username": user.username}


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    """Validate credentials and return an access token."""
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
    }


@router.get("/me")
def me(user: CurrentUser):
    """Return the current user's info. Requires authentication."""
    return {"username": user.username, "is_admin": user.is_admin}


@router.get("/admin")
def admin_only(user: CurrentUser):
    """Admin-only endpoint. Raises 403 for non-admin users."""
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only")
    return {"secret": "42", "message": f"Welcome, admin {user.username}!"}
