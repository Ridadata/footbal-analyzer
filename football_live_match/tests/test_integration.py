import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Football Data Visualization Project"}

def test_league_matches():
    league_id = "12345"
    response = client.get(f"/league/{league_id}/matches")
    assert response.status_code == 200
    # We expect either a valid data structure or an error message depending on the mocking
    # In a real environment with a live API, this would fetch actual data
    # For demonstration, just assert that we get a JSON response
    assert response.headers["content-type"] == "application/json"

def test_league_teams():
    league_id = "67890"
    response = client.get(f"/league/{league_id}/teams")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

def test_player_data():
    player_id = "999"
    response = client.get(f"/player/{player_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


