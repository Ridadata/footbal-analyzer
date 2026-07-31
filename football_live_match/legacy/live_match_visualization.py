import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from src.config import API_KEY

class LiveMatchVisualizer:
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self):
        self.headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "v3.football.api-sports.io"
        }
    
    def fetch_live_matches(self):
        """Fetch all currently live matches"""
        url = f"{self.BASE_URL}/fixtures"
        params = {"live": "all"}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def fetch_match_by_teams(self, league_name, team1_name, team2_name):
        """Find a specific match by team names"""
        # First get all live matches
        live_matches = self.fetch_live_matches()
        
        # Filter for the specific match
        for match in live_matches.get('response', []):
            league = match.get('league', {})
            teams = match.get('teams', {})
            
            league_match = league_name.lower() in league.get('name', '').lower()
            team1_match = team1_name.lower() in teams.get('home', {}).get('name', '').lower()
            team2_match = team2_name.lower() in teams.get('away', {}).get('name', '').lower()
            
            if league_match and team1_match and team2_match:
                return match
        
        return None
    
    def fetch_match_statistics(self, fixture_id):
        """Fetch statistics for a specific match"""
        url = f"{self.BASE_URL}/fixtures/statistics"
        params = {"fixture": fixture_id}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def fetch_match_events(self, fixture_id):
        """Fetch events (goals, cards, etc.) for a specific match"""
        url = f"{self.BASE_URL}/fixtures/events"
        params = {"fixture": fixture_id}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def save_graph(self, filename="live_match_graph.png"):
        """Save the current graph to a file"""
        plt.savefig(filename)
        plt.close()
        print(f"Graph saved as {filename}")
    
    def visualize_match_stats(self, stats_data, save=True):
        """Visualize match statistics"""
        if not stats_data.get('response'):
            print("No statistics available for this match")
            return
        
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
        
        # Add labels and title
        ax.set_xlabel('Statistics', fontweight='bold')
        ax.set_ylabel('Value', fontweight='bold')
        ax.set_title(f'Live Match Statistics: {home_team} vs {away_team}', fontweight='bold')
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
        
        if save:
            self.save_graph("live_match_stats.png")
        else:
            plt.show()
    
    def visualize_match_events(self, events_data, save=True):
        """Visualize match events timeline"""
        if not events_data.get('response'):
            print("No events available for this match")
            return
        
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
        if events:
            home_team = events[0]['team']['name']
            away_team = events[0]['team']['name']  # This should be the away team, but API might not provide it directly
            
            for event in events:
                if event['team']['id'] != events[0]['team']['id']:
                    away_team = event['team']['name']
                    break
            
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
        
        # Add labels and title
        ax.set_xlabel('Match Time (minutes)', fontweight='bold')
        ax.set_title('Match Events Timeline', fontweight='bold')
        
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
        
        if save:
            self.save_graph("match_events_timeline.png")
        else:
            plt.show()
    
    def visualize_possession_pie(self, stats_data, save=True):
        """Create a pie chart showing ball possession"""
        if not stats_data.get('response'):
            print("No statistics available for this match")
            return
        
        # Extract team names and possession stats
        home_team = stats_data['response'][0]['team']['name']
        away_team = stats_data['response'][1]['team']['name']
        
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
        
        # Add title
        ax.set_title('Ball Possession', fontsize=16, fontweight='bold')
        
        if save:
            self.save_graph("possession_pie_chart.png")
        else:
            plt.show()
    
    def visualize_shots_comparison(self, stats_data, save=True):
        """Create a bar chart comparing shots statistics"""
        if not stats_data.get('response'):
            print("No statistics available for this match")
            return
        
        # Extract team names and shots stats
        home_team = stats_data['response'][0]['team']['name']
        away_team = stats_data['response'][1]['team']['name']
        
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
        
        # Add labels and title
        ax.set_xlabel('Teams', fontweight='bold')
        ax.set_ylabel('Number of Shots', fontweight='bold')
        ax.set_title('Shot Statistics', fontweight='bold')
        
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
        
        if save:
            self.save_graph("shots_comparison.png")
        else:
            plt.show()

def main():
    visualizer = LiveMatchVisualizer()
    
    try:
        # Search for León vs Monterrey match in Liga MX
        print("Searching for León vs Monterrey match in Liga MX Clausura...")
        match = visualizer.fetch_match_by_teams("Liga MX", "León", "Monterrey")
        
        if match:
            fixture_id = match['fixture']['id']
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            score = f"{match['goals']['home']} - {match['goals']['away']}"
            status = match['fixture']['status']['elapsed']
            
            print(f"Found live match: {home_team} {score} {away_team} ({status}')")
            
            # Fetch match statistics
            print("Fetching match statistics...")
            stats_data = visualizer.fetch_match_statistics(fixture_id)
            
            # Fetch match events
            print("Fetching match events...")
            events_data = visualizer.fetch_match_events(fixture_id)
            
            # Visualize match data
            print("Creating visualizations...")
            visualizer.visualize_match_stats(stats_data)
            visualizer.visualize_match_events(events_data)
            visualizer.visualize_possession_pie(stats_data)
            visualizer.visualize_shots_comparison(stats_data)
            
            print("\nAll visualizations have been saved as PNG files.")
        else:
            print("Match not found or not currently live. Using sample data instead.")
            
            # Create sample visualizations
            print("Creating sample visualizations...")
            
            # Sample match stats
            sample_stats = {
                'response': [
                    {
                        'team': {'name': 'León'},
                        'statistics': [
                            {'type': 'Ball Possession', 'value': '45%'},
                            {'type': 'Total Shots', 'value': '8'},
                            {'type': 'Shots on Goal', 'value': '3'},
                            {'type': 'Passes %', 'value': '85%'},
                            {'type': 'Fouls', 'value': '12'},
                            {'type': 'Corner Kicks', 'value': '4'}
                        ]
                    },
                    {
                        'team': {'name': 'Monterrey'},
                        'statistics': [
                            {'type': 'Ball Possession', 'value': '55%'},
                            {'type': 'Total Shots', 'value': '12'},
                            {'type': 'Shots on Goal', 'value': '5'},
                            {'type': 'Passes %', 'value': '88%'},
                            {'type': 'Fouls', 'value': '10'},
                            {'type': 'Corner Kicks', 'value': '6'}
                        ]
                    }
                ]
            }
            
            # Sample match events
            sample_events = {
                'response': [
                    {
                        'time': {'elapsed': 9},
                        'team': {'id': 1, 'name': 'Monterrey'},
                        'player': {'name': 'I. Fimbres'},
                        'type': 'Goal',
                        'detail': 'Normal Goal'
                    },
                    {
                        'time': {'elapsed': 15},
                        'team': {'id': 2, 'name': 'León'},
                        'player': {'name': 'Player A'},
                        'type': 'Card',
                        'detail': 'Yellow Card'
                    },
                    {
                        'time': {'elapsed': 35},
                        'team': {'id': 1, 'name': 'Monterrey'},
                        'player': {'name': 'Player B'},
                        'type': 'Card',
                        'detail': 'Yellow Card'
                    }
                ]
            }
            
            visualizer.visualize_match_stats(sample_stats)
            visualizer.visualize_match_events(sample_events)
            visualizer.visualize_possession_pie(sample_stats)
            visualizer.visualize_shots_comparison(sample_stats)
            
            print("\nSample visualizations have been saved as PNG files.")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        
    print("\nTo view the visualizations, open the PNG files in your file explorer.")

if __name__ == "__main__":
    main()
