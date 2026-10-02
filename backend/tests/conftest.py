import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_expense_tracker.db"
os.environ["JWT_SECRET"] = "test-secret-with-enough-entropy-for-tests"
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    response = client.post(
        "/v1/auth/register",
        json={"email": "test@example.com", "password": "StrongPass123!", "display_name": "Tester", "base_currency": "UZS"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]
