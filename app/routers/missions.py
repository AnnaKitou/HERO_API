"""
Missions Router — Full CRUD for missions.

GET    /missions          → list all missions
POST   /missions          → create a new mission
GET    /missions/{id}     → get one mission
PATCH  /missions/{id}     → partial update
DELETE /missions/{id}     → delete a mission
"""

from fastapi import APIRouter, HTTPException, status

from app.dependencies import AdminUser, CurrentUser, SessionDep
from app.models.hero import Hero
from app.models.missions import Mission
from app.schemas.missions import MissionCreate, MissionOut, MissionUpdate
from sqlmodel import select

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("", response_model=list[MissionOut])
def list_missions(session: SessionDep):
    """List all missions."""
    missions = session.exec(select(Mission)).all()
    return missions


@router.post("", response_model=MissionOut, status_code=status.HTTP_201_CREATED)
def create_mission(data: MissionCreate, session: SessionDep, user: CurrentUser):
    """Create a new mission. Requires authentication."""
    # Verify hero exists
    hero = session.get(Hero, data.hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    mission = Mission(**data.model_dump())
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.get("/{mission_id}", response_model=MissionOut)
def get_mission(mission_id: int, session: SessionDep):
    """Get a single mission by ID."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mission not found")
    return mission


@router.patch("/{mission_id}", response_model=MissionOut)
def update_mission(
    mission_id: int,
    patch: MissionUpdate,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Partial update: only provided fields are changed.
    Requires authentication.
    """
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mission not found")

    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(
    mission_id: int,
    session: SessionDep,
    admin: AdminUser,
):
    """Delete a mission. Admin only."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mission not found")

    session.delete(mission)
    session.commit()
