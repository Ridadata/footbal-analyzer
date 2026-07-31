import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
from src.config import API_KEY

class LiveMatchDashboard:
    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self):
        self.headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "v3.football.api-sports.io"
        }
        # Create a directory for saving visualizations
        self.output_dir = "match_insights"
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_live_matches(self):
        """Fetch all currently live matches"""
        print("Fetching all live matches...")
        url = f"{self.BASE_URL}/fixtures"
        params = {"live": "all"}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def display_live_matches(self, matches_data):
        """Display all live matches in a formatted way"""
        if not matches_data.get('response'):
            print("No live matches found.")
            return None

        matches = matches_data['response']

        if len(matches) == 0:
            print("No live matches found.")
            return None

        print(f"\nFound {len(matches)} live matches:")
        print("-" * 80)
        print(f"{'ID':<6} {'League':<25} {'Home':<20} {'Score':<10} {'Away':<20} {'Time':<10}")
        print("-" * 80)

        for i, match in enumerate(matches):
            fixture_id = match['fixture']['id']
            league_name = match['league']['name']
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            home_score = match['goals']['home'] if match['goals']['home'] is not None else 0
            away_score = match['goals']['away'] if match['goals']['away'] is not None else 0
            score = f"{home_score} - {away_score}"
            elapsed = f"{match['fixture']['status']['elapsed']}'"

            print(f"{i+1:<6} {league_name[:25]:<25} {home_team[:20]:<20} {score:<10} {away_team[:20]:<20} {elapsed:<10}")

        return matches

    def select_match(self, matches):
        """Let the user select a match from the list"""
        if not matches:
            return None

        while True:
            try:
                choice = input("\nEnter the number of the match you want to analyze (or 'q' to quit): ")

                if choice.lower() == 'q':
                    return None

                choice = int(choice)
                if 1 <= choice <= len(matches):
                    return matches[choice-1]
                else:
                    print(f"Please enter a number between 1 and {len(matches)}")
            except ValueError:
                print("Please enter a valid number")

    def fetch_match_statistics(self, fixture_id):
        """Fetch statistics for a specific match"""
        print(f"Fetching statistics for match ID {fixture_id}...")
        url = f"{self.BASE_URL}/fixtures/statistics"
        params = {"fixture": fixture_id}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def fetch_match_events(self, fixture_id):
        """Fetch events (goals, cards, etc.) for a specific match"""
        print(f"Fetching events for match ID {fixture_id}...")
        url = f"{self.BASE_URL}/fixtures/events"
        params = {"fixture": fixture_id}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def fetch_match_lineups(self, fixture_id):
        """Fetch lineups for a specific match"""
        print(f"Fetching lineups for match ID {fixture_id}...")
        url = f"{self.BASE_URL}/fixtures/lineups"
        params = {"fixture": fixture_id}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def save_graph(self, filename):
        """Save the current graph to a file"""
        full_path = os.path.join(self.output_dir, filename)
        plt.savefig(full_path)
        plt.close()
        print(f"Graph saved as {full_path}")
        return full_path

    def visualize_match_stats(self, stats_data, match_info):
        """Visualize match statistics"""
        if not stats_data.get('response') or len(stats_data.get('response', [])) < 2:
            print("No statistics available for this match")
            return None

        # Extract team names and statistics
        home_team = stats_data['response'][0]['team']['name']
        away_team = stats_data['response'][1]['team']['name']

        home_stats = stats_data['response'][0]['statistics']
        away_stats = stats_data['response'][1]['statistics']

        # Create a dictionary to map stat types to their values
        home_values = {stat['type']: stat['value'] for stat in home_stats}
        away_values = {stat['type']: stat['value'] for stat in away_stats}

        # Select key statistics to display
        key_stats = [
            'Ball Possession',
            'Total Shots',
            'Shots on Goal',
            'Passes %',
            'Fouls',
            'Corner Kicks'
        ]

        # Prepare data for visualization
        home_data = []
        away_data = []

        for stat in key_stats:
            # Handle percentage values
            if stat in home_values and home_values[stat] is not None:
                if isinstance(home_values[stat], str) and '%' in home_values[stat]:
                    home_data.append(float(home_values[stat].strip('%')))
                else:
                    home_data.append(float(home_values[stat]) if home_values[stat] is not None else 0)
            else:
                home_data.append(0)

            if stat in away_values and away_values[stat] is not None:
                if isinstance(away_values[stat], str) and '%' in away_values[stat]:
                    away_data.append(float(away_values[stat].strip('%')))
                else:
                    away_data.append(float(away_values[stat]) if away_values[stat] is not None else 0)
            else:
                away_data.append(0)

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(12, 8))

        # Set the positions of the bars on the x-axis
        x = np.arange(len(key_stats))
        width = 0.35

        # Create the bars
        ax.bar(x - width/2, home_data, width, label=home_team, color='blue')
        ax.bar(x + width/2, away_data, width, label=away_team, color='red')

        # Add match score to the title
        home_score = match_info['goals']['home'] if match_info['goals']['home'] is not None else 0
        away_score = match_info['goals']['away'] if match_info['goals']['away'] is not None else 0
        score = f"{home_score} - {away_score}"
        elapsed = match_info['fixture']['status']['elapsed']

        # Add labels and title
        ax.set_xlabel('Statistics', fontweight='bold')
        ax.set_ylabel('Value', fontweight='bold')
        ax.set_title(f'Match Statistics: {home_team} {score} {away_team} ({elapsed}\')', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(key_stats, rotation=45, ha='right')

        # Add a legend
        ax.legend()

        # Add grid lines
        ax.grid(True, linestyle='--', alpha=0.7)

        # Add value labels on top of bars
        for i, v in enumerate(home_data):
            ax.text(i - width/2, v + 0.5, str(v), ha='center', fontweight='bold')

        for i, v in enumerate(away_data):
            ax.text(i + width/2, v + 0.5, str(v), ha='center', fontweight='bold')

        # Adjust layout
        plt.tight_layout()

        return self.save_graph(f"match_stats_{match_info['fixture']['id']}.png")

    def visualize_match_events(self, events_data, match_info):
        """Visualize match events timeline"""
        if not events_data.get('response'):
            print("No events available for this match")
            return None

        events = events_data['response']

        # Extract goals and cards
        goals = [event for event in events if event['type'] == 'Goal']
        cards = [event for event in events if event['type'] == 'Card']

        # Create a timeline visualization
        fig, ax = plt.subplots(figsize=(12, 6))

        # Set up the timeline
        ax.set_xlim(0, 90)  # Standard match time
        ax.set_ylim(0, 2)   # Two teams

        # Add team names
        home_team = match_info['teams']['home']['name']
        away_team = match_info['teams']['away']['name']

        ax.text(-5, 1.5, home_team, fontsize=12, fontweight='bold', ha='right', va='center')
        ax.text(-5, 0.5, away_team, fontsize=12, fontweight='bold', ha='right', va='center')

        # Plot goals
        for goal in goals:
            team_idx = 1.5 if goal['team']['name'] == home_team else 0.5
            time = int(goal['time']['elapsed'])
            player = goal['player']['name']

            ax.plot(time, team_idx, 'o', markersize=10, color='green')
            ax.text(time, team_idx + 0.2, f"{player} {time}'", rotation=45, ha='left')

        # Plot cards
        for card in cards:
            team_idx = 1.5 if card['team']['name'] == home_team else 0.5
            time = int(card['time']['elapsed'])
            player = card['player']['name']
            card_color = 'yellow' if card['detail'] == 'Yellow Card' else 'red'

            ax.plot(time, team_idx, 's', markersize=8, color=card_color)
            ax.text(time, team_idx - 0.2, f"{player} {time}'", rotation=45, ha='right')

        # Add match time markers
        ax.axvline(x=45, color='gray', linestyle='--', alpha=0.7)
        ax.text(45, 1.9, 'Half Time', ha='center')

        # Add match score to the title
        home_score = match_info['goals']['home'] if match_info['goals']['home'] is not None else 0
        away_score = match_info['goals']['away'] if match_info['goals']['away'] is not None else 0
        score = f"{home_score} - {away_score}"
        elapsed = match_info['fixture']['status']['elapsed']

        # Add labels and title
        ax.set_xlabel('Match Time (minutes)', fontweight='bold')
        ax.set_title(f'Events Timeline: {home_team} {score} {away_team} ({elapsed}\')', fontweight='bold')

        # Remove y-axis ticks
        ax.set_yticks([])

        # Add a legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Goal'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='yellow', markersize=8, label='Yellow Card'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=8, label='Red Card')
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        return self.save_graph(f"events_timeline_{match_info['fixture']['id']}.png")

    def visualize_possession_pie(self, stats_data, match_info):
        """Create a pie chart showing ball possession"""
        if not stats_data.get('response'):
            print("No statistics available for this match")
            return None

        # Extract team names and possession stats
        home_team = match_info['teams']['home']['name']
        away_team = match_info['teams']['away']['name']

        home_stats = stats_data['response'][0]['statistics']
        away_stats = stats_data['response'][1]['statistics']

        # Find possession values
        home_possession = 0
        away_possession = 0

        for stat in home_stats:
            if stat['type'] == 'Ball Possession':
                if stat['value'] is not None and '%' in stat['value']:
                    home_possession = int(stat['value'].strip('%'))
                break

        for stat in away_stats:
            if stat['type'] == 'Ball Possession':
                if stat['value'] is not None and '%' in stat['value']:
                    away_possession = int(stat['value'].strip('%'))
                break

        # If no possession data, use default values
        if home_possession == 0 and away_possession == 0:
            home_possession = 50
            away_possession = 50

        # Create the pie chart
        fig, ax = plt.subplots(figsize=(10, 8))

        labels = [f"{home_team} ({home_possession}%)", f"{away_team} ({away_possession}%)"]
        sizes = [home_possession, away_possession]
        colors = ['blue', 'red']
        explode = (0.1, 0)  # explode the 1st slice

        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=140)

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')

        # Add match score to the title
        home_score = match_info['goals']['home'] if match_info['goals']['home'] is not None else 0
        away_score = match_info['goals']['away'] if match_info['goals']['away'] is not None else 0
        score = f"{home_score} - {away_score}"
        elapsed = match_info['fixture']['status']['elapsed']

        # Add title
        ax.set_title(f'Ball Possession: {home_team} {score} {away_team} ({elapsed}\')', fontsize=16, fontweight='bold')

        return self.save_graph(f"possession_pie_{match_info['fixture']['id']}.png")

    def visualize_shots_comparison(self, stats_data, match_info):
        """Create a bar chart comparing shots statistics"""
        if not stats_data.get('response'):
            print("No statistics available for this match")
            return None

        # Extract team names
        home_team = match_info['teams']['home']['name']
        away_team = match_info['teams']['away']['name']

        home_stats = stats_data['response'][0]['statistics']
        away_stats = stats_data['response'][1]['statistics']

        # Find shots values
        home_total_shots = 0
        home_shots_on_goal = 0
        away_total_shots = 0
        away_shots_on_goal = 0

        for stat in home_stats:
            if stat['type'] == 'Total Shots':
                home_total_shots = int(stat['value']) if stat['value'] is not None else 0
            elif stat['type'] == 'Shots on Goal':
                home_shots_on_goal = int(stat['value']) if stat['value'] is not None else 0

        for stat in away_stats:
            if stat['type'] == 'Total Shots':
                away_total_shots = int(stat['value']) if stat['value'] is not None else 0
            elif stat['type'] == 'Shots on Goal':
                away_shots_on_goal = int(stat['value']) if stat['value'] is not None else 0

        # Calculate shots off target
        home_shots_off = home_total_shots - home_shots_on_goal
        away_shots_off = away_total_shots - away_shots_on_goal

        # Create the stacked bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        # Set the positions of the bars on the x-axis
        teams = [home_team, away_team]
        on_target = [home_shots_on_goal, away_shots_on_goal]
        off_target = [home_shots_off, away_shots_off]

        # Create the stacked bars
        ax.bar(teams, on_target, label='Shots on Target', color='green')
        ax.bar(teams, off_target, bottom=on_target, label='Shots off Target', color='gray')

        # Add match score to the title
        home_score = match_info['goals']['home'] if match_info['goals']['home'] is not None else 0
        away_score = match_info['goals']['away'] if match_info['goals']['away'] is not None else 0
        score = f"{home_score} - {away_score}"
        elapsed = match_info['fixture']['status']['elapsed']

        # Add labels and title
        ax.set_xlabel('Teams', fontweight='bold')
        ax.set_ylabel('Number of Shots', fontweight='bold')
        ax.set_title(f'Shot Statistics: {home_team} {score} {away_team} ({elapsed}\')', fontweight='bold')

        # Add a legend
        ax.legend()

        # Add value labels
        for i, team in enumerate(teams):
            # Label for on target
            if on_target[i] > 0:
                ax.text(i, on_target[i]/2, str(on_target[i]), ha='center', va='center', color='white', fontweight='bold')

            # Label for off target
            if off_target[i] > 0:
                ax.text(i, on_target[i] + off_target[i]/2, str(off_target[i]),
                       ha='center', va='center', color='white', fontweight='bold')

            # Label for total
            ax.text(i, on_target[i] + off_target[i] + 0.5, f"Total: {on_target[i] + off_target[i]}",
                   ha='center', va='center', color='black', fontweight='bold')

        return self.save_graph(f"shots_comparison_{match_info['fixture']['id']}.png")

    def generate_match_summary(self, match_info, stats_data, events_data):
        """Generate a text summary of the match"""
        home_team = match_info['teams']['home']['name']
        away_team = match_info['teams']['away']['name']
        home_score = match_info['goals']['home'] if match_info['goals']['home'] is not None else 0
        away_score = match_info['goals']['away'] if match_info['goals']['away'] is not None else 0
        score = f"{home_score} - {away_score}"
        elapsed = match_info['fixture']['status']['elapsed']
        league = match_info['league']['name']

        summary = [
            f"Match Summary: {home_team} vs {away_team}",
            f"League: {league}",
            f"Current Score: {score} ({elapsed} minutes played)",
            "\nKey Events:"
        ]

        # Add goals to summary
        if events_data and events_data.get('response'):
            goals = [event for event in events_data['response'] if event['type'] == 'Goal']

            if goals:
                for goal in goals:
                    team = goal['team']['name']
                    player = goal['player']['name']
                    time = goal['time']['elapsed']
                    summary.append(f"GOAL {time}' - Goal by {player} ({team})")
            else:
                summary.append("No goals scored yet")

            # Add cards to summary
            cards = [event for event in events_data['response'] if event['type'] == 'Card']

            if cards:
                summary.append("\nCards:")
                for card in cards:
                    team = card['team']['name']
                    player = card['player']['name']
                    time = card['time']['elapsed']
                    card_type = "YELLOW CARD" if card['detail'] == 'Yellow Card' else "RED CARD"
                    summary.append(f"{card_type} {time}' - {player} ({team})")
        else:
            summary.append("No detailed event data available for this match")

        # Add key statistics
        if stats_data and stats_data.get('response'):
            home_stats = stats_data['response'][0]['statistics']
            away_stats = stats_data['response'][1]['statistics']

            # Create dictionaries for easy access
            home_values = {stat['type']: stat['value'] for stat in home_stats}
            away_values = {stat['type']: stat['value'] for stat in away_stats}

            summary.append("\nKey Statistics:")

            # Possession
            home_possession = home_values.get('Ball Possession', '0%')
            away_possession = away_values.get('Ball Possession', '0%')
            summary.append(f"Ball Possession: {home_team} {home_possession} - {away_possession} {away_team}")

            # Shots
            home_shots = home_values.get('Total Shots', '0')
            away_shots = away_values.get('Total Shots', '0')
            summary.append(f"Total Shots: {home_team} {home_shots} - {away_shots} {away_team}")

            # Shots on target
            home_shots_on = home_values.get('Shots on Goal', '0')
            away_shots_on = away_values.get('Shots on Goal', '0')
            summary.append(f"Shots on Target: {home_team} {home_shots_on} - {away_shots_on} {away_team}")

            # Corners
            home_corners = home_values.get('Corner Kicks', '0')
            away_corners = away_values.get('Corner Kicks', '0')
            summary.append(f"Corner Kicks: {home_team} {home_corners} - {away_corners} {away_team}")

            # Fouls
            home_fouls = home_values.get('Fouls', '0')
            away_fouls = away_values.get('Fouls', '0')
            summary.append(f"Fouls: {home_team} {home_fouls} - {away_fouls} {away_team}")

        # Save summary to file
        summary_text = "\n".join(summary)
        summary_file = os.path.join(self.output_dir, f"match_summary_{match_info['fixture']['id']}.txt")

        with open(summary_file, 'w') as f:
            f.write(summary_text)

        print(f"Match summary saved to {summary_file}")

        # Also print the summary to console
        print("\n" + summary_text)

        return summary_file

    def create_html_dashboard(self, match_info, dashboard_files):
        """Create an HTML dashboard that combines all visualizations"""
        home_team = match_info['teams']['home']['name']
        away_team = match_info['teams']['away']['name']
        home_score = match_info['goals']['home'] if match_info['goals']['home'] is not None else 0
        away_score = match_info['goals']['away'] if match_info['goals']['away'] is not None else 0
        score = f"{home_score} - {away_score}"
        elapsed = match_info['fixture']['status']['elapsed']
        league = match_info['league']['name']

        # Read the match summary
        summary_text = ""
        with open(dashboard_files['summary_file'], 'r') as f:
            summary_text = f.read()

        # Create graph sections based on available data
        graph_sections = ""

        # Match Statistics
        if dashboard_files.get('stats_graph'):
            graph_sections += f"""
            <div class="graph-container">
                <h3>Match Statistics</h3>
                <img src="{os.path.basename(dashboard_files['stats_graph'])}" alt="Match Statistics">
            </div>
            """

        # Ball Possession
        if dashboard_files.get('possession_graph'):
            graph_sections += f"""
            <div class="graph-container">
                <h3>Ball Possession</h3>
                <img src="{os.path.basename(dashboard_files['possession_graph'])}" alt="Ball Possession">
            </div>
            """

        # Shot Statistics
        if dashboard_files.get('shots_graph'):
            graph_sections += f"""
            <div class="graph-container">
                <h3>Shot Statistics</h3>
                <img src="{os.path.basename(dashboard_files['shots_graph'])}" alt="Shot Statistics">
            </div>
            """

        # Match Events Timeline
        if dashboard_files.get('events_graph'):
            graph_sections += f"""
            <div class="graph-container">
                <h3>Match Events Timeline</h3>
                <img src="{os.path.basename(dashboard_files['events_graph'])}" alt="Match Events Timeline">
            </div>
            """

        # If no graphs are available
        if not graph_sections:
            graph_sections = "<p>No detailed statistics available for this match.</p>"

        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{home_team} vs {away_team} - Live Match Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #333; }}
                .match-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
                .score {{ font-size: 24px; font-weight: bold; }}
                .time {{ color: #777; }}
                .graphs {{ display: flex; flex-wrap: wrap; justify-content: space-between; }}
                .graph-container {{ width: 48%; margin-bottom: 20px; }}
                .graph-container img {{ width: 100%; border: 1px solid #ddd; }}
                .summary {{ background-color: #f9f9f9; padding: 15px; white-space: pre-line; }}
                @media (max-width: 768px) {{
                    .graph-container {{ width: 100%; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="match-header">
                    <h1>{home_team} vs {away_team}</h1>
                    <div>
                        <div class="score">{score}</div>
                        <div class="time">{elapsed}' | {league}</div>
                    </div>
                </div>

                <h2>Match Insights</h2>
                <div class="graphs">
                    {graph_sections}
                </div>

                <h2>Match Summary</h2>
                <div class="summary">
                    {summary_text}
                </div>
            </div>
        </body>
        </html>
        """

        # Save HTML file
        html_file = os.path.join(self.output_dir, f"dashboard_{match_info['fixture']['id']}.html")
        with open(html_file, 'w') as f:
            f.write(html_content)

        print(f"\nHTML Dashboard created: {html_file}")
        print("Open this file in your web browser to view the complete dashboard.")

        return html_file

    def create_dashboard(self, match_info):
        """Create a dashboard for the selected match"""
        fixture_id = match_info['fixture']['id']

        try:
            # Fetch match data
            stats_data = self.fetch_match_statistics(fixture_id)
            events_data = self.fetch_match_events(fixture_id)

            # Create visualizations
            print("\nGenerating match insights...")
            stats_graph = self.visualize_match_stats(stats_data, match_info)
            events_graph = self.visualize_match_events(events_data, match_info)
            possession_graph = self.visualize_possession_pie(stats_data, match_info)
            shots_graph = self.visualize_shots_comparison(stats_data, match_info)

            # Generate match summary
            summary_file = self.generate_match_summary(match_info, stats_data, events_data)

            # Create dashboard files dictionary with only available files
            dashboard_files = {'summary_file': summary_file}

            if stats_graph:
                dashboard_files['stats_graph'] = stats_graph

            if events_graph:
                dashboard_files['events_graph'] = events_graph

            if possession_graph:
                dashboard_files['possession_graph'] = possession_graph

            if shots_graph:
                dashboard_files['shots_graph'] = shots_graph

            # Create HTML dashboard
            self.create_html_dashboard(match_info, dashboard_files)

            print("\nDashboard created successfully!")
            print(f"All visualizations and summary saved in the '{self.output_dir}' directory.")

            return dashboard_files

        except Exception as e:
            print(f"Error creating dashboard: {str(e)}")
            return None

def main():
    dashboard = LiveMatchDashboard()

    try:
        # Fetch all live matches
        matches_data = dashboard.fetch_live_matches()

        # Display matches and let user select one
        matches = dashboard.display_live_matches(matches_data)

        if not matches:
            print("\nNo live matches found. Using sample data instead.")
            # Create sample match data
            sample_match = {
                'fixture': {
                    'id': 999999,
                    'status': {'elapsed': 40}
                },
                'league': {
                    'name': 'Liga MX Clausura'
                },
                'teams': {
                    'home': {'name': 'León'},
                    'away': {'name': 'Monterrey'}
                },
                'goals': {
                    'home': 0,
                    'away': 1
                }
            }

            # Create dashboard with sample data
            dashboard.create_dashboard(sample_match)
        else:
            # Let user select a match
            selected_match = dashboard.select_match(matches)

            if selected_match:
                # Create dashboard for selected match
                dashboard.create_dashboard(selected_match)
            else:
                print("No match selected. Exiting.")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
