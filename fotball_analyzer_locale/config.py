# Configuration file for fotball_analyzer_locale

import os
from dotenv import load_dotenv

load_dotenv()

# API-Football from RapidAPI configuration
API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST", "api-football-v1.p.rapidapi.com")
