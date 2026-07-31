import os
import time
import httpx
import logging
from src.config import API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "https://v3.football.api-sports.io"  # Actual football API base URL

# Simple in-memory cache: { (method, endpoint, sorted_params_tuple): (data, timestamp) }
CACHE = {}
CACHE_DURATION = 300  # Cache duration in seconds (5 minutes)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_CALLS = 10
REQUEST_TIMESTAMPS = []


def _rate_limit():
    """
    Naive rate-limiting approach: allow up to RATE_LIMIT_MAX_CALLS in RATE_LIMIT_WINDOW seconds.
    If surpassed, wait until within limit again.
    """
    now = time.time()
    # Remove timestamps older than RATE_LIMIT_WINDOW
    while REQUEST_TIMESTAMPS and (now - REQUEST_TIMESTAMPS[0]) > RATE_LIMIT_WINDOW:
        REQUEST_TIMESTAMPS.pop(0)

    if len(REQUEST_TIMESTAMPS) >= RATE_LIMIT_MAX_CALLS:
        # Wait until we can safely make another request
        time_to_wait = RATE_LIMIT_WINDOW - (now - REQUEST_TIMESTAMPS[0])
        if time_to_wait > 0:
            logger.info(f"Rate limit reached. Waiting {time_to_wait:.2f} seconds")
            time.sleep(time_to_wait)
        # After waiting, remove old timestamps again
        now = time.time()
        while REQUEST_TIMESTAMPS and (now - REQUEST_TIMESTAMPS[0]) > RATE_LIMIT_WINDOW:
            REQUEST_TIMESTAMPS.pop(0)

    REQUEST_TIMESTAMPS.append(time.time())


def _handle_error(response: httpx.Response):
    """
    Basic error handling for different response codes.
    Customize based on API docs.
    """
    if response.status_code == 401:
        logger.error("Error 401: Unauthorized. Check your API key.")
    elif response.status_code == 403:
        logger.error("Error 403: Forbidden. You might not have permission to access this resource.")
    elif response.status_code == 404:
        logger.error("Error 404: Resource not found.")
    elif 400 <= response.status_code < 500:
        logger.error(f"Client error {response.status_code}: {response.text}")
    elif response.status_code >= 500:
        logger.error(f"Server error {response.status_code}: {response.text}")


def _fetch_data(method: str, endpoint: str, params: dict = None):
    """
    Internal utility to fetch data from the API with caching, rate limiting, and error handling.
    method: HTTP method e.g. "GET", "POST"
    endpoint: e.g. "/matches", "/teams"
    params: dict of query params
    """
    if params is None:
        params = {}

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }

    # Cache key built from method, endpoint, and sorted params
    cache_key = (method, endpoint, tuple(sorted(params.items())))
    if cache_key in CACHE:
        data, timestamp = CACHE[cache_key]
        # Check if cache is still valid
        if time.time() - timestamp < CACHE_DURATION:
            logger.info(f"Using cached data for {endpoint}")
            return data
        else:
            # Cache expired, remove it
            del CACHE[cache_key]

    _rate_limit()

    url = f"{API_BASE_URL}{endpoint}"
    logger.info(f"Fetching data from {url} with params {params}")

    try:
        if method.upper() == "GET":
            response = httpx.get(url, headers=headers, params=params)
        else:
            # For demonstration, only GET is implemented here.
            # Extend as needed for POST/PUT/PATCH/DELETE
            response = httpx.get(url, headers=headers, params=params)

        if response.status_code != 200:
            _handle_error(response)
        response.raise_for_status()

        data = response.json()
        # Store in cache
        CACHE[cache_key] = (data, time.time())
        return data

    except httpx.HTTPError as e:
        logger.error(f"Error fetching data from endpoint {endpoint}: {e}")
        return None


def get_matches(league_id: str):
    """
    Fetch matches for a given league from the football API.
    """
    params = {"league": league_id}
    return _fetch_data("GET", "/fixtures", params)


def get_live_matches():
    """
    Fetch all currently live matches.
    """
    params = {"live": "all"}
    return _fetch_data("GET", "/fixtures", params)


def get_live_matches_by_league(league_id: str):
    """
    Fetch live matches for a specific league.
    """
    params = {"live": "all", "league": league_id}
    return _fetch_data("GET", "/fixtures", params)


def get_match_statistics(fixture_id: str):
    """
    Fetch statistics for a specific match.
    """
    params = {"fixture": fixture_id}
    return _fetch_data("GET", "/fixtures/statistics", params)


def get_match_events(fixture_id: str):
    """
    Fetch events (goals, cards, etc.) for a specific match.
    """
    params = {"fixture": fixture_id}
    return _fetch_data("GET", "/fixtures/events", params)


def get_teams(league_id: str):
    """
    Fetch teams for a given league.
    """
    params = {"league": league_id}
    return _fetch_data("GET", "/teams", params)


def get_player(player_id: str):
    """
    Fetch data for a specific player.
    """
    params = {"id": player_id}
    return _fetch_data("GET", "/players", params)


def get_leagues():
    """
    Fetch all available leagues.
    """
    return _fetch_data("GET", "/leagues")
