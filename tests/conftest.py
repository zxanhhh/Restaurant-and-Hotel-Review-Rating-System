import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from db.models import Base, Category
from db.database import CATEGORY_SEED
from api.app import app
from api.deps import get_db

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture(scope="function")
def db_session(engine):
    connection  = engine.connect()
    transaction = connection.begin()
    Session     = sessionmaker(bind=connection)
    session     = Session()

    for name, desc in CATEGORY_SEED:
        if not session.query(Category).filter_by(name=name).first():
            session.add(Category(name=name, description=desc))
    session.flush()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def api_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
