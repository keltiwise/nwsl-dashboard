# import libraries
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

# set up page configuration for StreamLit
st.set_page_config(
    page_title="NWSL Dashboard", # page title
    layout="wide", # wide layout
    initial_sidebar_state="expanded")
alt.themes.enable("dark")

# adding custom styling with HTML and CSS
st.markdown("""
<style>
[data-testid="block-container"] {
    padding-left: 2rem; # padding to the left
    padding-right: 2rem; # padding to the right
    padding-top: 1rem; # padding to the top
    padding-bottom: 0rem; # padding to the bottom
    margin-bottom: -7rem; # adjusting bottom margin to include visualizations
}

# remove padding from vertical blocks
[data-testid="stVerticalBlock"] {
    padding-left: 0rem; # remove left padding
    padding-right: 0rem; # remove right padding
}

# style background and text alignment
[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

# center the label inside the metric component
[data-testid="stMetricLabel"] {
  display: flex; # flexbox for layout
  justify-content: center; # center text alignment
  align-items: center; # center text alignment
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
""", unsafe_allow_html=True) # allow HTML content to be added to page

# import all CSV files gathered from API
games = pd.read_csv("games_ids_2024.csv")
shots = pd.read_csv("shots_data_2024.csv")
teams = pd.read_csv("team_ids_2024.csv")

# adding team_name to shots column to easily identify which team is shooting which will then 
# lead to sorting data by name
# merge the 'shots' DataFrame with the 'teams' DataFrame based on 'team_id'
merged_df = pd.merge(shots, teams[['team_id', 'team_name']], on='team_id', how='left')

# merge the shots dataframe with the games dataframe on the gameid and keep season name
merged_df = pd.merge(merged_df, games[['game_id', 'season_name']], on = 'game_id', how = 'left')

# define the heatmap function for all shots
def make_heatmap(shots_df, team_name, season_name, half = "first", cmap="turbo", bw_adjust=0.3, levels=10,
                 figsize=(12, 8), dpi=400):
    """
    creates a soccer field heatmap using shot location data.
    
    parameters:
        shots_df (DataFrame): DataFrame with shot locations.
                              must include 'shot_location_x' and 'shot_location_y' columns.
        team_name (str): the team name (used in the title).
        season_name (str): the season (used in the title).
        cmap (str): color map for the heatmap.
        bw_adjust (float): bandwidth adjustment for the KDE plot.
        levels (int): number of contour levels.
        figsize (tuple): size of the figure.
        dpi (int): resolution of the figure.
    
    Returns:
        fig: the Matplotlib figure with the heatmap.
    """

    # Filter shots by half
    if half == "first":
        shots_df = shots_df[shots_df["period_id"] == 1]
    elif half == "second":
        shots_df = shots_df[shots_df["period_id"] == 2]
    else:
        raise ValueError("Half must be either 'first' or 'second'.")

    # clear current figure for new image
    plt.clf()
    # create a new figure and subplots with size and resolution
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # set the background color to white
    fig.patch.set_facecolor('white')
    # set the background color of plot area to white
    ax.set_facecolor('white')
    # equal scaling on both axes
    ax.set_aspect('equal')
    
    # remove axes details
    # hide all borders of axes
    for spine in ax.spines.values():
        spine.set_visible(False)
    # remove tick marks from top and bottom
    ax.tick_params(bottom=False, left=False)
    # remove x and y ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # set field limits and invert the y-axis for a field-like layout
    # horizonal line
    plt.xlim([10, 90])
    # vertical line
    plt.ylim([60, 105])
    # invert the y axis to align with plot
    ax.invert_yaxis()
    
    # draw the field background (touchline)
    ax.add_patch(Rectangle((0, 0), 100, 100, ec=mcolors.CSS4_COLORS['black'], 
                           fc=mcolors.CSS4_COLORS['white'], lw=5))
    
    # plot the heatmap of shots using a kernel density estimate
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
    plt.title(f"{team_name.replace('_', ' ')} {season_name} {half.capitalize()} Half Shot Heatmap", fontsize=16, weight='bold', pad=20)
    plt.text(50, 60, f"Visualizing {half.capitalize()} Half Shots", fontsize=12, color='gray', ha='center')
    
    return fig

# Define the heatmap function for goals only
def make_goals_heatmap(goals_df, team_name, season_name, half = "first", cmap="turbo", bw_adjust=0.3, levels=10,
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

    # Filter goals by half
    if half == "first":
        goals_df = goals_df[goals_df["period_id"] == 1]
    elif half == "second":
        goals_df = goals_df[goals_df["period_id"] == 2]
    else:
        raise ValueError("Half must be either 'first' or 'second'.")
    
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
    plt.title(f"{team_name.replace('_', ' ')} {season_name} {half.capitalize()} Half Goal Heatmap", fontsize=16, weight='bold', pad=20)
    plt.text(50, 60, f"Visualizing {half.capitalize()} Half Goals", fontsize=12, color='gray', ha='center')

    
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

    # Dropdown for selecting first or second half
    half = st.selectbox("Select Half", ["First Half", "Second Half"], index=0)

# Convert the half to 'first' or 'second' for use in the heatmap function
half = 'first' if half == "First Half" else 'second'

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
st.markdown(f"<h1 style='text-align: center;'>{selected_team.replace('_', ' ')} {selected_season} {viz_type} Heatmap</h1>", unsafe_allow_html=True)

# Automatically show heatmap without a button
# Automatically show heatmap without a button
if viz_type == "Goals":
    fig = make_goals_heatmap(df_filtered, selected_team, selected_season, half=half)
else:
    fig = make_heatmap(df_filtered, selected_team, selected_season, half=half)


# Display the heatmap
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
    
# Column 1: Heatmap Visualization (Removed extra button)
with col[1]:
    # Removed title for this column
    
    # Get the team name as it should appear on the dashboard (e.g., "NJ/NY Gotham FC")
    team_display_name = selected_team  
    
    # Replace '/' with ':' to match the corresponding file name in the Logos folder
    file_team_name = selected_team.replace("/", ":")
    
    # Construct the file path for the team logo
    logo_path = os.path.join("Logos", f"{file_team_name}.png")
    
    # Check if the logo file exists; if it does, display the image
    if os.path.exists(logo_path):
        st.image(logo_path, width=400)  # Adjust the image width as necessary
    else:
        # If the logo is not found, display a warning message
        st.warning(f"Logo for {team_display_name} not found.")

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

    if not df_filtered.empty:
        total_shots = len(df_filtered)

        # Average Shot Distance
        if "distance_from_goal_yds" in df_filtered.columns:
            avg_distance = df_filtered["distance_from_goal_yds"].mean()
            styled_metric("Avg. Shot Distance", f"{avg_distance:.1f}", " yds")

        # Most Common Shot Yard
        if "distance_from_goal_yds" in df_filtered.columns:
            common_shot_distance = df_filtered["distance_from_goal_yds"].mode().iloc[0]
            styled_metric("Most Common Shot Yard", f"{common_shot_distance:.1f}", " yds")

        # Average xG (Expected Goals)
        if "shot_xg" in df_filtered.columns:
            avg_xg = df_filtered["shot_xg"].mean()
            styled_metric("Avg. xG per Shot (Expected Goals)", f"{avg_xg:.2f}")

        # Goal Percentage
        if "goal" in df_filtered.columns:
            total_goals = df_filtered["goal"].sum()
            goal_percentage = (total_goals / total_shots) * 100 if total_shots > 0 else 0
            styled_metric("Goal Percentage", f"{goal_percentage:.1f}", "%")

        # Percentage of Headers
        if "head" in df_filtered.columns:
            header_shots = df_filtered["head"].sum()
            header_percentage = (header_shots / total_shots) * 100 if total_shots > 0 else 0
            styled_metric("Headers", f"{header_percentage:.1f}", "%")

        # Shot Accuracy (Shots on Target)
        if "goal" in df_filtered.columns and "blocked" in df_filtered.columns:
            shots_on_target = df_filtered["goal"].sum() + df_filtered["blocked"].sum()
            shot_accuracy = (shots_on_target / total_shots) * 100 if total_shots > 0 else 0
            styled_metric("Shot Accuracy", f"{shot_accuracy:.1f}", "%")

        # Most Common Assist Type
        if "assist_through_ball" in df_filtered.columns and "assist_cross" in df_filtered.columns:
            through_balls = df_filtered["assist_through_ball"].sum()
            crosses = df_filtered["assist_cross"].sum()
            assist_type = "Through Balls" if through_balls > crosses else "Crosses"
            styled_metric("Most Common Assist Type", assist_type)

        # Average Game Minute for Shots
        if "game_minute" in df_filtered.columns:
            avg_game_minute = df_filtered["game_minute"].mean()
            styled_metric("Avg. Game Minute for Shots", f"{avg_game_minute:.1f}", " min")

        # Period Distribution
        if "period_id" in df_filtered.columns:
            most_common_period = df_filtered["period_id"].mode().iloc[0]
            styled_metric("Most Common Half", f"Half {most_common_period}")

    else:
        st.write("No additional metrics available.")
