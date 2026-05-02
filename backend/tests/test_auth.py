import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
import jwt
from unittest.mock import patch, MagicMock

from app.main import app
from app.auth.jwt import create_access_token, ALGORITHM, SECRET_KEY
from app.auth.models import User

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        is_active=True
    )

@pytest.fixture
def valid_token(mock_user):
    return create_access_token(
        data={"sub": mock_user.email},
        expires_delta=timedelta(minutes=30)
    )

def test_login_success(mock_user):
    with patch("app.auth.jwt.authenticate_user", return_value=mock_user):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "password"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials():
    with patch("app.auth.jwt.authenticate_user", return_value=False):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Incorrect email or password"}

def test_get_current_user_valid_token(valid_token, mock_user):
    with patch("app.auth.jwt.get_user_by_email", return_value=mock_user):
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == mock_user.email
        assert response.json()["username"] == mock_user.username

def test_get_current_user_invalid_token():
    invalid_token = "invalid_token"
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

def test_get_current_user_expired_token(mock_user):
    # Create an expired token
    expired_token = create_access_token(
        data={"sub": mock_user.email},
        expires_delta=timedelta(minutes=-30)  # Negative to make it expired
    )
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_register_user_success():
    with patch("app.auth.routes.get_user_by_email", return_value=None), \
         patch("app.auth.routes.create_user", return_value=MagicMock(id=1, email="new@example.com")):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "strongpassword123"
            }
        )
        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["email"] == "new@example.com"

def test_register_user_existing_email():
    with patch("app.auth.routes.get_user_by_email", return_value=MagicMock()):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "username": "existinguser",
                "password": "strongpassword123"
            }
        )
        assert response.status_code == 400
        assert "detail" in response.json()