import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.api_client import (
    get_matches,
    get_teams,
    get_player,
    get_live_matches,
    get_live_matches_by_league,
    get_match_statistics,
    get_match_events,
    get_leagues
)
from src.data_processing import (
    process_match_data,
    process_team_data,
    process_player_data,
    process_live_matches,
    process_match_statistics,
    process_match_events
)

app = FastAPI(title="Football Data Visualization")

# Mount static files
app.mount("/static", StaticFiles(directory=Path("src/web/static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=Path("src/web/templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Home page with search functionality for leagues and matches.
    """
    # Fetch available leagues for the dropdown
    leagues_data = get_leagues()
    leagues = []
    if leagues_data and "response" in leagues_data:
        for league in leagues_data["response"]:
            leagues.append({
                "id": league.get("league", {}).get("id"),
                "name": league.get("league", {}).get("name"),
                "country": league.get("country", {}).get("name")
            })

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "leagues": leagues}
    )

@app.get("/api/leagues")
async def api_leagues():
    """
    API endpoint to get all available leagues.
    """
    data = get_leagues()
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch leagues")
    return data

@app.get("/api/live-matches")
async def api_live_matches():
    """
    API endpoint to get all live matches.
    """
    data = get_live_matches()
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch live matches")

    processed_data = process_live_matches(data)
    return {"matches": processed_data}

@app.get("/api/league/{league_id}/live-matches")
async def api_league_live_matches(league_id: str):
    """
    API endpoint to get live matches for a specific league.
    """
    data = get_live_matches_by_league(league_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch live matches for this league")

    processed_data = process_live_matches(data)
    return {"matches": processed_data}

@app.get("/api/league/{league_id}/matches")
async def api_league_matches(league_id: str):
    """
    API endpoint to get all matches for a specific league.
    """
    data = get_matches(league_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch matches")

    processed_data = process_match_data(data)
    return {"matches": processed_data}

@app.get("/api/league/{league_id}/teams")
async def api_league_teams(league_id: str):
    """
    API endpoint to get all teams for a specific league.
    """
    data = get_teams(league_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch teams")

    processed_data = process_team_data(data)
    return {"teams": processed_data}

@app.get("/api/match/{match_id}/statistics")
async def api_match_statistics(match_id: str):
    """
    API endpoint to get statistics for a specific match.
    """
    data = get_match_statistics(match_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch match statistics")

    processed_data = process_match_statistics(data)
    return {"statistics": processed_data}

@app.get("/api/match/{match_id}/events")
async def api_match_events(match_id: str):
    """
    API endpoint to get events for a specific match.
    """
    data = get_match_events(match_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch match events")

    processed_data = process_match_events(data)
    return {"events": processed_data}

@app.get("/api/player/{player_id}")
async def api_player_data(player_id: str):
    """
    API endpoint to get data for a specific player.
    """
    data = get_player(player_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Unable to fetch player data")

    processed_data = process_player_data(data)
    return {"player": processed_data}

@app.get("/live-matches", response_class=HTMLResponse)
async def live_matches_page(request: Request):
    """
    Page to display all live matches.
    """
    data = get_live_matches()
    print(f"Raw data from get_live_matches: {data}")  # Debug print
    matches = []
    if data:
        matches = process_live_matches(data)
        print(f"Number of live matches: {len(matches)}")  # Debug print
        print(f"Live matches: {matches}")  # Debug print

    return templates.TemplateResponse(
        "live_matches.html",
        {"request": request, "matches": matches}
    )

@app.get("/league/{league_id}/live-matches", response_class=HTMLResponse)
async def league_live_matches_page(request: Request, league_id: str):
    """
    Page to display live matches for a specific league.
    """
    data = get_live_matches_by_league(league_id)
    matches = []
    if data:
        matches = process_live_matches(data)

    # Get league info
    leagues_data = get_leagues()
    league_name = "Unknown League"
    if leagues_data and "response" in leagues_data:
        for league in leagues_data["response"]:
            if str(league.get("league", {}).get("id")) == league_id:
                league_name = league.get("league", {}).get("name")
                break

    return templates.TemplateResponse(
        "live_matches.html",
        {"request": request, "matches": matches, "league_name": league_name, "league_id": league_id}
    )

@app.get("/match/{match_id}", response_class=HTMLResponse)
async def match_details_page(request: Request, match_id: str):
    """
    Page to display detailed information for a specific match.
    """
    # Get match data
    match_data = None

    # We need to search for the match in all live matches
    live_data = get_live_matches()
    if live_data:
        matches = process_live_matches(live_data)
        for match in matches:
            if str(match.get("match_id")) == match_id:
                match_data = match
                break

    if not match_data:
        raise HTTPException(status_code=404, detail="Match not found")

    # We don't need to fetch statistics and events here anymore
    # They will be fetched by the client-side JavaScript

    return templates.TemplateResponse(
        "match_details.html",
        {
            "request": request,
            "match": match_data
        }
    )

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
