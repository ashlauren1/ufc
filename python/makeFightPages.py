import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\ufc\data"
output_dir_fights = r"C:\Users\ashle\Documents\Projects\ufc\fights"

# Ensure output directory exists
os.makedirs(output_dir_fights, exist_ok=True)

# Load game logs data
gamelogs_csv = os.path.join(data_dir, "gamelogs.csv")
fight_data = pd.read_csv(gamelogs_csv, low_memory=False)

for _, row in fight_data.iterrows():
    event = row['event']
    event_id = row['eventID']
    fight_name = row['fight']
    fight_id = row['fightID']
    date = row['date']
    fight_location = row['location']
    weight_class = row['weight_class']
    scheduled_rounds = row['scheduled_rounds']
    result = row['result']
    fighter_name = row['fighter']
    fighter_id = row['fighterID']
    outcome	= row['outcome']
    fight_duration = row['fight_duration']

# Generate Individual Game Boxscore Pages
def create_fight_boxscores(fight_data, output_dir):
    grouped_data = fight_data.groupby('fightID')

    for fight_id, fight_data in grouped_data:
        fight_name = fight_data.iloc[0]['fight']
        weight_class = fight_data.iloc[0]['weight_class']
        scheduled_rounds = fight_data.iloc[0]['scheduled_rounds']
        fight_duration = fight_data.iloc[0]['fight_duration']
        date = fight_data.iloc[0]['date']
        fight_location = fight_data.iloc[0]['location']
        fighter_name = fight_data.iloc[0]['fighter']
        fighter_id = fight_data.iloc[0]['fighterID']
        round_duration = fight_data.iloc[0]['round_duration']
        home_data = fight_data[fight_data['Is_Home'] == 1]
        away_data = fight_data[fight_data['Is_Home'] == 0]
        fight_filename = f'{output_dir}/{fight_id}.html'

        
        def calculate_totals(data):
            totals = data[['round_duration', 'knockdowns', 'SigStr', 'SigStrAtt', 'totalStrikesLanded', 'totalStrikesAttempted', 'takedown', 'takedownAtt', 'subAtt', 'reversals', 'sigHeadStr', 'sigHeadStrAtt', 'sigBodyStr', 'sigBodyStrAtt', 'sigLegStr', 'sigLegStrAtt', 'clinchStrikes', 'clinchAttStr', 'groundStr', 'groundAttStr', 'SigStrAg', 'SigStrAttAg', 'TotStrAg', 'TotStrAttAg', 'TDAg', 'TDAttAg', 'SubAttAg']].sum()

            totals['StrAccuracy'] = (totals['SigStr'] / totals['SigStrAtt'] * 100) if totals['SigStrAtt'] > 0 else 0.0
            totals['SLPM'] = round((totals['SigStr'] / totals['round_duration']), 2) if totals['round_duration'] > 0 else 0.0
            totals['takedownAcc'] = (totals['takedown'] / totals['takedownAtt'] * 100) if totals['takedownAtt'] > 0 else 0.0
            totals['SigStrDef'] = (100-(totals['SigStrAg'] / totals['SigStrAttAg'] * 100)) if totals['SigStrAttAg'] > 0 else 0.0
            totals['TDDef'] = (100-(totals['TDAg'] / totals['TDAttAg'] * 100)) if totals['TDAttAg'] > 0 else 0.0
            
            return totals
        
        def calculate_rates(row):
            rates = {}
            
            rates['StrAccuracy'] = (row['SigStr'] / row['SigStrAtt'] * 100) if row['SigStrAtt'] > 0 else 0.0
            rates['SLPM'] = round((row['SigStr'] / row['round_duration']), 2) if row['round_duration'] > 0 else 0.0
            rates['takedownAcc'] = (row['takedown'] / row['takedownAtt'] * 100) if row['takedownAtt'] > 0 else 0.0
            rates['SigStrDef'] = (100 - (row['SigStrAg'] / row['SigStrAttAg'] * 100)) if row['SigStrAttAg'] > 0 else 0.0
            rates['TDDef'] = (100 - (row['TDAg'] / row['TDAttAg'] * 100)) if row['TDAttAg'] > 0 else 0.0
            return rates

            
        home_totals = calculate_totals(home_data)
        away_totals = calculate_totals(away_data)

        # Start HTML content for the game boxscore
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
<title>{fight_name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="stylesheet.css">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<script>
    document.addEventListener("DOMContentLoaded", async function () {{
        const searchBar = document.getElementById("search-bar");
        const searchResults = document.getElementById("search-results");

        let fighterLinks = {{}};
        let eventLinks = {{}};

        // Load JSON files
        async function loadLinks() {{
            fighterLinks = await fetch('fighters.json').then(response => response.json());
            eventLinks = await fetch('events.json').then(response => response.json());
        }}

        await loadLinks();

        // Filter data and show suggestions based on input
        function updateSuggestions() {{
            const query = searchBar.value.trim().toLowerCase();
            searchResults.innerHTML = ""; // Clear previous results

            if (query === "") return;

            const combinedLinks = {{ ...fighterLinks, ...eventLinks }};
            const matchingEntries = Object.entries(combinedLinks)
                .filter(([name]) => name.includes(query))
                .slice(0, 5); // Limit to top 5

            matchingEntries.forEach(([name, url]) => {{
                const resultItem = document.createElement("div");
                resultItem.classList.add("suggestion");

                // Proper case for names
                resultItem.textContent = name.split(" ")
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");

                resultItem.addEventListener("click", () => {{
                    window.open(url, "_self");
                }});
                searchResults.appendChild(resultItem);
            }});

            if (matchingEntries.length > 0) {{
                searchResults.style.display = "block";
            }} else {{
                const noResultItem = document.createElement("div");
                noResultItem.classList.add("no-result");
                noResultItem.textContent = "No results found.";
                searchResults.appendChild(noResultItem);
                searchResults.style.display = "block";
            }}
        }}
        
        document.addEventListener("click", function(event) {{
            if (!searchContainer.contains(event.target)) {{
                searchResults.style.display = "none";
            }}
        }});

        // Add event listener to search bar
        searchBar.addEventListener("input", updateSuggestions);
}});
</script>
</head>
<body>
    <div class="topnav">
        <a href="/ufc/">Projections</a>
        <a href="/ufc/fighters/">Fighters</a>
        <a href="/ufc/fights/">Fight Results</a>
        <a href="/ufc/stats/">Stats</a>
        <a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a fighter or event...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
        <h1>{fight_name}</h1>
        <h2>{event} - {date}</h2>
        <h2>{fight_location}</h2>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    <div id="boxscore-container">
    
    <div class="subhead">
        <h3>Weight Class: {weight_class}</h3>
        <h3>Scheduled Rounds: {int(scheduled_rounds) if str(scheduled_rounds).isdigit() else scheduled_rounds}</h3>
        <h3>Fight Duration: {fight_duration}</h3>
    </div>
        
    <div id="table-container">
        '''

        def create_fighter_table(fighter_data, fighter_name, totals, table_id):
            fighter_table = f'''
        <span class="caption">{fighter_name}</span>
        <table id="{table_id}">
        <thead>
            <tr>
                <td class="multiColHeaders" colspan="6"></td>
                <td class="multiColHeaders" colspan="17">Striking - Offense</td>
                <td class="multiColHeaders" colspan="5">Grappling - Offense</td>
                <td class="multiColHeaders" colspan="5">Striking - Defense</td>
                <td class="multiColHeaders" colspan="4">Grappling - Defense</td>
            </tr>
            <tr>
                <th>Fighter</th>
                <th></th>
                <th>Result</th>
                <th>Fight Duration</th>
                <th>Rd</th>
                <th>Rd Duration</th>
                <th>KD</th>
                <th>Sig. Str.</th>
                <th>Sig. Str. Att.</th>
                <th>Sig. Str. Acc.</th>
                <th>SSLPM</th>
                <th>Total Str.</th>
                <th>Total Str. Att.</th>
                <th>Sig. Head Str.</th>
                <th>Sig. Head Str. Att.</th>
                <th>Sig. Body Str.</th>
                <th>Sig. Body Str. Att.</th>
                <th>Sig. Leg Str.</th>
                <th>Sig. Leg Str. Att.</th>
                <th>Clinch Str.</th>
                <th>Clinch Str. Att.</th>
                <th>Ground Str.</th>
                <th>Ground Str. Att.</th>
                <th>TD</th>
                <th>TD Att</th>
                <th>TD Acc.</th>
                <th>Sub. Att.</th>
                <th>Reversal</th>
                <th>Sig. Str. Agst</th>
                <th>Sig. Str. Att. Agst</th>
                <th>Sig. Str. Def</th>
                <th>Total Str. Agst</th>
                <th>Total Str. Att. Agst</th>
                <th>TD Agst</th>
                <th>TD Att. Agst</th>
                <th>TD Def</th>
                <th>Sub. Att. Agst</th>
            </tr>
        </thead>
        <tbody>
            '''
            # Add rows for each fighter in the data
            for _, row in fighter_data.iterrows():
                rates = calculate_rates(row)
                fighter_table += f'''
            <tr>
                <td style="text-align:left"><a href="/ufc/fighters/{row['fighterID']}.html" target="_blank">{row['fighter']}</a></td>
                <td>{row['outcome']}</td>
                <td>{row['result']}</td>
                <td>{row['fight_duration']}</td>
                <td>{int(row['fightRound'])}</td>
                <td>{row['round_duration']}</td>
                <td>{int(row['knockdowns'])}</td>
                <td>{int(row['SigStr'])}</td>
                <td>{int(row['SigStrAtt'])}</td>
                <td>{rates['StrAccuracy']:.2f}%</td>
                <td>{rates['SLPM']:.2f}</td>
                <td>{int(row['totalStrikesLanded'])}</td>
                <td>{int(row['totalStrikesAttempted'])}</td>
                <td>{int(row['sigHeadStr'])}</td>
                <td>{int(row['sigHeadStrAtt'])}</td>
                <td>{int(row['sigBodyStr'])}</td>
                <td>{int(row['sigBodyStrAtt'])}</td>
                <td>{int(row['sigLegStr'])}</td>
                <td>{int(row['sigLegStrAtt'])}</td>
                <td>{int(row['clinchStrikes'])}</td>
                <td>{int(row['clinchAttStr'])}</td>
                <td>{int(row['groundStr'])}</td>
                <td>{int(row['groundAttStr'])}</td>
                <td>{int(row['takedown'])}</td>
                <td>{int(row['takedownAtt'])}</td>
                <td>{rates['takedownAcc']:.2f}%</td>
                <td>{int(row['subAtt'])}</td>
                <td>{int(row['reversals'])}</td>
                <td>{int(row['SigStrAg'])}</td>
                <td>{int(row['SigStrAttAg'])}</td>
                <td>{rates['SigStrDef']:.2f}%</td>
                <td>{int(row['TotStrAg'])}</td>
                <td>{int(row['TotStrAttAg'])}</td>               
                <td>{int(row['TDAg'])}</td>
                <td>{int(row['TDAttAg'])}</td>
                <td>{rates['TDDef']:.2f}%</td>
                <td>{int(row['SubAttAg'])}</td>
            </tr>
                '''
            # Add totals row in tfoot
            fighter_table += f'''
        </tbody>
        <tfoot>
            <tr>
                <td colspan="6"><strong>Total</strong></td>
                <td>{int(totals['knockdowns'])}</td>
                <td>{int(totals['SigStr'])}</td>
                <td>{int(totals['SigStrAtt'])}</td>
                <td>{totals['StrAccuracy']:.2f}%</td>
                <td>{totals['SLPM']}</td>
                <td>{int(totals['totalStrikesLanded'])}</td>
                <td>{int(totals['totalStrikesAttempted'])}</td>
                <td>{int(totals['sigHeadStr'])}</td>
                <td>{int(totals['sigHeadStrAtt'])}</td>
                <td>{int(totals['sigBodyStr'])}</td>
                <td>{int(totals['sigBodyStrAtt'])}</td>
                <td>{int(totals['sigLegStr'])}</td>
                <td>{int(totals['sigLegStrAtt'])}</td>
                <td>{int(totals['clinchStrikes'])}</td>
                <td>{int(totals['clinchAttStr'])}</td>
                <td>{int(totals['groundStr'])}</td>
                <td>{int(totals['groundAttStr'])}</td>
                <td>{int(totals['takedown'])}</td>
                <td>{int(totals['takedownAtt'])}</td>
                <td>{totals['takedownAcc']:.2f}%</td>
                <td>{int(totals['subAtt'])}</td>
                <td>{int(totals['reversals'])}</td>
                <td>{int(totals['SigStrAg'])}</td>
                <td>{int(totals['SigStrAttAg'])}</td>
                <td>{totals['SigStrDef']:.2f}%</td>
                <td>{int(totals['TotStrAg'])}</td>
                <td>{int(totals['TotStrAttAg'])}</td>               
                <td>{int(totals['TDAg'])}</td>
                <td>{int(totals['TDAttAg'])}</td>
                <td>{totals['TDDef']:.2f}%</td>
                <td>{int(totals['SubAttAg'])}</td>
            </tr>
        </tfoot>
        </table>
            '''
            return fighter_table

        html_content += create_fighter_table(home_data, home_data.iloc[0]['fighter'], home_totals, "home-boxscore")
        html_content += create_fighter_table(away_data, away_data.iloc[0]['fighter'], away_totals, "away-boxscore")

        # Close HTML content
        html_content += '''
    </div>
    </div>
    <div class="footer"></div>
</body>
</html>
        '''

        with open(fight_filename, 'w') as file:
            file.write(html_content)

    print("Fight pages created successfully.")

# Create individual game boxscore pages
create_fight_boxscores(fight_data, output_dir_fights)
