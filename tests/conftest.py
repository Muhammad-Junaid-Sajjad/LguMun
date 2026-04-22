import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import INET
from app.database import Base, get_db
from app.main import app
from app.models import Committee, Delegate

# Override INET type for SQLite compatibility
import sqlalchemy.dialects.postgresql as postgresql_dialect
original_inet = postgresql_dialect.INET

class TestINET(String):
    pass

postgresql_dialect.INET = TestINET

# SQLite in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Disable rate limiting for tests
    app.state.limiter.enabled = False

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    app.state.limiter.enabled = True

@pytest.fixture
def test_committee(db_session):
    committee = Committee(
        short_name="TEST",
        full_name="Test Committee",
        total_seats=5,
        filled_seats=0,
        last_sequence=0,
        is_active=True
    )
    db_session.add(committee)
    db_session.commit()
    db_session.refresh(committee)
    return committee

@pytest.fixture
def full_committee(db_session):
    committee = Committee(
        short_name="FULL",
        full_name="Full Committee",
        total_seats=5,
        filled_seats=5,
        last_sequence=5,
        is_active=True
    )
    db_session.add(committee)
    db_session.commit()
    db_session.refresh(committee)
    return committee
