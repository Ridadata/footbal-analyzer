import requests
import pandas as pd
import matplotlib.pyplot as plt
from src.config import API_KEY

class FootballAPI:
    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self):
        self.headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "https://v3.football.api-sports.io"
        }

    def get_live_odds(self, fixture_id):
        url = f"{self.BASE_URL}/odds/live"
        params = {"fixture": fixture_id}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def visualize_odds(self, data):
        # Check if response contains data
        if not data['response'] or len(data['response']) == 0:
            print("No data available for visualization.")
            self.show_sample_graph()  # Show a sample graph instead
            return

        df = pd.json_normalize(data['response'])

        # Check if 'name' column exists
        if 'name' not in df.columns:
            print("Expected data structure not found. Showing sample graph instead.")
            self.show_sample_graph()
            return

        # Plot Over/Under Line odds
        over_under = df[df['name'] == 'Over/Under Line']
        if len(over_under) > 0:
            over_values = over_under[over_under['values.value'] == 'Over']
            under_values = over_under[over_under['values.value'] == 'Under']

            plt.figure(figsize=(10, 6))
            plt.bar(over_values['values.odd'], over_values['values.handicap'], label='Over')
            plt.bar(under_values['values.odd'], under_values['values.handicap'], label='Under')
            plt.xlabel('Odds')
            plt.ylabel('Handicap')
            plt.title('Over/Under Line Odds')
            plt.legend()
            plt.show()
        else:
            print("No Over/Under Line odds found. Showing sample graph instead.")
            self.show_sample_graph()

    def show_sample_graph(self):
        """Show a sample graph when no API data is available"""
        # Generate sample data
        categories = ['Home Win', 'Draw', 'Away Win']
        values = [2.5, 3.2, 2.8]

        # Create bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(categories, values, color=['green', 'blue', 'red'])
        plt.xlabel('Outcome')
        plt.ylabel('Odds')
        plt.title('Sample Football Match Odds')
        plt.ylim(0, 4)

        # Add value labels on top of bars
        for i, v in enumerate(values):
            plt.text(i, v + 0.1, str(v), ha='center')

        plt.show()

    def visualize_as_pie_chart(self, data):
        """Visualize odds data as a pie chart"""
        # Check if response contains data
        if not data['response'] or len(data['response']) == 0:
            print("No data available for visualization.")

            # Create sample pie chart
            labels = ['Home Win', 'Draw', 'Away Win']
            sizes = [45, 25, 30]
            colors = ['lightgreen', 'lightblue', 'coral']
            explode = (0.1, 0, 0)  # explode the 1st slice

            plt.figure(figsize=(8, 8))
            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct='%1.1f%%', shadow=True, startangle=140)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.title('Sample Win Probability Distribution')
            plt.show()
            return

        # If we have real data, process it here
        # This is a placeholder for actual implementation
        print("Pie chart with real data would be shown here")

def main():
    api = FootballAPI()
    try:
        # Test with a sample fixture ID
        fixture_id = "721238"  # You can change this to any valid fixture ID
        data = api.get_live_odds(fixture_id)
        print("API request successful!")
        print("Response data:", data)

        # Visualize the odds in different ways
        print("\n1. Bar Chart Visualization:")
        api.visualize_odds(data)

        print("\n2. Pie Chart Visualization:")
        api.visualize_as_pie_chart(data)

    except Exception as e:
        print(f"Error: {str(e)}")

    print("\nTo show different types of graphs for API data, you can:")
    print("1. Use matplotlib for static graphs (bar charts, line charts, pie charts)")
    print("2. Use seaborn for more advanced statistical visualizations")
    print("3. Use plotly for interactive graphs")
    print("4. Use dash for creating web dashboards with your graphs")

if __name__ == "__main__":
    main()



