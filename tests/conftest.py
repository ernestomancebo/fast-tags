import pytest
from starlette.testclient import TestClient

from api.main import app

# let's have some fun with pytest fixtures
# https://docs.pytest.org/en/stable/fixture.html
# https://fastapi.tiangolo.com/tutorial/testing/
# https://fastapi.tiangolo.com/advanced/testing-dependencies/
# https://fastapi.tiangolo.com/advanced/async-tests/
# https://fastapi.tiangolo.com/advanced/async-sql-databases/
# https://fastapi.tiangolo.com/advanced/async-sql-databases/#create-a-dependency


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture
def default_user():
    """Default user for testing"""
    return {
        "_id": 1,
        "email": "demo@mail.com",
        "is_active": True,
        "links": []
    }


@pytest.fixture
def default_user_email():
    """Default user email for testing"""
    return "demo@mail.com"


@pytest.fixture
def default_tagged_link():
    """Default tagged link for testing"""
    return {"_id": 1,
            "url": "https://www.google.com",
            "tags": ["google"],
            "owner_id": 1}


@pytest.fixture
def default_tagged_link_url():
    """Default tagged link url for testing"""
    return "https://www.google.com"


@pytest.fixture
def default_tagged_link_list():
    """List of default tagged links for testing"""
    return [{"_id": 1, "url": "https://www.google.com", "tags": ["google"], "owner_id": 1},
            {"_id": 2, "url": "https://www.yahoo.com", "tags": ["yahoo"], "owner_id": 1},]
