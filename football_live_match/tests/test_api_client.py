import pytest
from unittest.mock import patch, MagicMock
from src.api_client import get_matches, get_teams, get_player

@pytest.mark.parametrize("league_id", ["12345", "67890"])
def test_get_matches(league_id):
    with patch("src.api_client.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"matches": [{"match_id": 1}, {"match_id": 2}]}
        mock_get.return_value = mock_response

        result = get_matches(league_id)
        assert result is not None
        assert len(result["matches"]) == 2

@pytest.mark.parametrize("league_id", ["abc", "def"])
def test_get_teams(league_id):
    with patch("src.api_client.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"teams": [{"team_id": 10}, {"team_id": 20}]}
        mock_get.return_value = mock_response

        result = get_teams(league_id)
        assert result is not None
        assert len(result["teams"]) == 2

@pytest.mark.parametrize("player_id", ["999", "111"])
def test_get_player(player_id):
    with patch("src.api_client.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"player": {"id": 999, "name": "Test Player"}}
        mock_get.return_value = mock_response

        result = get_player(player_id)
        assert result is not None
        assert "player" in result
        assert result["player"]["id"] == 999
        assert result["player"]["name"] == "Test Player"
