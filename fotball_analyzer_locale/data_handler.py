import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.table import Table
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from io import BytesIO
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
from config import API_KEY, API_HOST

headers = {
	"x-rapidapi-key": API_KEY,
	"x-rapidapi-host": API_HOST
}

LEAGUE_ID = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61,
    "UEFA Champions League": 2,
    "UEFA Europa League": 3,
    "Eredivisie": 88,
    "Primeira Liga": 94,
    "MLS": 253,
    "Brasileirão": 71,
    "Argentine Primera División": 128,
    "Saudi Pro League": 307,
    "Turkish Süper Lig": 203,
    "Russian Premier League": 235,
    "Belgian Pro League": 144,
    "Swiss Super League": 207,
    "Scottish Premiership": 179,
    "Greek Super League": 197,
    "J1 League": 98
}


def get_top_scorers(year, league_name):
    url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"
    league_id = LEAGUE_ID[league_name]
    params = {
            "league": league_id,      # id de premier league
            "season": year
        }

    response = requests.get(url, headers=headers , params=params)
    
    data = response.json()

    top_players=data["response"][:20]
    names=[player["player"]["name"] for player in top_players]   
    goals = [player["statistics"][0]["goals"]["total"] for player in top_players] 
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Horizontal bar plot
    bars = ax.barh(names[::-1], goals[::-1], color="skyblue")
    ax.set_xlabel("Goals", fontsize=12)
    ax.set_title(f"Top 20 Goal Scorers - {league_name} {year}", fontweight="bold")

    # Annotate bars
    for bar in bars:
        ax.text(bar.get_width() + 0.2, bar.get_y() + 0.2, str(int(bar.get_width())))

    fig.tight_layout()
    return fig  # ✅ Return the Figure object




def get_top_assisters(league_name, season, top_n=10):
    url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"
    league_id = LEAGUE_ID[league_name]
    params = {
                "league": league_id,      # ID de La Liga
                "season": season
                
            }
    try:
        
        response=requests.get(url,headers=headers ,params=params)
        response.raise_for_status()
        data=response.json()

        if not data.get("response"):
            print("NO data fouind!")
            return
        
        players=sorted(
            data["response"],
            key=lambda p: p["statistics"][0]["goals"]["assists"] or 0,
            reverse=True
        )

        top_players=players[:top_n]

        names = [p["player"]["name"] for p in top_players]
        assists = [p["statistics"][0]["goals"]["assists"] or 0 for p in top_players]


        #visulalissation :

        fig2,ax2=plt.subplots(figsize=(12,6))
        bars=ax2.barh(names[::-1],assists[::-1],color="lightgreen")
        ax2.set_xlabel("Assists",fontsize=12)
        ax2.set_title(f"Top {top_n} assisters - {league_name} {season} ", fontweight="bold")
        fig2.tight_layout()
        

        for bar in bars:
            ax2.text(bar.get_width()+0.2 , bar.get_y()+0.2 ,str(int(bar.get_width())))

        return fig2


    except requests.exceptions.RequestException as e:
        print(f"Error fetching data : {e}")



def get_leagues():
    url ="https://api-football-v1.p.rapidapi.com/v3/leagues"
    response = requests.get(url, headers=headers)
    leagues = response.json()
    league_names = []
    for item in leagues['response']:
        league_names.append(item['league']['name'])
    return sorted(list(set(league_names)))



def get_seasons():
    # Get all seasons (2020, 2021, etc.)
    # Could also be tied to a specific league later
    return [str(y) for y in range(2014, 2026)]


def get_teams(league_name, season):
    # Get league ID by name
    leagues_url ="https://api-football-v1.p.rapidapi.com/v3/leagues"

    leagues = requests.get(leagues_url, headers=headers).json()
    
    league_id = None
    for item in leagues['response']:
        if item['league']['name'] == league_name:
            league_id = item['league']['id']
            break

    if not league_id:
        return []

    teams_url = f"https://api-football-v1.p.rapidapi.com/v3/teams?league={league_id}&season={season}"
    teams = requests.get(teams_url, headers=headers).json()
    return [team['team']['name'] for team in teams['response']]




def get_fixture_id(team1_name, team2_name, date, league, season):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    league_id = LEAGUE_ID[league]  # Make sure LEAGUE_ID is defined
    params = {
        "league": league_id,
        "season": season,
        "date": date  # Must be in YYYY-MM-DD format
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json().get("response", [])

    for fixture in data:
        home = fixture["teams"]["home"]["name"].lower()
        away = fixture["teams"]["away"]["name"].lower()

        if (team1_name.lower() in home and team2_name.lower() in away) or \
           (team1_name.lower() in away and team2_name.lower() in home):
            return fixture["fixture"]["id"]  # Found match

    raise ValueError(f"No fixture found matching {team1_name} vs {team2_name} on {date} in {league}.")

#exemple use:
# fixture_id = get_fixture_id(
#     team1_name="Barcelona",
#     team2_name="Real Madrid",
#     match_date="2023-10-28",
#     league_name="La Liga",
#     season=2023
# )



def get_fixture_stats(fixture_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
    params = {"fixture": fixture_id}
    response = requests.get(url, headers=headers, params=params)
    
    data = response.json().get("response", [])

    if not data or len(data) < 2:
        raise ValueError(f"No statistics found for fixture ID {fixture_id}. Response: {data}")

    # Team 1
    team1_name = data[0]["team"]["name"]
    team1_id = data[0]["team"]["id"]
    stats1 = {item["type"]: item["value"] for item in data[0]["statistics"]}

    # Team 2
    team2_name = data[1]["team"]["name"]
    team2_id = data[1]["team"]["id"]
    stats2 = {item["type"]: item["value"] for item in data[1]["statistics"]}

    return team1_name, stats1, team2_name, stats2




def plot_grouped_stats(team_name, team_stats, opponent_name, opponent_stats):
    keys = list(team_stats.keys())
    team_values = []
    opponent_values = []

    for key in keys:
        t_val = team_stats.get(key, 0)
        o_val = opponent_stats.get(key, 0)

        # Convert percentages like '61%' to float
        if isinstance(t_val, str) and t_val.endswith('%'):
            t_val = t_val.replace('%', '')
        if isinstance(o_val, str) and o_val.endswith('%'):
            o_val = o_val.replace('%', '')

        # Convert all to float, if fails set 0
        try:
            t_val = float(t_val)
        except:
            t_val = 0
        try:
            o_val = float(o_val)
        except:
            o_val = 0

        team_values.append(t_val)
        opponent_values.append(o_val)

    x = np.arange(len(keys))
    width = 0.35

    fig , ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, team_values, width, label=team_name, color='royalblue')
    ax.bar(x + width/2, opponent_values, width, label=opponent_name, color='tomato')

    ax.set_xticks(x)
    plt.setp(ax.get_xticklabels(), rotation=45)

    ax.set_ylabel('Value')
    ax.set_title(f'{team_name} vs {opponent_name} - Match Stats')
    ax.legend()
    fig.tight_layout()
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    return fig





def plot_possession_pie(team_name, team_percent, opponent_name, opponent_percent):
    # Convert string to float if needed
    if isinstance(team_percent, str):
        team_percent = float(team_percent.replace('%', ''))
    if isinstance(opponent_percent, str):
        opponent_percent = float(opponent_percent.replace('%', ''))

    labels = [team_name, opponent_name]
    sizes = [team_percent, opponent_percent]
    colors = ['skyblue', 'lightcoral']

    fig ,ax =plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title('Possession')
    ax.axis('equal')  # Equal aspect ratio ensures pie is circular
    return fig





def plot_passes_pie(team_name, team_percent, opponent_name, opponent_percent):
    # Convert string to float if needed
    if isinstance(team_percent, str):
        team_percent = float(team_percent.replace('%', ''))
    if isinstance(opponent_percent, str):
        opponent_percent = float(opponent_percent.replace('%', ''))

    labels = [team_name, opponent_name]
    sizes = [team_percent, opponent_percent]
    colors = ['royalblue', 'lightcoral']

    fig,ax=plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title('Passes')
    ax.axis('equal')  # Equal aspect ratio ensures pie is circular
    return fig



def plot_passes_stats(team1, stats1, team2, stats2):
    keys = ['Total passes', 'Passes accurate']
    team_values = []
    opponent_values = []

    for key in keys:
        t_val = stats1.get(key, 0)
        o_val = stats2.get(key, 0)

        try:
            t_val = float(str(t_val).replace('%', ''))
            o_val = float(str(o_val).replace('%', ''))
        except:
            t_val = o_val = 0

        team_values.append(t_val)
        opponent_values.append(o_val)

    x = np.arange(len(keys))
    width = 0.35

    fig,ax = plt.subplots(figsize=(6, 5))
    ax.bar(x - width/2, team_values, width, label=team1, color='royalblue')
    ax.bar(x + width/2, opponent_values, width, label=team2, color='tomato')

    ax.set_xticks(x, keys)
    ax.set_ylabel('Count')
    ax.set_title('Passes Comparison')
    ax.legend()
    fig.tight_layout()
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    return fig



def plot_compact_stats(team1, stats1, team2, stats2):
    keys = ['Shots on Goal', 'Total Shots', 'Fouls', 'Yellow Cards', 'Red Cards', 'Corner Kicks', 'Offsides']
    team_values = []
    opponent_values = []

    for key in keys:
        t_val = stats1.get(key, 0)
        o_val = stats2.get(key, 0)

        try:
            t_val = float(str(t_val).replace('%', ''))
            o_val = float(str(o_val).replace('%', ''))
        except:
            t_val = o_val = 0

        team_values.append(t_val)
        opponent_values.append(o_val)

    x = np.arange(len(keys))
    width = 0.35

    fig,ax=plt.subplots(figsize=(10, 5))
    ax.bar(x - width/2, team_values, width, label=team1, color='steelblue')
    ax.bar(x + width/2, opponent_values, width, label=team2, color='indianred')

    ax.set_xticks(x, keys,  ha='right')  # rotation=45,
    ax.set_ylabel('Count')
    ax.set_title('Key Match Stats')
    ax.legend()
    fig.tight_layout()
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    return fig





def final_plot_stats_match(team1_name,team2_name,match_date,league_name, season):
    fixture_id=get_fixture_id(team1_name, team2_name, match_date, league_name, season)
    print(f"Using fixture ID: {fixture_id}")
    team_name,team_stats,opponent_name,opponent_stats =get_fixture_stats(fixture_id)

    # fig1=plot_grouped_stats(team_name, team_stats, opponent_name, opponent_stats)
    fig2=plot_possession_pie(team_name,team_stats["Ball Possession"],opponent_name,opponent_stats["Ball Possession"])
    fig3=plot_passes_pie(team_name,team_stats["Passes %"],opponent_name,opponent_stats["Passes %"])
    fig4=plot_passes_stats(team_name, team_stats, opponent_name, opponent_stats)
    fig5=plot_compact_stats(team_name, team_stats, opponent_name, opponent_stats)
    return [fig2,fig3,fig4,fig5]
#all this funcitn must return a figure then i ll use them in main gui





# final_plot_stats_match("Barcelona", "Real Madrid","2023-10-28","La Liga",2023)






def get_league_standings(league, season):
    league_id = LEAGUE_ID[league]
    if not league_id:
        raise ValueError(f"Unknown league: {league}")

    url = "https://api-football-v1.p.rapidapi.com/v3/standings"
    params = {
        "league": league_id,
        "season": season
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code != 200 or "response" not in data or not data["response"]:
        raise Exception("Failed to fetch standings data.")
    
    standings = data["response"][0]["league"]["standings"][0]

    # Build data rows
    table_data = [["Pos", "Team", "P", "W", "D", "L", "Pts"]]
    for team in standings:
        table_data.append([
            team["rank"],
            team["team"]["name"],
            team["all"]["played"],
            team["all"]["win"],
            team["all"]["draw"],
            team["all"]["lose"],
            team["points"]
        ])

    # Plotting
    fig, ax = plt.subplots(figsize=(10, len(table_data) * 0.4))
    ax.set_axis_off()

    table = Table(ax, bbox=[0, 0, 1, 1])

    n_rows = len(table_data)
    n_cols = len(table_data[0])

    col_widths = [0.07, 0.30, 0.07, 0.07, 0.07, 0.07, 0.07]

    for i in range(n_rows):
        for j in range(n_cols):
            cell_text = str(table_data[i][j])
            table.add_cell(i, j, width=col_widths[j], height=0.4,
                           text=cell_text,
                           loc='center',
                           facecolor="#f0f0f0" if i == 0 else "white",
                           edgecolor='black')

    table.set_fontsize(12)
    ax.add_table(table)
    ax.set_title(f"{league} {season} Standings", fontsize=12, fontweight="bold", pad=5)

    plt.tight_layout()
    return fig






def get_match_info(league, season, round_number):
    league_id = LEAGUE_ID[league]
    if not league_id:
        raise ValueError(f"Unknown league: {league}")

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {
        "league": league_id,
        "season": season,
        "round": f"Regular Season - {round_number}"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    matches = data['response']
    if not matches:
        raise Exception("No match data found.")

    # Plot Setup
    fig, ax = plt.subplots(figsize=(14, len(matches) * 1.2))
    ax.axis('off')

    for idx, match in enumerate(matches):
        y_pos = len(matches) - idx

        # Extract team names, logos, and scores
        home = match["teams"]["home"]
        away = match["teams"]["away"]
        home_name = home["name"]
        away_name = away["name"]
        home_logo = home["logo"]
        away_logo = away["logo"]

        status = match["fixture"]["status"]["short"]
        date = match["fixture"]["date"][:10]
        time = match["fixture"]["date"][11:16]

        # Match status or result
        if status in ["FT", "AET", "PEN"]:
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]
            result_text = f"{home_goals} - {away_goals}"
            ax.text(0.5, y_pos, result_text, va='center', ha='center', fontsize=12, color='white', bbox=dict(facecolor='red', boxstyle='round,pad=0.3'))
            ax.text(0.55, y_pos, f"({date})", va='center', ha='left', fontsize=10, color='gray')
        else:
            ax.text(0.5, y_pos, f"{time}", va='center', ha='center', fontsize=12, color='white', bbox=dict(facecolor='red', boxstyle='round,pad=0.3'))
            ax.text(0.55, y_pos, f"({date})", va='center', ha='left', fontsize=10, color='gray')


            # Match display with date added below the result
        ax.text(0.25, y_pos + 0.2, home_name, va='center', ha='right', fontsize=12, weight='bold')
        # ax.text(0.5, y_pos + 0.2, result_text, va='center', ha='center', fontsize=12, color='white', bbox=dict(facecolor='red', boxstyle='round,pad=0.3'))
        ax.text(0.75, y_pos + 0.2, away_name, va='center', ha='left', fontsize=12, weight='bold')



        # Add logos
        def add_logo(image_url, x, y):
            try:
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img = img.resize((30, 30))
                imagebox = OffsetImage(img, zoom=1)
                ab = AnnotationBbox(imagebox, (x, y), frameon=False)
                ax.add_artist(ab)
            except Exception:
                pass

        add_logo(home_logo, 0.08, y_pos)
        add_logo(away_logo, 0.92, y_pos)

    ax.set_ylim(0.5, len(matches) + 1)
    ax.set_xlim(0, 1)
    ax.set_title(f"{league} {season} - Round {round_number} Matches", fontsize=16, weight='bold', pad=20)

    plt.tight_layout()
    return fig






def get_round():
    round=[]
    for i in range(1,40):
        round.append(str(i))
    return round




def get_all_players(league, season):
    url = "https://api-football-v1.p.rapidapi.com/v3/players"

    if league not in LEAGUE_ID:
        raise ValueError(f"Unknown league: {league}")

    league_id = LEAGUE_ID[league]
    players = {}
    page = 1

    while True:
        params = {
            "league": league_id,
            "season": season,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if response.status_code != 200 or not data.get("response"):
            break

        for item in data["response"]:
            name = item["player"]["name"]
            player_id = item["player"]["id"]
            players[name] = player_id

        page += 1

    return players



def plot_player_radar_by_id(player_id,league,season):
    league_id = LEAGUE_ID[league]
    url = "https://api-football-v1.p.rapidapi.com/v3/players"
    params = {
        "id": player_id,
        "season": season,
        "league": league_id

    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data["response"]:
        raise ValueError(f"No stats found for player ID {player_id}")

    stats = data["response"][0]["statistics"][0]
    player_name = data["response"][0]["player"]["name"]
    league_name = stats["league"]["name"]
    

    metrics = {
        "Goals": stats["goals"]["total"] or 0,
        "Assists": stats["goals"]["assists"] or 0,
        "Shots": stats["shots"]["total"] or 0,
        "Key Passes": stats["passes"]["key"] or 0,
        "Tackles": stats["tackles"]["total"] or 0,
        "Interceptions": stats["tackles"]["interceptions"] or 0,
        "Dribbles": stats["dribbles"]["success"] or 0,
    }

    # Normalize metrics here if needed...

    # Radar plotting code same as before
    labels = list(metrics.keys())
    values = list(metrics.values())
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='crimson', alpha=0.4)
    ax.plot(angles, values, color='crimson', linewidth=2)

    # Add values at each point
    for i, (angle, value) in enumerate(zip(angles, values)):
        if i == len(labels):  # Skip the repeated last point
            continue
        ax.text(angle, value + max(values) * 0.05, str(value), ha='center', va='center', fontsize=10, color='black', fontweight='bold')

    # Setup axes and titles
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_title(f"{player_name} - {league_name} {season}", fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, linestyle='dotted', color='gray', alpha=0.6)

    return fig
