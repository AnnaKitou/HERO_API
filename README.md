## Project Overview

HERO_API is a FastAPI application for managing heroes and missions with JWT-based authentication. It demonstrates production-ready patterns including database ORM, authentication, role-based access control (admin/user), custom exception handling, and comprehensive testing.

Stack:
- **Framework**: FastAPI 0.135.2
- **Database**: SQLite with SQLModel ORM
- **Authentication**: JWT via python-jose, password hashing with bcrypt
- **Validation**: Pydantic v2
- **Testing**: Pytest with TestClient

## Common Commands

### Development

```bash
# Start the development server (with auto-reload)
uvicorn app.main:app --reload

# Interactive API documentation
# After starting server: http://127.0.0.1:8000/docs
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_api.py

# Run a specific test function
pytest tests/test_api.py::test_register

# Run with coverage report
pytest --cov=app tests/
```

### Environment Setup

```bash
# Activate virtual environment (Windows)
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Update requirements.txt after adding dependencies
pip freeze > requirements.txt
```

## Architecture Overview

### Core Structure

The application follows FastAPI best practices with modular organization:

- **app/main.py**: FastAPI application factory. Sets up:
  - Lifespan context manager (DB table creation on startup)
  - CORS middleware (allows localhost:3000, localhost:5173)
  - Custom TimingMiddleware (adds X-Process-Time and X-Request-ID headers)
  - Exception handlers for BusinessError and RequestValidationError
  - Three routers: auth, heroes, missions

- **app/config.py**: Environment-based configuration using pydantic-settings. Settings are singleton-cached via @lru_cache. Reads from .env file with defaults:
  - `database_url`: SQLite path
  - `secret_key`: JWT signing key (MUST change in production)
  - `algorithm`: HS256 for JWT
  - `access_token_expire_minutes`: 30 min token expiry
  - `cors_origins`: frontend URLs

- **app/db.py**: Database engine and session management:
  - Uses SQLModel (SQLAlchemy hybrid with Pydantic)
  - Creates SQLite engine with check_same_thread=False for testing
  - `create_db_and_tables()`: Called on app startup via lifespan
  - `get_session()`: FastAPI dependency that yields a Session per request

### Authentication & Authorization

- **app/security.py**:
  - `hash_password()` / `verify_password()`: bcrypt-based password hashing
  - `create_access_token()`: Creates JWT with `sub` (username) and `exp` claims

- **app/dependencies.py**:
  - `SessionDep`: Annotated database session for endpoints
  - `oauth2_scheme`: OAuth2PasswordBearer for token extraction from Authorization header
  - `get_current_user()`: Decodes JWT, looks up user in DB, raises 401 if invalid
  - `CurrentUser`: Dependency for authenticated endpoints
  - `get_current_admin()`: Checks `user.is_admin`, raises 403 if not admin
  - `AdminUser`: Dependency for admin-only endpoints

- **app/routers/auth.py**:
  - `POST /auth/register`: Create new user (username "admin" gets admin=True)
  - `POST /auth/login`: OAuth2 password flow, returns JWT access_token
  - `GET /auth/me`: Current user info (requires CurrentUser)
  - `GET /auth/admin`: Admin-only endpoint (requires AdminUser)

### Data Models & Validation

- **app/models/**: SQLModel ORM models (database tables)
  - User: id, username (unique, indexed), hashed_password, is_admin
  - Hero: id, name (indexed), power, level (1-100), active
  - Mission: Similar structure for missions

- **app/schemas/**: Pydantic schemas (request/response validation)
  - Separate from models to decouple API contracts from DB schema
  - E.g., UserCreate for registration, UserOut for responses (without hashed_password)

### Exception Handling

**app/exceptions.py** defines:
- `BusinessError(code, msg)`: Custom business-logic exceptions
- `register_exception_handlers()`: Registers handlers that return clean JSON:
  - BusinessError → 422 with {code, message}
  - RequestValidationError → 400 with {error, issues[]} listing field-level errors

## Key Patterns & Conventions

### Dependency Injection
FastAPI's `Depends()` is used throughout:
- Database sessions via `SessionDep` (Annotated)
- Authentication via `CurrentUser` / `AdminUser`
- Form data via `OAuth2PasswordRequestForm`

This allows tests to override dependencies easily (see test fixtures).

### SQLModel
SQLModel unifies SQLAlchemy ORM models with Pydantic validation. Models inherit `SQLModel` and use `table=True` for ORM. Fields use `Field()` for validation (min/max length, ranges, indexing, uniqueness).

### Request/Response Separation
- Request schemas (e.g., UserCreate) define input validation
- Response schemas (e.g., UserOut) exclude sensitive fields
- Models are database schema; schemas are API contracts

### Error Responses
- Invalid input: 400 with structured validation errors
- Unauthenticated: 401 with WWW-Authenticate header
- Forbidden (non-admin): 403
- Business errors: 422 with code and message

## Testing Strategy

**tests/test_api.py** uses pytest fixtures:
- `session_fixture()`: In-memory SQLite session (no disk I/O)
- `client_fixture()`: FastAPI TestClient with dependency override
- `test_user_fixture()`: Sample test user (non-admin)
- `admin_user_fixture()`: Sample admin user

Dependency overrides ensure tests use in-memory DB, not production:
```python
app.dependency_overrides[get_session] = get_session_override
```

Tests verify endpoints, authentication, authorization, and error cases.

## Development Notes

### Adding a New Endpoint
1. Create request/response schemas in `app/schemas/`
2. Add router function in `app/routers/` using `SessionDep` / `CurrentUser` / `AdminUser` as needed
3. Add test cases to `tests/test_api.py`
4. Run `pytest -v` to verify

### Database Changes
- Modify `app/models/` (SQLModel classes)
- Tables are auto-created on app startup via `create_db_and_tables()` in lifespan
- For production migrations, implement Alembic (currently not in use)

### Environment Variables
- Create `.env` in project root with `SECRET_KEY=<real-key>`, `DATABASE_URL=sqlite:///./database.db`, etc.
- Settings are lazy-loaded and singleton-cached (see config.py)

### CORS Configuration
- Frontend URLs are whitelisted in `app.config.cors_origins`
- Add development/production URLs as needed (e.g., localhost:3000 for Next.js, localhost:5173 for Vite)
