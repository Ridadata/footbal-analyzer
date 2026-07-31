"""
Data processing utilities for formatting API responses for frontend visualization.
These utilities transform raw API responses into the structures
our templates and charts expect.
"""

def process_match_data(raw_data):
    """
    Takes raw match data from the API and returns a list of dictionaries
    suitable for table rendering or chart generation.

    Expected input format from the football API:
    {
      "response": [
        {
          "fixture": {
            "id": 123,
            "date": "2023-04-15T14:00:00+00:00",
            "status": { "short": "FT", "long": "Match Finished" }
          },
          "league": {
            "id": 39,
            "name": "Premier League",
            "country": "England"
          },
          "teams": {
            "home": { "id": 33, "name": "Manchester United", "logo": "https://..." },
            "away": { "id": 34, "name": "Newcastle", "logo": "https://..." }
          },
          "goals": {
            "home": 2,
            "away": 1
          },
          "score": {
            "halftime": { "home": 1, "away": 0 },
            "fulltime": { "home": 2, "away": 1 }
          }
        },
        ...
      ]
    }

    Returned output (example):
    [
      {
        "match_id": 123,
        "league_id": 39,
        "league_name": "Premier League",
        "home_team": "Manchester United",
        "away_team": "Newcastle",
        "home_logo": "https://...",
        "away_logo": "https://...",
        "score_home": 2,
        "score_away": 1,
        "status": "Match Finished",
        "status_short": "FT",
        "date": "2023-04-15T14:00:00+00:00",
        "halftime_score": "1-0"
      },
      ...
    ]
    """
    if not raw_data:
        return []

    # Football API structure
    matches = raw_data.get("response", [])
    if not matches:
        return []

    formatted_matches = []
    for match in matches:
        fixture = match.get("fixture", {})
        league = match.get("league", {})
        teams = match.get("teams", {})
        goals = match.get("goals", {})
        score = match.get("score", {})

        home_team = teams.get("home", {})
        away_team = teams.get("away", {})
        status = fixture.get("status", {})

        halftime = score.get("halftime", {})
        halftime_score = f"{halftime.get('home', 0)}-{halftime.get('away', 0)}"

        formatted_match = {
            "match_id": fixture.get("id"),
            "league_id": league.get("id"),
            "league_name": league.get("name"),
            "league_country": league.get("country"),
            "home_team": home_team.get("name"),
            "away_team": away_team.get("name"),
            "home_logo": home_team.get("logo"),
            "away_logo": away_team.get("logo"),
            "score_home": goals.get("home"),
            "score_away": goals.get("away"),
            "status": status.get("long"),
            "status_short": status.get("short"),
            "date": fixture.get("date"),
            "halftime_score": halftime_score
        }
        print(f"Formatted match: {formatted_match}")  # Debug print
        formatted_matches.append(formatted_match)

    return formatted_matches


def process_team_data(raw_data):
    """
    Takes raw team data from the API and returns a list of dictionaries
    for table rendering or chart generation.
    """
    if not raw_data:
        return []

    teams = raw_data.get("teams")
    if teams is None:
        return []

    formatted_teams = []
    for team in teams:
        formatted_team = {
            "team_id": team.get("team_id"),
            "team_name": team.get("team_name"),
            "wins": team.get("wins"),
            "losses": team.get("losses"),
            "draws": team.get("draws")
        }
        formatted_teams.append(formatted_team)

    return formatted_teams


def process_player_data(raw_data):
    """
    Takes raw player data from the API and returns a dictionary with key details.
    """
    if not raw_data:
        return {}

    # Depending on actual data format
    player_info = raw_data.get("player", {})
    formatted_player = {
        "player_id": player_info.get("id"),
        "player_name": player_info.get("name"),
        "position": player_info.get("position"),
        "goals": player_info.get("goals"),
        "assists": player_info.get("assists"),
        "appearances": player_info.get("appearances"),
        # etc.
    }
    return formatted_player


def process_live_matches(raw_data):
    """
    Process live match data specifically.
    This is similar to process_match_data but focuses on live matches.

    Returns a list of dictionaries with live match information.
    """
    matches = process_match_data(raw_data)

    # Filter to only include matches that are live
    live_statuses = ['1H', '2H', 'HT', 'ET', 'P', 'BT', 'LIVE']
    live_matches = [match for match in matches if match.get('status_short') in live_statuses]

    return live_matches


def process_match_statistics(raw_data):
    """
    Process match statistics data.

    Expected input format:
    {
      "response": [
        {
          "team": {
            "id": 33,
            "name": "Manchester United",
            "logo": "https://..."
          },
          "statistics": [
            {
              "type": "Shots on Goal",
              "value": 5
            },
            {
              "type": "Shots off Goal",
              "value": 7
            },
            ...
          ]
        },
        {
          "team": {
            "id": 34,
            "name": "Newcastle",
            "logo": "https://..."
          },
          "statistics": [
            ...
          ]
        }
      ]
    }

    Returns a dictionary with team statistics organized by team.
    """
    if not raw_data:
        return {}

    teams_stats = raw_data.get("response", [])
    if not teams_stats:
        return {}

    result = {}

    for team_data in teams_stats:
        team = team_data.get("team", {})
        team_id = team.get("id")
        team_name = team.get("name")

        if not team_id or not team_name:
            continue

        stats = {}
        for stat in team_data.get("statistics", []):
            stat_type = stat.get("type")
            stat_value = stat.get("value")

            # Convert percentage strings to numbers
            if isinstance(stat_value, str) and '%' in stat_value:
                try:
                    stat_value = float(stat_value.strip('%'))
                except ValueError:
                    pass

            stats[stat_type] = stat_value

        result[team_name] = {
            "team_id": team_id,
            "team_name": team_name,
            "logo": team.get("logo"),
            "statistics": stats
        }

    return result


def process_match_events(raw_data):
    """
    Process match events data (goals, cards, substitutions, etc.)

    Expected input format:
    {
      "response": [
        {
          "time": {
            "elapsed": 23,
            "extra": null
          },
          "team": {
            "id": 33,
            "name": "Manchester United",
            "logo": "https://..."
          },
          "player": {
            "id": 153,
            "name": "Marcus Rashford"
          },
          "type": "Goal",
          "detail": "Normal Goal"
        },
        ...
      ]
    }

    Returns a list of dictionaries with event information.
    """
    if not raw_data:
        return []

    events = raw_data.get("response", [])
    if not events:
        return []

    formatted_events = []

    for event in events:
        time_data = event.get("time", {})
        team = event.get("team", {})
        player = event.get("player", {})

        formatted_event = {
            "time": time_data.get("elapsed"),
            "extra_time": time_data.get("extra"),
            "team_id": team.get("id"),
            "team_name": team.get("name"),
            "team_logo": team.get("logo"),
            "player_id": player.get("id"),
            "player_name": player.get("name"),
            "type": event.get("type"),
            "detail": event.get("detail")
        }

        formatted_events.append(formatted_event)

    # Sort events by time
    formatted_events.sort(key=lambda x: (x.get("time") or 0, x.get("extra_time") or 0))

    return formatted_events
