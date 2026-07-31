
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from data_handler import *


def gui():
    base_dir = os.path.dirname(__file__)

    def load_players():
        league = league_var.get()
        season = int(season_var.get())
        player_combo.set("Loading...")
        player_combo["values"] = []
        root.after(100, lambda: update_player_combobox(league, season))

    player_id_map = {}

    def update_player_combobox(league, season):
        nonlocal player_id_map
        try:
            player_id_map = get_all_players(league, season)
            player_list = sorted(player_id_map.keys())
            player_combo["values"] = player_list
            player_combo.set(player_list[0] if player_list else "No players found")
        except Exception as e:
            player_combo.set(f"Error: {e}")

    root = tk.Tk()
    root.title("Football Stats Analyzer")
    root.geometry("1200x850")
    root.configure(bg='black')

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="black")
    style.configure("TLabel", background="black", foreground="white", font=("Segoe UI", 12))
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
    style.configure("TCombobox", fieldbackground="#fff", background="white", foreground="black")

    # --- Navbar ---
    nav_frame = tk.Frame(root, bg="black", height=70)
    nav_frame.pack(fill=tk.X)

    # Left: Logo + Title
    left_nav = tk.Frame(nav_frame, bg="black")
    left_nav.pack(side=tk.LEFT, padx=20)
    try:
        logo_path = os.path.join(base_dir, "assets", "foooot.jpg")
        logo_img = Image.open(logo_path).resize((40, 40))
        logo_photo = ImageTk.PhotoImage(logo_img)
        tk.Label(left_nav, image=logo_photo, bg="black").pack(side=tk.LEFT)
    except:
        pass
    tk.Label(left_nav, text="FOTBALL LAB", fg="white", bg="black", font=("Orbitron", 16, "bold")).pack(side=tk.LEFT, padx=10)

    # Center: Buttons
    help_popup = None

    def toggle_help_popup(event=None):
        nonlocal help_popup 

        if help_popup and help_popup.winfo_exists():
            help_popup.destroy()
            help_popup = None
            return

        help_popup = tk.Toplevel(bg="black")
        help_popup.overrideredirect(True)
        help_popup.attributes("-topmost", True)

        x = how_to_use_btn.winfo_rootx()
        y = how_to_use_btn.winfo_rooty() + how_to_use_btn.winfo_height()
        help_popup.geometry(f"700x500+{x}+{y}")

        def close_popup(event):
            if help_popup and not help_popup.winfo_containing(event.x_root, event.y_root):
                help_popup.destroy()

        help_popup.bind("<FocusOut>", lambda e: help_popup.destroy())
        help_popup.focus_force()
        help_popup.bind("<Button-1>", close_popup)

        canvas = tk.Canvas(help_popup, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        scroll_frame = tk.Frame(canvas, bg="black")
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollincrement=1)
        
        sections = [
            ("Getting Started", 
             "Football Lab provides comprehensive football analytics, matchup statistics, and player performance data.\n"
             "This guide will help you navigate through the various features of the platform."),
            ("Main Dashboard", 
             "→ League Card: Shows current league and season information.\n"
             "→ Match Card: Displays upcoming or selected match details.\n"
             "→ Player Card: Highlights featured player information."),
            ("Statistics Navigation",
             "→ Top Scorers: View leading goal scorers in the league.\n"
             "→ Top Assisters: Check players with most assists.\n"
             "→ League Standing: Current league table and points.\n"
             "→ Possession Pie: Possession statistics visualized.\n"
             "→ Passes Stats: Detailed passing analytics.\n"
             "→ Compact Stats: Condensed statistical overview.\n"
             "→ Match Info: Comprehensive match details.\n"
             "→ Player Radar: Player performance visualization."),
            ("Live Matches",
             "→ Click the 'Live Matches' button to view current matches\n"
             "→ Double-click any match to see detailed statistics\n"
             "→ Use the back button to return to the match list")
        ]
        
        for title, text in sections:
            frame = tk.Frame(scroll_frame, bg="#1c1c1c", bd=1, relief="solid")
            frame.pack(fill="x", padx=10, pady=5)

            tk.Label(frame, text=title, font=("Helvetica", 12, "bold"),
                    fg="#00BFFF", bg="#1c1c1c").pack(anchor="w", padx=10, pady=(5, 0))

            for line in text.split("\n"):
                tk.Label(frame, text=line, font=("Helvetica", 10),
                        fg="white", bg="#1c1c1c", wraplength=660, justify="left").pack(anchor="w", padx=20, pady=1)

        scroll_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    center_nav = tk.Frame(nav_frame, bg="black")
    center_nav.pack(side=tk.LEFT, expand=True)
    tk.Button(center_nav, text="Home", bg="black", fg="white", font=("Arial", 10, "italic"), bd=0).pack(side=tk.LEFT, padx=20)
    how_to_use_btn = tk.Button(center_nav, text="How to Use", bg="black", fg="white",
                            font=("Arial", 10, "italic"), bd=0, command=toggle_help_popup)
    how_to_use_btn.pack(side=tk.LEFT, padx=20)

    # Right: Profile Icon
    right_nav = tk.Frame(nav_frame, bg="black")
    right_nav.pack(side=tk.RIGHT, padx=20)
    tk.Label(right_nav, text="👤", font=("Arial", 14), bg="black", fg="white").pack()

    # Separator line
    tk.Frame(root, bg="white", height=2).pack(fill=tk.X)

    # Input Frame
    entry_frame = tk.Frame(root, bg="black")
    entry_frame.pack(pady=10)

    league_var = tk.StringVar()
    season_var = tk.StringVar()
    team1_var = tk.StringVar()
    team2_var = tk.StringVar()
    match_date_var = tk.StringVar()
    round_var = tk.StringVar()
    player_name_var = tk.StringVar()
        
    # Helper to add labeled combobox with tighter alignment
    def labeled_combobox(frame, label_text, variable, values=None, row=0):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="e", padx=(0, 5), pady=3)
        combo = ttk.Combobox(frame, textvariable=variable, values=values or [], width=25, state="readonly")
        combo.grid(row=row, column=1, padx=(0, 10), pady=3)
        return combo

    # League Frame
    league_frame = tk.Frame(entry_frame, bg="black")
    league_frame.grid(row=0, column=0, padx=30)
    try:
        league_path = os.path.join(base_dir, "assets", "Leagaue.png")
        league_img = Image.open(league_path).resize((160, 160))
        league_photo = ImageTk.PhotoImage(league_img)
        tk.Label(league_frame, image=league_photo, bg="black").grid(row=0, column=1, columnspan=2, pady=(0, 10))
    except:
        pass

    labeled_combobox(league_frame, "League:", league_var, list(LEAGUE_ID.keys()), row=1)
    labeled_combobox(league_frame, "Season:", season_var, get_seasons(), row=2)

    # Match Info Frame
    match_frame = tk.Frame(entry_frame, bg="black")
    match_frame.grid(row=0, column=1, padx=30)
    try:
        match_path = os.path.join(base_dir, "assets", "team1 vs team2.png")
        match_img = Image.open(match_path).resize((160, 160))
        match_photo = ImageTk.PhotoImage(match_img)
        tk.Label(match_frame, image=match_photo, bg="black").grid(row=0, column=1, columnspan=2, pady=(0, 10))
    except:
        pass

    team1_menu = labeled_combobox(match_frame, "Team 1:", team1_var, row=1)
    team2_menu = labeled_combobox(match_frame, "Team 2:", team2_var, row=2)

    ttk.Label(match_frame, text="Match Date:").grid(row=3, column=0, sticky="e", padx=(0, 5), pady=3)
    ttk.Entry(match_frame, textvariable=match_date_var, width=28).grid(row=3, column=1, padx=(0, 10), pady=3)

    labeled_combobox(match_frame, "Round:", round_var, get_round(), row=4)

    # Player Info Frame
    player_frame = tk.Frame(entry_frame, bg="black")
    player_frame.grid(row=0, column=2, padx=30)
    try:
        player_path = os.path.join(base_dir, "assets", "palyerStast.jpg")
        player_img = Image.open(player_path).resize((160, 160))
        player_photo = ImageTk.PhotoImage(player_img)
        tk.Label(player_frame, image=player_photo, bg="black").grid(row=0, column=1, columnspan=2, pady=(0, 10))
    except:
        pass

    ttk.Label(player_frame, text="Player Name:").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=3)
    player_combo = ttk.Combobox(player_frame, textvariable=player_name_var, width=25, state="readonly")
    player_combo.grid(row=1, column=1, padx=(0, 10), pady=3)

    ttk.Button(player_frame, text="Load Players", command=load_players).grid(row=2, column=0, columnspan=2, pady=5)

    # Update team list when league or season changes
    def update_teams(*args):
        if league_var.get() and season_var.get():
            teams = get_teams(league_var.get(), season_var.get())
            team1_menu['values'] = teams
            team2_menu['values'] = teams

    league_var.trace_add("write", update_teams)
    season_var.trace_add("write", update_teams)

    # Analyze Button
    ttk.Button(root, text="Analyze", command=lambda: submit_selection()).pack(pady=10)
    
    # Function to open the web dashboard
    import socket
    import subprocess
    import sys
    import time

    def open_web_dashboard():
        # Check if FastAPI server is running on port 8000
        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("127.0.0.1", port)) == 0

        fastapi_dir = os.path.abspath(os.path.join(base_dir, "..", "football_live_match"))
        server_running = is_port_in_use(8000)

        if not server_running:
            # Start FastAPI server in a new process
            subprocess.Popen(
                [sys.executable, "-m", "src.main"],
                cwd=fastapi_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )
            # Wait for the server to start
            for _ in range(20):
                if is_port_in_use(8000):
                    break
                time.sleep(0.5)

        # Open the web dashboard in the browser
        webbrowser.open("http://127.0.0.1:8000")

    # Live Matches Button with better styling
    live_btn = ttk.Button(
        root, 
        text="⚽ Live Matches", 
        command=open_web_dashboard,
        style="TButton"
    )
    live_btn.pack(pady=5)

  

        # Notebook Tabs for Plots
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tabs = {
        "Top Scorers": ttk.Frame(notebook),
        "Top Assisters": ttk.Frame(notebook),
        "League Standings": ttk.Frame(notebook),
        "Possession Pie": ttk.Frame(notebook),
        "Passes Pie": ttk.Frame(notebook),
        "Passes Stats": ttk.Frame(notebook),
        "Compact Stats": ttk.Frame(notebook),
        "Match Info": ttk.Frame(notebook),
        "Player Radar": ttk.Frame(notebook),
    }

    for title, tab in tabs.items():
        notebook.add(tab, text=title)

    def clear_tab(tab):
        for widget in tab.winfo_children():
            widget.destroy()

    def plot_figure(tab, fig):
        clear_tab(tab)
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def submit_selection():
        league = league_var.get()
        season = season_var.get()
        team1 = team1_var.get()
        team2 = team2_var.get()
        match_date = match_date_var.get()
        round = round_var.get()
        player_name = player_name_var.get()

        if team1 and team2 and match_date:
            figs = final_plot_stats_match(team1, team2, match_date, league, season)
            info = get_match_info(league, season, round)
            plot_figure(tabs["Possession Pie"], figs[0])
            plot_figure(tabs["Passes Pie"], figs[1])
            plot_figure(tabs["Passes Stats"], figs[2])
            plot_figure(tabs["Compact Stats"], figs[3])
            plot_figure(tabs["Match Info"], info)

        if player_name:
            player_id = player_id_map.get(player_name)
            if player_id:
                fig = plot_player_radar_by_id(player_id, league, season)
                plot_figure(tabs["Player Radar"], fig)
                notebook.select(tabs["Player Radar"])
            else:
                messagebox.showerror("Player ID Not Found", f"No ID found for player '{player_name}'")

        if league and season:
            plot_figure(tabs["Top Scorers"], get_top_scorers(season, league))
            plot_figure(tabs["Top Assisters"], get_top_assisters(league, season))
            plot_figure(tabs["League Standings"], get_league_standings(league, season))

    root.mainloop()

if __name__ == '__main__':
    gui()
