import json

from api.service import TaggedLinkService, UserService

from starlette.testclient import TestClient


def test_ping(test_app):
    response = test_app.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong pong"}


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


def test_create_user_existing_email(test_app, monkeypatch, default_user,
                                    default_user_email):
    test_request_payload = {"email": default_user_email, "password": "demo"}
    test_response_payload = {
        "detail": f"Email '{default_user_email}' already registered"}

    def mock_post(self, db, email):
        return default_user

    monkeypatch.setattr(UserService, "get_user_by_email", mock_post)
    response = test_app.post("/users/", data=json.dumps(test_request_payload))
    assert response.status_code == 400
    assert response.json() == test_response_payload


def test_create_user_bad_input(test_app, monkeypatch):
    test_request_payload = {"email1": "email@mail.com"}
    response = test_app.post("/users/", data=json.dumps(test_request_payload))
    assert response.status_code == 422


# GET /users/
def test_read_users(test_app, monkeypatch, default_user):
    """Gets all users endpoint"""
    test_data = [default_user]

    def mock_get_users(self, db, skip, limit):
        return test_data

    monkeypatch.setattr(UserService, "get_users", mock_get_users)

    response = test_app.get("/users/")
    assert response.status_code == 200
    assert response.json() == test_data

# GET /users/{user_id}


def test_read_user(test_app, monkeypatch, default_user):
    """Get user by id endpoint"""
    test_data = default_user

    def mock_get_user(self, db, user_id):
        return test_data

    monkeypatch.setattr(UserService, "get_user", mock_get_user)

    response = test_app.get("/users/1")
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_user_404(test_app, monkeypatch):
    """Get user by id endpoint"""

    def mock_get_user(self, db, user_id):
        return None

    monkeypatch.setattr(UserService, "get_user", mock_get_user)

    response = test_app.get("/users/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

# POST /users/{user_id}/links/


def test_create_link(test_app, monkeypatch, default_tagged_link):
    """Create link endpoint"""
    test_request_payload = {
        "url": "https://www.google.com", "tags": ["search", "engine"]}
    test_response_payload = default_tagged_link

    def mock_create_user_tagged_link(self, db, tagged_link, user_id):
        return default_tagged_link

    monkeypatch.setattr(
        TaggedLinkService, "create_user_tagged_link", mock_create_user_tagged_link)

    response = test_app.post(
        "/users/1/links/", data=json.dumps(test_request_payload))
    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_link_no_url(test_app):
    """Tries to create link without user_id"""
    test_request_payload = {"tags": ["search", "engine"]}
    response = test_app.post(
        "/users/1/links/", data=json.dumps(test_request_payload))
    # invalid input requests
    assert response.status_code == 422

# PUT /links/{link_id}


def test_update_link(test_app, monkeypatch, default_tagged_link):
    test_request_payload = {"_id": 1, "tags": [
        "search", "engine", "google"], "owner_id": 1}
    test_response_payload = default_tagged_link.copy()
    test_response_payload["tags"] = test_request_payload["tags"]

    def mock_update_user_tagged_link(self, db, tagged_link):
        return test_response_payload

    monkeypatch.setattr(
        TaggedLinkService, "update_user_tagged_link", mock_update_user_tagged_link)
    response = test_app.put("/links/1", data=json.dumps(test_request_payload))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_update_link_404(test_app, monkeypatch):
    test_request_payload = {"_id": 1, "tags": ["search", "engine", "google"]}
    test_response_payload = {"detail": "Tagged link not found"}

    def mock_update_user_tagged_link(self, db, tagged_link):
        return None

    monkeypatch.setattr(
        TaggedLinkService, "update_user_tagged_link", mock_update_user_tagged_link)
    response = test_app.put("/links/1", data=json.dumps(test_request_payload))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_update_link_no_id(test_app):
    test_request_payload = {"tags": ["search", "engine", "google"]}
    response = test_app.put("/links/1", data=json.dumps(test_request_payload))
    assert response.status_code == 422

# DELETE /links/{link_id}


def test_delete_link(test_app, monkeypatch, default_tagged_link):
    test_request_payload = {"_id": 1, "tags": ["search", "engine", "google"]}

    def mock_delete_user_tagged_link(self, db, tagged_link_id):
        return True

    monkeypatch.setattr(
        TaggedLinkService, "delete_user_tagged_link", mock_delete_user_tagged_link)
    response = test_app.delete("/links/1")
    assert response.status_code == 204


def test_delete_link_404(test_app: TestClient, monkeypatch):
    test_response_payload = {"detail": "Tagged link not found"}

    def mock_delete_user_tagged_link(self, db, tagged_link_id):
        return False

    monkeypatch.setattr(
        TaggedLinkService, "delete_user_tagged_link", mock_delete_user_tagged_link)
    response = test_app.delete("/links/1")
    assert response.status_code == 404
    assert response.json() == test_response_payload

# GET /links/


def test_get_links(test_app, monkeypatch,  default_tagged_link_list):
    """Pulls all links"""
    test_data = default_tagged_link_list

    def mock_get_links(self, db, skip, limit):
        return test_data

    monkeypatch.setattr(TaggedLinkService, "get_tagged_links", mock_get_links)

    response = test_app.get("/links/")
    assert response.status_code == 200
    assert response.json() == test_data
