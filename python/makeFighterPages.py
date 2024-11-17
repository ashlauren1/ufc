import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\ufc\data"
output_dir = r"C:\Users\ashle\Documents\Projects\ufc\fighters"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# **Load Data**
roster_csv = os.path.join(data_dir, "rosters.csv")
gamelogs_csv = os.path.join(data_dir, "gamelogs.csv")

# Load roster data
roster_data = pd.read_csv(roster_csv)
fight_data = pd.read_csv(gamelogs_csv, low_memory=False)


# **Part 1: Generate Player Directory (index.html)**
def create_player_directory(roster_data, output_file_path):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fighter Directory</title>
        <link rel="stylesheet" href="stylesheet.css">
        <link rel="icon" type="image/x-icon" href="favicon.ico">
        
    <script>
    document.addEventListener("DOMContentLoaded", function () {
        const table = document.getElementById("fighter-index");
        const headerRow = table.querySelector("thead tr:first-child");
        const filterRow = document.querySelector("#filter-row");
        const rows = Array.from(table.querySelectorAll("tbody tr"));

        // Add filters and sorting
        addFilters(table);
        addSortToHeaders(table);

        function addFilters(table) {
            const headerRow = table.querySelector("thead tr:first-child");
            const filterRow = document.createElement("tr");
            filterRow.id = "filter-row";
            Array.from(headerRow.cells).forEach((header, index) => {
                const filterCell = document.createElement("td");
                const filterSelect = document.createElement("select");
                filterSelect.classList.add("filter-select");

                filterSelect.innerHTML = '<option value="">All</option>';
                const values = Array.from(new Set(
                    Array.from(table.querySelectorAll("tbody tr td:nth-child(" + (index + 1) + ")"))
                    .map(cell => cell.textContent.trim())
                )).sort();

                values.forEach(value => {
                    const option = document.createElement("option");
                    option.value = value;
                    option.textContent = value;
                    filterSelect.appendChild(option);
                });

                filterSelect.addEventListener("change", filterTable);
                filterCell.appendChild(filterSelect);
                filterRow.appendChild(filterCell);
            });
            table.querySelector("thead").appendChild(filterRow);
        }

        function filterTable() {
            const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
            rows.forEach(row => {
                const cells = Array.from(row.cells);
                const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
                row.style.display = matchesFilter ? "" : "none";
            });
        }

        function addSortToHeaders(table) {
            const headers = table.querySelectorAll("thead th");
            headers.forEach((header, index) => {
                header.style.cursor = "pointer";
                header.addEventListener("click", function () {
                    sortTable(table, index);
                });
            });
        }

        function sortTable(table, columnIndex) {
            const rows = Array.from(table.querySelectorAll("tbody tr"));
            const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
            table.dataset.sortDirection = direction;

            // Detect data type
            let isNumeric = true;
            let isDate = true;
            for (let row of rows) {
                const cellText = row.cells[columnIndex].textContent.trim();
                if (cellText === '') continue; // Skip empty cells
                if (isNumeric && isNaN(cellText)) {
                    isNumeric = false;
                }
                if (isDate && isNaN(Date.parse(cellText))) {
                    isDate = false;
                }
                if (!isNumeric && !isDate) break;
            }

            rows.sort((a, b) => {
                const cellA = a.cells[columnIndex].textContent.trim();
                const cellB = b.cells[columnIndex].textContent.trim();

                let valA, valB;

                if (isNumeric) {
                    valA = parseFloat(cellA);
                    valB = parseFloat(cellB);
                } else if (isDate) {
                    valA = new Date(cellA);
                    valB = new Date(cellB);
                } else {
                    valA = cellA.toLowerCase();
                    valB = cellB.toLowerCase();
                }

                if (valA < valB) {
                    return direction === "desc" ? -1 : 1;
                } else if (valA > valB) {
                    return direction === "desc" ? 1 : -1;
                } else {
                    return 0;
                }
            });

            const tbody = table.querySelector("tbody");
            rows.forEach(row => tbody.appendChild(row));
        }
    });
    document.addEventListener("DOMContentLoaded", async function () {
    const searchBar = document.getElementById("search-bar");
    const searchResults = document.getElementById("search-results");

    let fighterLinks = {};
    let eventLinks = {};
    let fightLinks = {};

    // Load players and teams data from JSON files
    async function loadLinks() {
        fighterLinks = await fetch('fighters.json').then(response => response.json());
        eventLinks = await fetch('events.json').then(response => response.json());
        fightLinks = await fetch('fights.json').then(response => response.json());
    }

    await loadLinks();  // Ensure links are loaded before searching

    // Filter data and show suggestions based on input
    function updateSuggestions() {
        const query = searchBar.value.trim().toLowerCase();
        searchResults.innerHTML = ""; // Clear previous results

        if (query === "") return;

        // Combine players and teams for search
        const combinedLinks = { ...fighterLinks, ...eventLinks, ...fightLinks };
        const matchingEntries = Object.entries(combinedLinks)
            .filter(([name]) => name.includes(query))  // Matches on both name and ID
            .slice(0, 5); // Limit to top 5

        matchingEntries.forEach(([name, url]) => {
            const resultItem = document.createElement("div");
            resultItem.classList.add("suggestion");

            // Proper case for names
            resultItem.textContent = name.split(" ")
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ");

            resultItem.addEventListener("click", () => {
                window.open(url, "_self");
            });
            searchResults.appendChild(resultItem);
        });

        if (matchingEntries.length > 0) {
            searchResults.style.display = "block"; // Show results if matches are found
        } else {
            const noResultItem = document.createElement("div");
            noResultItem.classList.add("no-result");
            noResultItem.textContent = "No results found.";
            searchResults.appendChild(noResultItem);
            searchResults.style.display = "block";
        }
    }
    
    document.addEventListener("click", function(event) {
        if (!searchContainer.contains(event.target)) {
            searchResults.style.display = "none";
        }
    });

    // Add event listener to search bar
    searchBar.addEventListener("input", updateSuggestions);
});
    </script>
</head>
<body>
    <div class="topnav">
        <a href="/ufc/">Rankings</a>
        <a href="/ufc/fighters/">Fighters</a>
        <a href="/ufc/fights/">Fights and Results</a>
        <a href="/ufc/events/">Events</a>
        <a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for events, fights, or fighters...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
        <h1>Fighter Directory</h1>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
    <div id="index-container">
    <table id="fighter-index">
        <thead>
            <tr>
                <th>Fighter</th>
                <th>Status</th>
                <th>Fighting Style</th>
                <th>Age</th>
                <th>Height</th>
                <th>Weight</th>
                <th>Debut</th>
                <th>Reach</th>
                <th>Leg Reach</th>                
            </tr>
        </thead>
        <tbody>
    """

    # Generate table rows grouped by team
    for _, row in roster_data.iterrows():
        fighter_id = row["fighterID"]
        fighter_name = row["fighter"]
        status = row["Status"]
        style = row["Style"]
        age = row["Age"]
        height = row["Height"]
        weight = row["Weight"]
        debut = row["Debut"]
        reach = row["Reach"]
        leg_reach = row["LegReach"]

        # Add player row
        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/ufc/fighters/{fighter_id}.html">{fighter_name}</a></td>
                <td style="text-align:left">{status}</td>
                <td style="text-align:left">{style}</td>
                <td style="text-align:center">{age}</td>
                <td style="text-align:center">{height}</td>
                <td style="text-align:center">{weight}</td>
                <td style="text-align:left">{debut}</td>
                <td style="text-align:center">{reach}</td>
                <td style="text-align:center">{leg_reach}</td>
            </tr>
        """

    # Close the single <tbody>, table, and HTML tags
    html_content += """
        </tbody>
        </table>
        <div class="footer"></div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Player directory created at {output_file_path}")


# Define calculate_fight_totals function outside create_fightlog
def calculate_fight_totals(data):
    totals = data[['knockdowns', 'SigStr', 'SigStrAtt', 'totalStrikesLanded', 'totalStrikesAttempted', 'takedown', 'takedownAtt', 'subAtt', 'reversals', 'sigHeadStr', 'sigHeadStrAtt', 'sigBodyStr', 'sigBodyStrAtt', 'sigLegStr', 'sigLegStrAtt', 'clinchStrikes', 'clinchAttStr', 'groundStr', 'groundAttStr', 'SigStrAg', 'SigStrAttAg', 'TotStrAg', 'TotStrAttAg', 'TDAg', 'TDAttAg', 'SubAttAg']].sum()
    
    totals['StrAccuracy'] = (totals['SigStr'] / totals['SigStrAtt'] * 100) if totals['SigStrAtt'] > 0 else 0.0
    totals['SLPM'] = round((totals['SigStr'] / data['fight_duration'].sum()), 2) if data['fight_duration'].sum() > 0 else 0.0
    totals['takedownAcc'] = (totals['takedown'] / totals['takedownAtt'] * 100) if totals['takedownAtt'] > 0 else 0.0
    totals['SigStrDef'] = (100 - (totals['SigStrAg'] / totals['SigStrAttAg'] * 100)) if totals['SigStrAttAg'] > 0 else 0.0
    totals['TDDef'] = (100 - (totals['TDAg'] / totals['TDAttAg'] * 100)) if totals['TDAttAg'] > 0 else 0.0
    
    return totals

# Now define create_fightlog function
def create_fightlog(fight_data, output_dir):
    grouped_data = fight_data.groupby('fighterID')
    
    for fighter_id, fighter_data in grouped_data:
        fighter_name = fighter_data.iloc[0]['fighter']
        fighter_filename = f'{output_dir}/{fighter_id}.html'

        # Start HTML content for the game boxscore
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
<title>{fighter_name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="stylesheet.css">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<script>
    document.addEventListener("DOMContentLoaded", function () {{
        const table = document.getElementById("fighter-table");
        const headerRow = table.querySelector("thead tr:first-child");
        const rows = Array.from(table.querySelectorAll("tbody tr"));

        // Add filters and sorting
        addFilters(table);
        addSortToHeaders(table);

        function addFilters(table) {{
            const headerRow = table.querySelector("thead tr:first-child");
            const filterRow = document.createElement("tr");
            filterRow.id = "filter-row";
            Array.from(headerRow.cells).forEach((header, index) => {{
                const filterCell = document.createElement("td");
                const filterSelect = document.createElement("select");
                filterSelect.classList.add("filter-select");

                filterSelect.innerHTML = '<option value="">All</option>';
                const values = Array.from(new Set(
                    Array.from(table.querySelectorAll("tbody tr td:nth-child(" + (index + 1) + ")"))
                    .map(cell => cell.textContent.trim())
                )).sort();

                values.forEach(value => {{
                    const option = document.createElement("option");
                    option.value = value;
                    option.textContent = value;
                    filterSelect.appendChild(option);
                }});

                filterSelect.addEventListener("change", filterTable);
                filterCell.appendChild(filterSelect);
                filterRow.appendChild(filterCell);
            }});
            table.querySelector("thead").appendChild(filterRow);
        }}

        function filterTable() {{
            const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
            rows.forEach(row => {{
                const cells = Array.from(row.cells);
                const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
                row.style.display = matchesFilter ? "" : "none";
            }});
        }}

        function addSortToHeaders(table) {{
            const headers = table.querySelectorAll("thead th");
            headers.forEach((header, index) => {{
                header.style.cursor = "pointer";
                header.addEventListener("click", function () {{
                    sortTable(table, index);
                }});
            }});
        }}

        function sortTable(table, columnIndex) {{
            const rows = Array.from(table.querySelectorAll("tbody tr"));
            const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
            table.dataset.sortDirection = direction;

            // Detect data type
            let isNumeric = true;
            let isDate = true;
            for (let row of rows) {{
                const cellText = row.cells[columnIndex].textContent.trim();
                if (cellText === '') continue; // Skip empty cells
                if (isNumeric && isNaN(cellText)) {{
                    isNumeric = false;
                }}
                if (isDate && isNaN(Date.parse(cellText))) {{
                    isDate = false;
                }}
                if (!isNumeric && !isDate) break;
            }}

            rows.sort((a, b) => {{
                const cellA = a.cells[columnIndex].textContent.trim();
                const cellB = b.cells[columnIndex].textContent.trim();

                let valA, valB;

                if (isNumeric) {{
                    valA = parseFloat(cellA);
                    valB = parseFloat(cellB);
                }} else if (isDate) {{
                    valA = new Date(cellA);
                    valB = new Date(cellB);
                }} else {{
                    valA = cellA.toLowerCase();
                    valB = cellB.toLowerCase();
                }}

                if (valA < valB) {{
                    return direction === "asc" ? -1 : 1;
                }} else if (valA > valB) {{
                    return direction === "asc" ? 1 : -1;
                }} else {{
                    return 0;
                }}
            }});

            const tbody = table.querySelector("tbody");
            rows.forEach(row => tbody.appendChild(row));
        }}
    }});
    document.addEventListener("DOMContentLoaded", async function () {{
    const searchBar = document.getElementById("search-bar");
    const searchResults = document.getElementById("search-results");

    let fighterLinks = {{}};
    let eventLinks = {{}};
    let fightLinks = {{}};

    // Load players and teams data from JSON files
    async function loadLinks() {{
        fighterLinks = await fetch('fighters.json').then(response => response.json());
        eventLinks = await fetch('events.json').then(response => response.json());
        fightLinks = await fetch('fights.json').then(response => response.json());
    }}

    await loadLinks();  // Ensure links are loaded before searching

    // Filter data and show suggestions based on input
    function updateSuggestions() {{
        const query = searchBar.value.trim().toLowerCase();
        searchResults.innerHTML = ""; // Clear previous results

        if (query === "") return;

        // Combine players and teams for search
        const combinedLinks = {{ ...fighterLinks, ...eventLinks, ...fightLinks }};
        const matchingEntries = Object.entries(combinedLinks)
            .filter(([name]) => name.includes(query))  // Matches on both name and ID
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
            searchResults.style.display = "block"; // Show results if matches are found
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
        <a href="/ufc/events/">Events</a>
        <a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for events, fights, or fighters...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
        <h1>{fighter_name}</h1>
    </div>
    <div class="info-box">
    </div>
    
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    
    <div id="fighter-container">
    <div id="table-container">
    <span class="table-button-container">
    <span class="caption">Fight History</span>
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </span>
        <table id="fighter-table">
        <thead>
            <tr>
                <th>Event</th>
                <th>Fight</th>
                <th>Opp</th>
                <th>Date</th>
                <th>Location</th>
                <th>Weight Class</th>
                <th>Result</th>
                <th></th>
                <th>Scheduled Rounds</th>
                <th>Fight Duration</th>
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
        fight_groups = fighter_data.groupby('fightID')
        for fight_id, fight_rounds in fight_groups:
            fight_totals = calculate_fight_totals(fight_rounds)  # Calculate totals for all rounds in this fight
            row = fight_rounds.iloc[0]
            html_content  += f'''
        <tr>
            <td style="text-align:left"><a href="/ufc/events/{row['eventID']}.html" target="_blank">{row['event']}</a></td>
            <td style="text-align:left"><a href="/ufc/fights/{row['fightID']}.html" target="_blank">{row['fight']}</a></td>
            <td style="text-align:left"><a href="/ufc/fighters/{row['oppID']}.html" target="_blank">{row['opp']}</a></td>
            <td>{row['date']}</td>
            <td>{row['location']}</td>
            <td>{row['weight_class']}</td>
            <td>{row['result']}</td>
            <td>{row['outcome']}</td>
            <td>{row['scheduled_rounds']}</td>
            <td>{row['fight_duration']}</td>
            <td>{int(fight_totals['knockdowns'])}</td>
            <td>{int(fight_totals['SigStr'])}</td>
            <td>{int(fight_totals['SigStrAtt'])}</td>
            <td>{fight_totals['StrAccuracy']:.2f}%</td>
            <td>{fight_totals['SLPM']:.2f}</td>
            <td>{int(fight_totals['totalStrikesLanded'])}</td>
            <td>{int(fight_totals['totalStrikesAttempted'])}</td>
            <td>{int(fight_totals['sigHeadStr'])}</td>
            <td>{int(fight_totals['sigHeadStrAtt'])}</td>
            <td>{int(fight_totals['sigBodyStr'])}</td>
            <td>{int(fight_totals['sigBodyStrAtt'])}</td>
            <td>{int(fight_totals['sigLegStr'])}</td>
            <td>{int(fight_totals['sigLegStrAtt'])}</td>
            <td>{int(fight_totals['clinchStrikes'])}</td>
            <td>{int(fight_totals['clinchAttStr'])}</td>
            <td>{int(fight_totals['groundStr'])}</td>
            <td>{int(fight_totals['groundAttStr'])}</td>
            <td>{int(fight_totals['takedown'])}</td>
            <td>{int(fight_totals['takedownAtt'])}</td>
            <td>{fight_totals['takedownAcc']:.2f}%</td>
            <td>{int(fight_totals['subAtt'])}</td>
            <td>{int(fight_totals['reversals'])}</td>
            <td>{int(fight_totals['SigStrAg'])}</td>
            <td>{int(fight_totals['SigStrAttAg'])}</td>
            <td>{fight_totals['SigStrDef']:.2f}%</td>
            <td>{int(fight_totals['TotStrAg'])}</td>
            <td>{int(fight_totals['TotStrAttAg'])}</td>               
            <td>{int(fight_totals['TDAg'])}</td>
            <td>{int(fight_totals['TDAttAg'])}</td>
            <td>{fight_totals['TDDef']:.2f}%</td>
            <td>{int(fight_totals['SubAttAg'])}</td>
        </tr>
            '''
        # Add totals row in tfoot
        html_content += '''
        </tbody>
        </table>
    </div>
    </div>
    <div class="footer"></div>
</body>
</html>
        '''

        with open(fighter_filename, 'w') as file:
            file.write(html_content)

    print("Fight pages created successfully.")

# Create individual game boxscore pages
create_fightlog(fight_data, output_dir)

# Create player directory
output_file_path = os.path.join(output_dir, "index.html")
create_player_directory(roster_data, output_file_path)


