# Fotball Analyzer Locale

This directory contains the **Fotball Analyzer Locale** application, a desktop app for football data analysis, user authentication, and visualization. It is built with Python, CustomTkinter, and PIL, and is designed for local use alongside the web-based dashboard.

## Features

- User registration and login with secure password hashing
- Local user management (JSON-based)
- Football data analysis and visualization
- Modern, user-friendly GUI with CustomTkinter
- Asset management for images and icons

## Directory Structure & Components

- **main.py**: Entry point for the locale app. Launches the main GUI and integrates analysis and data handling.
- **data_handler.py**: Contains core logic for football data analysis and statistics computation.
- **login.py**: Implements the authentication system (registration, login) and the main login/register GUI.
- **config.py**: Configuration file (e.g., API keys).
- **users.json**: Stores registered user data (emails, hashed passwords, timestamps).
- **color_login.json**: CustomTkinter color theme for the login interface.
- **assets/**: Contains images and icons used in the GUI (backgrounds, icons, etc.).

## Setup

1. **Install dependencies**:
   - Python 3.8+
   - Install required packages:
     ```
     pip install -r requirements.txt
     ```
2. **Assets**: Ensure the `assets/` directory contains all required images (see included files).

3. **Configuration**:
   - Obtain an API key from [API-Football on RapidAPI](https://rapidapi.com/api-sports/api/api-football).
   - Copy `.env.example` to `.env` and set your key:
     ```
     cp .env.example .env
     ```
     `config.py` loads `API_KEY`/`API_HOST` from this file — never commit real keys.

## Usage

1. **Run the application**:
   ```
   python main.py
   ```
2. **Login/Register**:
   - On first launch, register a new account.
   - Login with your credentials to access the main features.

3. **Features**:
   - Analyze football data, view statistics, and visualize results.
   - User data is stored locally in `users.json`.

## File Descriptions

| File/Folder         | Description                                                      |
|---------------------|------------------------------------------------------------------|
| main.py             | Main entry point; launches the GUI and app logic                 |       
| data_handler.py     | Football data analysis and statistics                            |
| login.py            | User authentication and login/register GUI                       |
| config.py           | Configuration (API keys, etc.)                                   |
| users.json          | Local user database (JSON)                                       |
| color_login.json    | CustomTkinter color theme                                        |
| assets/             | Images and icons for the GUI                                     |

## Notes

- All user data is stored locally; no external server is required for authentication.
- `users.json` ships as an empty template (`{"users": []}`) and is populated as people register.
- For best experience, ensure all asset files are present in the `assets/` directory.

---

For instructions on using the locale app together with the web dashboard, see the main project README.
