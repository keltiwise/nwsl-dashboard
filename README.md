
# NWSL Dashboard

## Overview
The NWSL Dashboard is an interactive Streamlit application for visualizing National Women's Soccer League (NWSL) shot and goal data. Users can explore shot locations, goal statistics, and generate heatmaps for different teams and seasons.

## Dashboard
https://nwsl-dashboard-wvsjsaylms2zezkxqpy8jy.streamlit.app/

## Features
- Select different NWSL seasons and teams for data visualization
- Display shot and goal heatmaps
- Interactive filtering based on season and team
- Team logos and summary statistics

## Installation

### Prerequisites
- Python 3.8+
- Streamlit
- Pandas
- Matplotlib

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/keltiwise/nwsl-dashboard.git
   cd nwsl-dashboard
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```
