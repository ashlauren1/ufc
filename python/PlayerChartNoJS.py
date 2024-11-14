import pandas as pd
from bs4 import BeautifulSoup
import os

# Paths to CSV files and directory containing HTML files
gamelogs_path = r'C:\Users\ashle\Documents\Projects\ufc\data\gamelogs.csv'
html_dir = r'C:\Users\ashle\Documents\Projects\ufc\fighters'

# Load the data
gamelogs_df = pd.read_csv(gamelogs_path, low_memory=False)
gamelogs_df['date'] = pd.to_datetime(gamelogs_df['date'])
gamelogs_df = gamelogs_df.sort_values(by='date')

# List of all stats to generate charts for
all_stats = ['SigStr', 'knockdowns', 'SigStrAtt', 'takedown', 'takedownAtt', 'subAtt', 'SigStrAg', 'SigStrAttAg', 'TDAg', 'TDAttAg', 'SubAttAg']

# Default betting line and stat
default_betting_line = 25.5
default_stat = "SigStr"

# Updated HTML template with an external JS file
chart_html_template = """
<div class="player-chart-container">
    <!-- Stat Selection Dropdown -->
    <div class="barChart-filters">
        <div class="barChartFilter">
            <label for="statSelector_{fighter_id}">Stat:</label>
            <select id="statSelector_{fighter_id}" onchange="updateStat('{fighter_id}', this.value)">
                {stat_options}
            </select>
        </div>  
        <div class="barChartFilter">
            <label for="startDate_{fighter_id}">Start:</label>
            <input type="date" id="startDate_{fighter_id}" onchange="applyFilters('{fighter_id}')">
        </div>
        <div class="barChartFilter">
            <label for="endDate_{fighter_id}">End:</label>
            <input type="date" id="endDate_{fighter_id}" onchange="applyFilters('{fighter_id}')">
        </div>
    </div>
    <canvas id="chart_{fighter_id}" class="player-barChart"></canvas>
    <div class="filter-buttons">
        <button id="L5_{fighter_id}" onclick="showRecentGames('{fighter_id}', 5)">L5</button>
        <button id="L10_{fighter_id}" onclick="showRecentGames('{fighter_id}', 10)">L10</button>
        <button id="L20_{fighter_id}" onclick="showRecentGames('{fighter_id}', 20)">L20</button>
        <button id="showAll_{fighter_id}" onclick="showAllGames('{fighter_id}')">All</button>
        <button id="fight_duration_{fighter_id}" onclick="toggleFightDurationOverlay('{fighter_id}')">Toggle Fight Duration</button>
        <button id="clearFiltersBtn_{fighter_id}" onclick="clearFilters('{fighter_id}')" class="clear-chart-filters">Clear Filters</button>
    </div>
    <div class="slider-container">
        <div id="line-slider">
            <label for="lineSlider_{fighter_id}">Change Line:</label>
            <input type="range" id="lineSlider_{fighter_id}" min="0" max="250" step="0.5" value="{betting_line}" oninput="updateLine('{fighter_id}', this.value)">
            <span id="lineValue_{fighter_id}">{betting_line}</span>
        </div>
        <div class="chartButtons">
            <button id="reset-line-btn_{fighter_id}" onclick="resetLine('{fighter_id}', {default_betting_line})" class="reset-line-btn">Reset Line</button>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.1.0"></script>
<script src="chartScript.js"></script>
<script>
    // Initialize the chart with player-specific data by calling a function from chart_logic.js
    initializeChart("{fighter_id}", {chart_data}, {betting_line}, "{default_stat}");
</script>
"""

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        fighter_id = filename.replace(".html", "")
                
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as file:
                soup = BeautifulSoup(file, "html.parser")

        # Select where to insert the chart based on table id
        player_table = soup.select_one("#table-container")
        if not player_table:
            print(f"No player table found in {filename}. Skipping.")
            continue

        # Filter gamelogs for the player
        player_gamelogs = gamelogs_df[gamelogs_df['fighterID'] == fighter_id]
        if player_gamelogs.empty:
            print(f"No gamelog data found for player {fighter_id} in {filename}")
            continue

        chart_data = [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                **{stat.replace("+", "_"): row[stat] for stat in all_stats if stat in row}  # Replace `+` with `_`
            }
            for _, row in player_gamelogs.iterrows()
        ]
        chart_data.sort(key=lambda x: x["date"])

        # Mapping of short stat codes to full names
        stat_map = {
            'SigStr': 'Significant Strikes', 
            'knockdowns': 'Knockdowns',
            'SigStrAtt': 'Significant Strike Attempts', 
            'takedown': 'Takedowns', 
            'takedownAtt': 'Takedown Attempts', 
            'subAtt': 'Submission Attempts',
            'SigStrAg': 'Significant Strikes Against',
            'SigStrAttAg': 'Significant Strike Attempts Against',
            'TDAg': 'Takedowns Against', 
            'TDAttAg': 'Takedown Attempts Against', 
            'SubAttAg': 'Submission Attempts Against'
        }
        stat_options = "\n".join([f'<option value="{stat}">{stat_map.get(stat, stat)}</option>' for stat in all_stats])

        chart_html = chart_html_template.format(
            fighter_id=fighter_id,
            stat_options=stat_options,
            chart_data=chart_data,
            betting_line=default_betting_line,
            default_stat=default_stat,
            default_betting_line=default_betting_line
        )
        chart_soup = BeautifulSoup(chart_html, "html.parser")
        player_table.insert_before(chart_soup)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

print("All files have been processed.")
