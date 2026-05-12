"""
Heroes Router — Full CRUD for heroes.

GET    /heroes          → list all heroes (with pagination)
POST   /heroes          → create a new hero
GET    /heroes/{id}     → get one hero
PATCH  /heroes/{id}     → partial update
DELETE /heroes/{id}     → delete a hero
"""

from fastapi import APIRouter, HTTPException, status

from app.dependencies import AdminUser, CurrentUser, SessionDep
from app.models.hero import Hero
from app.models.missions import Mission
from app.schemas.hero import HeroCreate, HeroOut, HeroUpdate
from sqlmodel import select

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.get("", response_model=list[HeroOut])
def list_heroes(session: SessionDep):
    """List heroes."""
    heroes = session.exec(select(Hero)).all()
    return heroes


@router.post("", response_model=HeroOut, status_code=status.HTTP_201_CREATED)
def create_hero(data: HeroCreate, session: SessionDep, user: CurrentUser):
    """Create a new hero. Requires authentication."""
    hero = Hero(**data.model_dump())
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.get("/{hero_id}", response_model=HeroOut)
def get_hero(hero_id: int, session: SessionDep):
    """Get a single hero by ID."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )
    return hero


@router.patch("/{hero_id}", response_model=HeroOut)
def update_hero(
    hero_id: int,
    patch: HeroUpdate,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Partial update: only provided fields are changed.
    Requires authentication.
    """
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(hero, field, value)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(
    hero_id: int,
    session: SessionDep,
    admin: AdminUser,
):
    """Delete a hero. Admin only. Active missions must be completed first."""


    # Find hero
    hero = session.get(Hero, hero_id)

    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )

    # Check active missions
    active_missions = session.exec(
        select(Mission).where(
            Mission.hero_id == hero_id,
            Mission.completed == False,
        )
    ).all()

    if active_missions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot delete hero with active missions",
        )

    # Delete hero
    session.delete(hero)
    session.commit()
