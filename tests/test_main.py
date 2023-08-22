import json
import pytest
from api.service import UserService, TaggedLinkService


def test_ping(test_app):
    response = test_app.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong pong"}

# let's have some fun with pytest fixtures
# https://docs.pytest.org/en/stable/fixture.html
# https://fastapi.tiangolo.com/tutorial/testing/
# https://fastapi.tiangolo.com/advanced/testing-dependencies/
# https://fastapi.tiangolo.com/advanced/async-tests/
# https://fastapi.tiangolo.com/advanced/async-sql-databases/
# https://fastapi.tiangolo.com/advanced/async-sql-databases/#create-a-dependency

# let's have a default user for testing


@pytest.fixture
def default_user():
    return {
        "_id": 1,
        "email": "demo@mail.com",
        "is_active": True,
        "links": []
    }


@pytest.fixture
def default_user_email():
    return "demo@mail.com"

# Let's test the user endpoints:

# POST /users/
# Let's create a valid user


def test_create_user(test_app, monkeypatch, default_user):
    test_request_payload = {"email": "demo@mail.com", "password": "demo"}
    test_response_payload = default_user

    def mock_get_user_by_email(self, db, email):
        return None

    def mock_create_user(self, db, user):
        return default_user

    monkeypatch.setattr(UserService, "get_user_by_email",
                        mock_get_user_by_email)
    monkeypatch.setattr(UserService, "create_user", mock_create_user)

    response = test_app.post("/users/", data=json.dumps(test_request_payload))
    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_user_existing_email(test_app, monkeypatch, default_user, default_user_email):
    test_request_payload = {"email": default_user_email, "password": "demo"}
    test_response_payload = {"detail": "Email already registered"}

    async def mock_post(self, db, email):
        return default_user

    monkeypatch.setattr(UserService, "get_user_by_email", mock_post)
    response = test_app.post("/users/", data=json.dumps(test_request_payload))
    assert response.status_code == 400
    assert response.json() == test_response_payload

# GET /users/
# GET /users/{user_id}
# POST /users/{user_id}/links/
# GET /users/{user_id}/links/
