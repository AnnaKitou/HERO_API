import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.db import get_session
from app.models.user import User
from app.models.hero import Hero
from app.models.missions import Mission
from app.security import hash_password, create_access_token


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        username="testuser",
        hashed_password=hash_password("password123"),
        is_admin=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session):
    admin = User(
        username="admin",
        hashed_password=hash_password("admin123"),
        is_admin=True,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


@pytest.fixture(name="test_hero")
def test_hero_fixture(session: Session):
    hero = Hero(
        name="Superman",
        power="Super Strength",
        level=10,
        active=True,
    )
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


# --- User Registration & Login Tests ---


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["username"] == "newuser"


def test_login_returns_token(client: TestClient, test_user: User):
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# --- Hero Creation Tests ---


def test_create_hero_requires_authentication(client: TestClient):
    response = client.post(
        "/heroes",
        json={
            "name": "Batman",
            "power": "Intelligence",
            "level": 8,
            "active": True,
        },
    )
    assert response.status_code == 401


def test_create_hero_with_token(client: TestClient, test_user: User):
    token = create_access_token("testuser")
    response = client.post(
        "/heroes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Batman",
            "power": "Intelligence",
            "level": 8,
            "active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Batman"
    assert data["power"] == "Intelligence"
    assert data["level"] == 8


# --- Mission Tests ---


def test_create_mission_for_missing_hero_returns_404(
    client: TestClient, test_user: User
):
    token = create_access_token("testuser")
    response = client.post(
        "/missions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Save the world",
            "difficulty": 5,
            "hero_id": 999,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Hero not found"


# --- Delete Tests ---


def test_normal_user_cannot_delete_hero(
    client: TestClient, test_user: User, test_hero: Hero
):
    token = create_access_token("testuser")
    response = client.delete(
        f"/heroes/{test_hero.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_admin_can_delete_mission(
    client: TestClient, admin_user: User, test_hero: Hero, session: Session
):
    mission = Mission(
        title="Complete training",
        difficulty=3,
        completed=False,
        hero_id=test_hero.id,
    )
    session.add(mission)
    session.commit()
    session.refresh(mission)

    token = create_access_token("admin")
    response = client.delete(
        f"/missions/{mission.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    deleted_mission = session.get(Mission, mission.id)
    assert deleted_mission is None
