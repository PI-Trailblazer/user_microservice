import pytest

from app.models.user import User
from fastapi.testclient import TestClient
from app.tests.conftest import SessionTesting

test_user = {
    "uid": "test_user",
    "email": "test@email.com",
    "f_name": "Test",
    "l_name": "User",
    "phone_number": "1234567890",
    "roles": ["user"],
    "verified": True,
    "tags": ["test"],
    "image": "https://test.com/image.jpg",
}


@pytest.fixture(autouse=True)
def setup_database(db: SessionTesting):
    user = User(**test_user)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield
    db.delete(user)
    db.commit()


def test_get_user_by_id(db: SessionTesting, client: TestClient):
    response = client.get("/api/v1/user/test_user")
    assert response.status_code == 200
    assert response.json() == test_user
