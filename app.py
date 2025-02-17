import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import streamlit as st
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle, Arc
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

st.set_page_config(
    page_title="NWSL Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")
alt.themes.enable("dark")

st.markdown("""
<style>
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}
[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}
[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}
[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
</style>
""", unsafe_allow_html=True)

# Import all CSV files gathered from API
games = pd.read_csv("games_ids_2024.csv")
shots = pd.read_csv("shots_data_2024.csv")
teams = pd.read_csv("team_ids_2024.csv")

# Adding team_name to shots column to easily identify which team is shooting which will then 
# lead to sorting data by name
# Merge the 'shots' DataFrame with the 'teams' DataFrame based on 'team_id'
merged_df = pd.merge(shots, teams[['team_id', 'team_name']], on='team_id', how='left')
# Merge the shots dataframe with the games dataframe on the gameid and keep season name
merged_df = pd.merge(merged_df, games[['game_id', 'season_name']], on = 'game_id', how = 'left')


# Define the heatmap function for all shots
def make_heatmap(shots_df, team_name, season_name, cmap="turbo", bw_adjust=0.3, levels=10,
                 figsize=(12, 8), dpi=400):
    """
    Creates a soccer field heatmap using shot location data.
    
    Parameters:
        shots_df (DataFrame): DataFrame with shot locations.
                              Must include 'shot_location_x' and 'shot_location_y' columns.
        team_name (str): The team name (used in the title).
        season_name (str): The season (used in the title).
        cmap (str): Color map for the heatmap.
        bw_adjust (float): Bandwidth adjustment for the KDE plot.
        levels (int): Number of contour levels.
        figsize (tuple): Size of the figure.
        dpi (int): Resolution of the figure.
    
    Returns:
        fig: The Matplotlib figure with the heatmap.
    """
    plt.clf()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.set_aspect('equal')
    
    # Remove axes details
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Set field limits and invert the y-axis for a field-like layout
    plt.xlim([10, 90])
    plt.ylim([60, 105])
    ax.invert_yaxis()
    
    # Draw the field background (touchline)
    ax.add_patch(Rectangle((0, 0), 100, 100, ec=mcolors.CSS4_COLORS['black'], 
                           fc=mcolors.CSS4_COLORS['white'], lw=5))
    
    # Plot the heatmap of shots using a kernel density estimate
    sns.kdeplot(
        x=shots_df["shot_location_y"],
        y=shots_df["shot_location_x"],
        cmap=cmap,
        shade=True,
        levels=levels,
        bw_adjust=bw_adjust,
        alpha=0.8,
        antialiased=True,
        ax=ax
    )
    
    # Cover areas beyond the playing zone if needed
    ax.add_patch(Rectangle((0, 100), 100, 10, ec=None, fc=mcolors.CSS4_COLORS['white']))
    
    # Draw additional field elements:
    # Endline
    ax.add_patch(Rectangle((0, 50), 100, 50, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # 18-yard box
    ax.add_patch(Rectangle((21, 82), 58, 18, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # 6-yard box
    ax.add_patch(Rectangle((37, 94), 26, 6, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # Goal
    ax.add_patch(Rectangle((45, 100), 10, 1, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # Penalty arc
    ax.add_artist(Arc((50, 88), 28, 18, angle=0, theta1=210, theta2=330, 
                      ec=mcolors.CSS4_COLORS['black'], lw=4))
    
    # Add title and subtitle
    plt.title(f"{team_name.replace('_', ' ')} {season_name} Shot Heatmap", fontsize=16, weight='bold', pad=20)
    plt.text(50, 60, "Visualizing All Shots", fontsize=12, color='gray', ha='center')
    
    return fig

# Define the heatmap function for goals only
def make_goals_heatmap(goals_df, team_name, season_name, cmap="turbo", bw_adjust=0.3, levels=10,
                       figsize=(12, 8), dpi=400):
    """
    Creates a soccer field heatmap using goal shot location data.
    
    Parameters:
        goals_df (DataFrame): DataFrame with goal shot locations.
                              Must include 'shot_location_x' and 'shot_location_y' columns.
        team_name (str): The team name (used in the title).
        season_name (str): The season (used in the title).
        cmap (str): Color map for the heatmap.
        bw_adjust (float): Bandwidth adjustment for the KDE plot.
        levels (int): Number of contour levels.
        figsize (tuple): Size of the figure.
        dpi (int): Resolution of the figure.
        
    Returns:
        fig: The Matplotlib figure with the heatmap.
    """
    plt.clf()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.set_aspect('equal')
    
    # Remove axes details
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Set field limits and invert the y-axis for a field-like layout
    plt.xlim([10, 90])
    plt.ylim([60, 105])
    ax.invert_yaxis()
    
    # Draw the field background (touchline)
    ax.add_patch(Rectangle((0, 0), 100, 100, ec=mcolors.CSS4_COLORS['black'], 
                           fc=mcolors.CSS4_COLORS['white'], lw=5))
    
    # Plot the heatmap using a kernel density estimate for goal locations
    sns.kdeplot(
        x=goals_df["shot_location_y"],
        y=goals_df["shot_location_x"],
        cmap=cmap,
        shade=True,
        levels=levels,
        bw_adjust=bw_adjust,
        alpha=0.8,
        antialiased=True,
        ax=ax
    )
    
    # Cover areas beyond the playing zone if needed
    ax.add_patch(Rectangle((0, 100), 100, 10, ec=None, fc=mcolors.CSS4_COLORS['white']))
    
    # Draw additional field elements:
    # Endline
    ax.add_patch(Rectangle((0, 50), 100, 50, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # 18-yard box
    ax.add_patch(Rectangle((21, 82), 58, 18, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # 6-yard box
    ax.add_patch(Rectangle((37, 94), 26, 6, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # Goal
    ax.add_patch(Rectangle((45, 100), 10, 1, ec=mcolors.CSS4_COLORS['black'], fill=False, lw=4))
    # Penalty arc
    ax.add_artist(Arc((50, 88), 28, 18, angle=0, theta1=210, theta2=330,
                      ec=mcolors.CSS4_COLORS['black'], lw=4))
    
    # Add title and subtitle
    plt.title(f"{team_name.replace('_', ' ')} {season_name} Goal Heatmap", fontsize=16, weight='bold', pad=20)
    plt.text(50, 60, "Visualizing All Goals", fontsize=12, color='gray', ha='center')
    
    return fig
# --- Streamlit Sidebar ---
with st.sidebar:
    st.title('NWSL Dashboard')

    # Visualization type selection
    viz_type = st.selectbox('Select Visualization Type', ['All Shots', 'Goals'])

    # Define active years for each team
    team_years = {
        "Chicago Stars FC": (2013, 2024),
        "Bay FC": (2024, 2024),
        "Boston Breakers": (2013, 2017),
        "Houston Dash": (2014, 2024),
        "Kansas City Current": (2021, 2024),
        "NJ/NY Gotham FC": (2013, 2024),
        "North Carolina Courage": (2017, 2024),
        "Orlando Pride": (2016, 2024),
        "Portland Thorns FC": (2013, 2024),
        "Racing Louisville FC": (2021, 2024),
        "San Diego Wave FC": (2022, 2024),
        "Washington Spirit": (2013, 2024),
        "Western New York Flash": (2013, 2016),
        "Seattle Reign FC": (2013, 2018),
        "Utah Royals FC": (2018, 2020),
        "Angel City FC": (2022, 2024),
        "FC Kansas City": (2013, 2017)
    }

    # Dropdown for season selection (sorted and removing NaN values)
    season_list = sorted([int(s) for s in merged_df.season_name.unique() if pd.notna(s)])  # Convert to int
    season_list = [str(s) for s in season_list]  # Convert to string for display
    selected_season = st.selectbox('Select a season', season_list, index=len(season_list) - 1)

    # Convert selected_season to an integer for safe comparisons
    selected_season = int(selected_season)

    # Filter teams dynamically based on their active years
    team_list = [team for team, (start, end) in team_years.items() if start <= selected_season <= end]

    # Ensure team list is not empty
    if not team_list:
        team_list = ["No Teams Available"]

    # Dropdown for team selection
    selected_team = st.selectbox('Select a team', team_list, index=0)

    # Handle edge case where no valid teams exist
    if selected_team == "No Teams Available":
        selected_team = "Unknown Team"

# Define the relevant columns to keep
columns_to_keep = [
    "goal", "own_goal", "blocked", "distance_from_goal_yds",  # Shot results
    "shot_xg", "shot_psxg",  # Expected goals metrics
    "assist_through_ball", "assist_cross",  # Assist types
    "head",  # Header or not
    "game_minute", "period_id", "home_score", "away_score",  # Game context
    "shot_location_x", "shot_location_y",  # Shot location
    "blocked_x", "blocked_y",  # Blocked shot location
    "team_name", "season_name", "shooter_player_id", "assist_player_id"  # Identifiers
]

# Filter the DataFrame based on the selected team and season
if viz_type == "Goals":
    df_filtered = merged_df[
        (merged_df["goal"] == 1) &
        (merged_df["own_goal"] != 1) &
        (merged_df["season_name"] == selected_season) &
        (merged_df["team_name"] == selected_team)
    ]
else:  # "All Shots"
    df_filtered = merged_df[
        (merged_df["season_name"] == selected_season) &
        (merged_df["team_name"] == selected_team)
    ]

# Keep only the necessary columns if they exist in the dataset
df_filtered = df_filtered[[col for col in columns_to_keep if col in df_filtered.columns]]


# --- Main Page ---
st.header(f"{selected_team.replace('_', ' ')} {selected_season} {viz_type} Heatmap")

# Automatically show heatmap without a button
if viz_type == "Goals":
    fig = make_goals_heatmap(df_filtered, selected_team, selected_season)
else:
    fig = make_heatmap(df_filtered, selected_team, selected_season)
st.pyplot(fig)

col = st.columns((1.5, 4.5, 2), gap='medium')

# Column 0: Summary Metrics
with col[0]:
    st.markdown("""
        <style>
        .metric-container {
            background-color: #1E88E5; /* Change this color */
            color: white;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### Visualization Summary")
    st.markdown(f"**Team:** {selected_team.replace('_', ' ')}")
    st.markdown(f"**Season:** {selected_season}")
    st.markdown(f"**Type:** {viz_type}")

    total_events = df_filtered.shape[0]
    metric_label = "Total Goals" if viz_type == "Goals" else "Total Shots"

    # Apply custom styling to the metric display
    st.markdown(f'<div class="metric-container">{metric_label}: {total_events}</div>', unsafe_allow_html=True)
    
logo_path = Path(f"Logos/{selected_team}.png")

# Column 1: Heatmap Visualization (Removed extra button)
with col[1]:
    st.markdown("### Team Logo")
    
    # Ensure team name formatting for logo file path
    safe_team_name = selected_team.replace("/", "_")  # Replace ':' with '/'
    
    # Construct the path to the logo file
    logo_path = os.path.join("Logos", f"{safe_team_name}.png")
    
    # Check if the logo file exists
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)  # Adjust width for a smaller display
    else:
        st.warning(f"Logo for {selected_team} not found.")


# Column 2: Additional Insights
with col[2]:
    st.markdown("### Additional Insights")

    # Define a function for styled metric display
    def styled_metric(label, value, unit=""):
        st.markdown(
            f"""
            <div style="
                background-color: #ffffff;  /* White background */
                padding: 10px;
                border-radius: 10px;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
                color: #333; /* Dark text */
                border: 1px solid #ddd; /* Light border */
                margin-bottom: 10px;">
                {label}: <span style="font-size: 20px; color: #007bff;">{value}{unit}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Average Shot Distance
    if "distance_from_goal_yds" in df_filtered.columns and not df_filtered.empty:
        avg_distance = df_filtered["distance_from_goal_yds"].mean()
        styled_metric("Avg. Shot Distance", f"{avg_distance:.1f}", " yds")

    # Average xG (Expected Goals)
    if "shot_xg" in df_filtered.columns and not df_filtered.empty:
        avg_xg = df_filtered["shot_xg"].mean()
        styled_metric("Avg. xG per Shot", f"{avg_xg:.2f}")

    # Percentage of Shots on Target (Goals + Blocked Shots)
    if "goal" in df_filtered.columns and "blocked" in df_filtered.columns and not df_filtered.empty:
        total_shots = len(df_filtered)
        shots_on_target = df_filtered["goal"].sum() + df_filtered["blocked"].sum()
        shot_accuracy = (shots_on_target / total_shots) * 100 if total_shots > 0 else 0
        styled_metric("Shot Accuracy", f"{shot_accuracy:.1f}", "%")

    # Percentage of Headers
    if "head" in df_filtered.columns and not df_filtered.empty:
        header_shots = df_filtered["head"].sum()
        header_percentage = (header_shots / total_shots) * 100 if total_shots > 0 else 0
        styled_metric("Headers", f"{header_percentage:.1f}", "%")

    # Assist Type Distribution
    if "assist_through_ball" in df_filtered.columns and "assist_cross" in df_filtered.columns and not df_filtered.empty:
        through_balls = df_filtered["assist_through_ball"].sum()
        crosses = df_filtered["assist_cross"].sum()
        assist_type = "Through Balls" if through_balls > crosses else "Crosses"
        styled_metric("Most Common Assist Type", assist_type)

    # If no relevant metrics available
    if df_filtered.empty:
        st.write("No additional metrics available.")



