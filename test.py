# pip install pytest mongomock flask-testing

import os
import pytest
from app import app as flask_app
from app import db
from flask import session
from bson import ObjectId
import mongomock
from datetime import datetime

# Mock database setup (optional if needed for better isolation)
@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    # Replace the db object with a mongomock version
    mock_client = mongomock.MongoClient()
    mock_db = mock_client['CodeShadow']
    monkeypatch.setattr('app.db', mock_db)
    return mock_db

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

# --------- ROUTE TESTS ---------

def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sign Up" in response.data  # assuming signup page has "Sign Up" text

def test_signup_and_login(client, mock_db):
    # 1. Signup new user
    signup_data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com"
    }
    response = client.post("/signup", data=signup_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data or b"Dashboard" in response.data

    # Confirm user is inserted
    user = mock_db.users.find_one({"username": "testuser"})
    assert user is not None
    assert user["email"] == "test@example.com"

    # 2. Try to login with correct credentials
    login_data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com"
    }
    response = client.post("/login", data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_login_failures(client, mock_db):
    # Insert a user
    mock_db.users.insert_one({
        "username": "fakeuser",
        "password": "fakepass",
        "email": "fake@example.com"
    })

    # Wrong password
    response = client.post("/login", data={
        "username": "fakeuser",
        "password": "wrongpass",
        "email": "fake@example.com"
    })
    assert b"Incorrect password" in response.data

    # Wrong email
    response = client.post("/login", data={
        "username": "fakeuser",
        "password": "fakepass",
        "email": "wrong@example.com"
    })
    assert b"Incorrect email" in response.data

    # User not found
    response = client.post("/login", data={
        "username": "nouser",
        "password": "whatever",
        "email": "whatever@example.com"
    })
    assert b"User not found" in response.data

def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=True)
    assert b"Login" in response.data

def test_logout(client, mock_db):
    # Simulate a user session
    user = mock_db.users.insert_one({
        "username": "logoutuser",
        "password": "pass",
        "email": "logout@example.com"
    })
    with client.session_transaction() as sess:
        sess['user_id'] = str(user.inserted_id)

    # Now logout
    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

# --------- LOGGING ENTRIES TESTS ---------

def test_sleep_log(client, mock_db):
    # Insert user and login
    user = mock_db.users.insert_one({
        "username": "sleepuser",
        "password": "pass",
        "email": "sleep@example.com"
    })
    with client.session_transaction() as sess:
        sess['user_id'] = str(user.inserted_id)

    sleep_data = {
        "hours_slept": "8",
        "sleep_notes": "Good sleep",
        "sleep_quality": "High",
        "date": "2025-04-24"
    }
    response = client.post("/log/sleep", data=sleep_data, follow_redirects=True)
    assert response.status_code == 200
    logs = list(mock_db.sleep_logs.find({"user_id": user.inserted_id}))
    assert len(logs) == 1
    assert logs[0]["hours_slept"] == 8

def test_nutrition_log(client, mock_db):
    user = mock_db.users.insert_one({
        "username": "nutritionuser",
        "password": "pass",
        "email": "nutrition@example.com"
    })
    with client.session_transaction() as sess:
        sess['user_id'] = str(user.inserted_id)

    nutrition_data = {
        "carbs": "100",
        "fats": "40",
        "proteins": "60",
        "date": "2025-04-24"
    }
    response = client.post("/log/nutrition", data=nutrition_data, follow_redirects=True)
    assert response.status_code == 200
    logs = list(mock_db.nutrition_logs.find({"user_id": user.inserted_id}))
    assert len(logs) == 1
    assert logs[0]["balanced"] is True

def test_exercise_log(client, mock_db):
    user = mock_db.users.insert_one({
        "username": "exerciseuser",
        "password": "pass",
        "email": "exercise@example.com"
    })
    with client.session_transaction() as sess:
        sess['user_id'] = str(user.inserted_id)

    exercise_data = {
        "exercise_type": "Running",
        "duration": "30",
        "date": "2025-04-24"
    }
    response = client.post("/log/exercise", data=exercise_data, follow_redirects=True)
    assert response.status_code == 200
    logs = list(mock_db.exercise_logs.find({"user_id": user.inserted_id}))
    assert len(logs) == 1
    assert logs[0]["exercise_type"] == "Running"

# --------- ACTIVITY FEED TESTS ---------

def test_activity_feed(client, mock_db):
    user = mock_db.users.insert_one({
        "username": "feeduser",
        "password": "pass",
        "email": "feed@example.com"
    })
    with client.session_transaction() as sess:
        sess['user_id'] = str(user.inserted_id)

    mock_db.sleep_logs.insert_one({
        "user_id": user.inserted_id,
        "hours_slept": 7,
        "date": "2025-04-23",
        "timestamp": datetime.now()
    })
    mock_db.nutrition_logs.insert_one({
        "user_id": user.inserted_id,
        "carbs": 50,
        "fats": 30,
        "proteins": 20,
        "date": "2025-04-23",
        "timestamp": datetime.now()
    })
    mock_db.exercise_logs.insert_one({
        "user_id": user.inserted_id,
        "exercise_type": "Cycling",
        "duration": 45,
        "date": "2025-04-23",
        "timestamp": datetime.now()
    })

    response = client.get("/activity_feed")
    assert response.status_code == 200
    assert b"Sleep" in response.data
    assert b"Nutrition" in response.data
    assert b"Exercise" in response.data
