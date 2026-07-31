import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.config import API_KEY

class FootballDataVisualizer:
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self):
        self.headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "v3.football.api-sports.io"
        }
    
    def fetch_data(self, endpoint, params=None):
        """Fetch data from the API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def save_graph(self, filename="football_graph.png"):
        """Save the current graph to a file instead of showing it"""
        plt.savefig(filename)
        plt.close()
        print(f"Graph saved as {filename}")
    
    def bar_chart_example(self, save=True):
        """Create a bar chart with sample data"""
        print("Creating bar chart...")
        
        # Sample data - team statistics
        teams = ['Manchester City', 'Liverpool', 'Chelsea', 'Arsenal', 'Tottenham']
        goals_scored = [85, 78, 65, 62, 58]
        goals_conceded = [25, 30, 35, 40, 45]
        
        # Set up the figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Set the width of the bars
        bar_width = 0.35
        
        # Set the positions of the bars on the x-axis
        r1 = np.arange(len(teams))
        r2 = [x + bar_width for x in r1]
        
        # Create the bars
        ax.bar(r1, goals_scored, width=bar_width, label='Goals Scored', color='green')
        ax.bar(r2, goals_conceded, width=bar_width, label='Goals Conceded', color='red')
        
        # Add labels and title
        ax.set_xlabel('Teams', fontweight='bold')
        ax.set_ylabel('Goals', fontweight='bold')
        ax.set_title('Goals Scored vs Goals Conceded by Top Teams', fontweight='bold')
        ax.set_xticks([r + bar_width/2 for r in range(len(teams))])
        ax.set_xticklabels(teams, rotation=45, ha='right')
        
        # Add a legend
        ax.legend()
        
        # Add grid lines
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add value labels on top of bars
        for i, v in enumerate(goals_scored):
            ax.text(i - 0.1, v + 1, str(v), color='black', fontweight='bold')
            
        for i, v in enumerate(goals_conceded):
            ax.text(i + bar_width - 0.1, v + 1, str(v), color='black', fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
        if save:
            self.save_graph("bar_chart_example.png")
        else:
            plt.show()
    
    def pie_chart_example(self, save=True):
        """Create a pie chart with sample data"""
        print("Creating pie chart...")
        
        # Sample data - match outcome probabilities
        labels = ['Home Win', 'Draw', 'Away Win']
        sizes = [45, 25, 30]
        colors = ['lightgreen', 'lightblue', 'coral']
        explode = (0.1, 0, 0)  # explode the 1st slice
        
        # Create the pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=140)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Add title
        ax.set_title('Match Outcome Probability Distribution', fontsize=16, fontweight='bold')
        
        if save:
            self.save_graph("pie_chart_example.png")
        else:
            plt.show()
    
    def line_chart_example(self, save=True):
        """Create a line chart with sample data"""
        print("Creating line chart...")
        
        # Sample data - team performance over 10 matches
        matches = list(range(1, 11))
        team_a_points = [0, 3, 6, 7, 10, 13, 16, 17, 20, 23]
        team_b_points = [3, 6, 7, 10, 10, 13, 13, 16, 19, 22]
        team_c_points = [3, 3, 6, 9, 12, 12, 15, 18, 19, 20]
        
        # Create the line chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the lines
        ax.plot(matches, team_a_points, marker='o', linewidth=2, label='Team A')
        ax.plot(matches, team_b_points, marker='s', linewidth=2, label='Team B')
        ax.plot(matches, team_c_points, marker='^', linewidth=2, label='Team C')
        
        # Add labels and title
        ax.set_xlabel('Match Number', fontweight='bold')
        ax.set_ylabel('Points', fontweight='bold')
        ax.set_title('Team Performance Over 10 Matches', fontsize=16, fontweight='bold')
        
        # Add grid lines
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add a legend
        ax.legend()
        
        # Set x-axis ticks
        ax.set_xticks(matches)
        
        if save:
            self.save_graph("line_chart_example.png")
        else:
            plt.show()
    
    def stacked_bar_chart_example(self, save=True):
        """Create a stacked bar chart with sample data"""
        print("Creating stacked bar chart...")
        
        # Sample data - match statistics
        teams = ['Team A', 'Team B', 'Team C', 'Team D', 'Team E']
        wins = [8, 7, 6, 5, 4]
        draws = [2, 3, 4, 5, 6]
        losses = [2, 2, 2, 2, 2]
        
        # Create the stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the bars
        ax.bar(teams, wins, label='Wins', color='green')
        ax.bar(teams, draws, bottom=wins, label='Draws', color='blue')
        ax.bar(teams, losses, bottom=[i+j for i,j in zip(wins, draws)], label='Losses', color='red')
        
        # Add labels and title
        ax.set_xlabel('Teams', fontweight='bold')
        ax.set_ylabel('Number of Matches', fontweight='bold')
        ax.set_title('Match Results by Team', fontsize=16, fontweight='bold')
        
        # Add a legend
        ax.legend()
        
        # Add value labels
        for i, team in enumerate(teams):
            # Label for wins
            ax.text(i, wins[i]/2, str(wins[i]), ha='center', va='center', color='white', fontweight='bold')
            
            # Label for draws
            ax.text(i, wins[i] + draws[i]/2, str(draws[i]), ha='center', va='center', color='white', fontweight='bold')
            
            # Label for losses
            ax.text(i, wins[i] + draws[i] + losses[i]/2, str(losses[i]), 
                   ha='center', va='center', color='white', fontweight='bold')
        
        if save:
            self.save_graph("stacked_bar_chart_example.png")
        else:
            plt.show()
    
    def radar_chart_example(self, save=True):
        """Create a radar chart with sample data"""
        print("Creating radar chart...")
        
        # Sample data - player statistics
        categories = ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physical']
        
        # Values for two players (scale of 0-100)
        player1_stats = [95, 88, 82, 90, 45, 75]
        player2_stats = [80, 92, 85, 78, 50, 85]
        
        # Number of categories
        N = len(categories)
        
        # Create angles for each category
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Add the stats for the loop closure
        player1_stats += player1_stats[:1]
        player2_stats += player2_stats[:1]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        # Draw the lines and fill the areas
        ax.plot(angles, player1_stats, 'o-', linewidth=2, label='Player 1')
        ax.fill(angles, player1_stats, alpha=0.25)
        
        ax.plot(angles, player2_stats, 'o-', linewidth=2, label='Player 2')
        ax.fill(angles, player2_stats, alpha=0.25)
        
        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        # Set radial limits
        ax.set_ylim(0, 100)
        
        # Add a legend
        ax.legend(loc='upper right')
        
        # Add title
        plt.title('Player Comparison', size=20, fontweight='bold')
        
        if save:
            self.save_graph("radar_chart_example.png")
        else:
            plt.show()

def main():
    visualizer = FootballDataVisualizer()
    
    try:
        # Create different types of charts
        visualizer.bar_chart_example()
        visualizer.pie_chart_example()
        visualizer.line_chart_example()
        visualizer.stacked_bar_chart_example()
        visualizer.radar_chart_example()
        
        print("\nAll graphs have been saved as PNG files in the current directory.")
        print("\nTo show different types of graphs for API data, you can:")
        print("1. Use matplotlib for static graphs (bar, line, pie charts)")
        print("2. Use seaborn for more advanced statistical visualizations")
        print("3. Use plotly for interactive graphs")
        print("4. Use dash for creating web dashboards with your graphs")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()


