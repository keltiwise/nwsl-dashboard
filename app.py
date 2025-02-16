import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import streamlit as st
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle, Arc
import matplotlib.pyplot as plt
import seaborn as sns

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
    
    # Filter teams based on season (Remove Bay FC if season is before 2024)
    if int(selected_season) < 2024:
        team_list = list(merged_df[merged_df.team_name != "Bay FC"].team_name.unique())
    else:
        team_list = list(merged_df.team_name.unique())

    # Dropdown for team selection
    selected_team = st.selectbox('Select a team', team_list, index=len(team_list) - 1)
    
    # Dropdown for season selection (using season_name)
    season_list = sorted(merged_df.season_name.unique())
    selected_season = st.selectbox('Select a season', season_list, index=len(season_list) - 1)
    
    # Filter the DataFrame based on the selected team and season.
    # If "Goals" is selected, filter for rows where goal == 1 and own_goal != 1.
    if viz_type == "Goals":
        df_filtered = merged_df[
            (merged_df["goal"] == 1) &
            (merged_df["own_goal"] != 1) &
            (merged_df["season_name"] == selected_season) &
            (merged_df.team_name == selected_team)
        ]
    else:  # "All Shots"
        df_filtered = merged_df[
            (merged_df["season_name"] == selected_season) &
            (merged_df.team_name == selected_team)
        ]
        
# --- Main Page ---
st.header(f"{selected_team.replace('_', ' ')} {selected_season} {viz_type} Heatmap")

if st.button("Show Heatmap"):
    if viz_type == "Goals":
        fig = make_goals_heatmap(df_filtered, selected_team, selected_season)
    else:
        fig = make_heatmap(df_filtered, selected_team, selected_season)
    st.pyplot(fig)

col = st.columns((1.5, 4.5, 2), gap='medium')

# Column 0: Summary Metrics
with col[0]:
    st.markdown("### Visualization Summary")
    st.markdown(f"**Team:** {selected_team.replace('_', ' ')}")
    st.markdown(f"**Season:** {selected_season}")
    st.markdown(f"**Type:** {viz_type}")
    total_events = df_filtered.shape[0]
    if viz_type == "Goals":
        st.metric(label="Total Goals", value=total_events)
    else:
        st.metric(label="Total Shots", value=total_events)

# Column 1: Heatmap Visualization (Removed extra button)
with col[1]:
    st.header(f"{selected_team.replace('_', ' ')} {selected_season} {viz_type} Heatmap")
    st.info("Click the button above to display the heatmap.")

# Column 2: Additional Insights
with col[2]:
    st.markdown("### Additional Insights")
    if "shot_distance" in df_filtered.columns:
        avg_distance = df_filtered["shot_distance"].mean()
        st.metric(label="Avg. Shot Distance", value=f"{avg_distance:.1f}")
    else:
        st.write("No additional metrics available.")
