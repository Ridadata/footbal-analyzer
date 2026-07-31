# Football Live Match — Web Dashboard

A FastAPI web application for live football match data: live scores, event timelines, team/player
info, and league standings, powered by [API-Football](https://rapidapi.com/api-sports/api/api-football).

See the [root README](../README.md) for the full project (this is one of two components).

## Features

- **Live Match Tracking** — currently ongoing matches across all leagues or filtered by league
- **Match Details** — statistics and event timeline for a specific fixture
- **Player & Team Lookups** — data for individual players/teams
- **In-memory caching + basic rate limiting** on outgoing API calls (see `src/api_client.py`)

## Project Structure

```
football_live_match/
├── src/
│   ├── main.py             # FastAPI app + routes
│   ├── api_client.py       # API-Football HTTP client (cached, rate-limited)
│   ├── config.py           # Loads API_KEY from .env
│   ├── data_processing.py  # Shapes API responses for templates
│   └── web/                # Jinja2 templates + static assets
├── legacy/                 # Early prototype scripts, not used by the running app (see legacy/README.md)
├── match_insights/          # Sample generated dashboard output
├── tests/                   # pytest unit/integration tests
└── requirements.txt
```

## Installation

```bash
cd football_live_match
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
# then edit .env and set API_KEY=<your RapidAPI key>
```

Get a free key from [API-Football on RapidAPI](https://rapidapi.com/api-sports/api/api-football).

## Usage

```bash
python src/main.py
```

Then open `http://localhost:8000`.

## Testing

```bash
pip install pytest
pytest tests/
```

## License

[MIT License](../LICENSE)
