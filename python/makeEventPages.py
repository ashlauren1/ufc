import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\ufc\data"
output_dir = r"C:\Users\ashle\Documents\Projects\ufc\events"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load game logs data
event_csv = os.path.join(data_dir, "eventIndex.csv")
fight_data = pd.read_csv(event_csv, low_memory=False)

# **Part 1: Create Team Directory (index.html)**
def create_event_directory(fight_data, output_dir):
    unique_events = fight_data.drop_duplicates(subset=['eventID'])
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Event Directory</title>
        <link rel="stylesheet" href="stylesheet.css">
        <link rel="icon" type="image/x-icon" href="favicon.ico">
    <script>
    document.addEventListener("DOMContentLoaded", function () {
        const table = document.getElementById("event-index");
        const headerRow = table.querySelector("thead tr:first-child");
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
                    return direction === "asc" ? -1 : 1;
                } else if (valA > valB) {
                    return direction === "asc" ? 1 : -1;
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

    // Load players and teams data from JSON files
    async function loadLinks() {
        fighterLinks = await fetch('fighters.json').then(response => response.json());
        eventLinks = await fetch('events.json').then(response => response.json());
    }

    await loadLinks();  // Ensure links are loaded before searching

    // Filter data and show suggestions based on input
    function updateSuggestions() {
        const query = searchBar.value.trim().toLowerCase();
        searchResults.innerHTML = ""; // Clear previous results

        if (query === "") return;

        // Combine players and teams for search
        const combinedLinks = { ...fighterLinks, ...eventLinks };
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
        <a href="/ufc/">Projections</a>
        <a href="/ufc/fighters/">Fighters</a>
        <a href="/ufc/fights/">Fight Results</a>
        <a href="/ufc/events/">Events</a>
        <a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for fighters or events...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    

        <div class="header">
        <h1>Event Directory</h1>
        </div>
        <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
        <div id="index-container">
        <table id="event-index">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Event Type</th>
                    <th>Date</th>
                    <th>Location</th>
                </tr>
            </thead>
            <tbody>
    """

    # Populate the table with each unique team and link
    for _, row in unique_events.iterrows():
        event_name = row["event"]
        event_id = row["eventID"]
        event_type = row["event_type"]
        date = row["date"]
        location = row["location"]
        

        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/ufc/events/{event_id}.html">{event_name}</a></td>
                <td style="text-align:left">{event_type}</td>
                <td style="text-align:left">{date}</td>
                <td style="text-align:left">{location}</td>
            </tr>
        """

    # Close the table and HTML tags
    html_content += """
            </tbody>
        </table>
        <div class="footer"></div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    output_file_path = os.path.join(output_dir, "index.html")
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Event directory created at {output_file_path}")

# **Part 2: Generate Individual Team Pages**
def create_event_pages(fight_data, output_dir):
    grouped_data = fight_data.groupby('eventID')

    for event_id, event_data in grouped_data:
        event_name = event_data.iloc[0]["event"]
        event_id = event_data.iloc[0]["eventID"]
        event_type = event_data.iloc[0]["event_type"]
        date = event_data.iloc[0]["date"]
        location = event_data.iloc[0]["location"]
        weight_class = event_data.iloc[0]["weight_class"]
        fight = event_data.iloc[0]["fight"]
        fight_id = event_data.iloc[0]["fightID"]
        fight_duration = event_data.iloc[0]["fight_duration"]
        scheduled_rounds = event_data.iloc[0]["scheduled_rounds"]
        result = event_data.iloc[0]["result"]
        
        event_filename = os.path.join(output_dir, f"{event_id}.html")
        
        def calculate_rates(row):
            rates = {}
            
            rates['StrAccuracy'] = (row['StrAccuracy'] * 100) if row['StrAccuracy'] > 0 else 0.0
            rates['SLPM'] = round(row['SLPM'], 2) if row['SLPM'] > 0 else 0.0
            rates['takedownAcc'] = (row['takedownAcc'] * 100) if row['takedownAcc'] > 0 else 0.0
            rates['StrDef'] = (row['StrDef'] * 100) if row['StrDef'] > 0 else 0.0
            rates['takedownDef'] = (row['takedownDef'] * 100) if row['takedownDef'] > 0 else 0.0
            
            rates['opp_StrAccuracy'] = (row['opp_StrAccuracy'] * 100) if row['opp_StrAccuracy'] > 0 else 0.0
            rates['opp_SLPM'] = round(row['opp_SLPM'], 2) if row['opp_SLPM'] > 0 else 0.0
            rates['opp_takedownAcc'] = (row['opp_takedownAcc'] * 100) if row['opp_takedownAcc'] > 0 else 0.0
            rates['opp_StrDef'] = (row['opp_StrDef'] * 100) if row['opp_StrDef'] > 0 else 0.0
            rates['opp_takedownDef'] = (row['opp_takedownDef'] * 100) if row['opp_takedownDef'] > 0 else 0.0
            
            return rates

        # Start HTML content for the team's gamelog
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
<title>{event_name}</title>
<link rel="stylesheet" href="stylesheet.css">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<script>
    document.addEventListener("DOMContentLoaded", function () {{
        const table = document.getElementById("event-table");
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

    // Load players and teams data from JSON files
    async function loadLinks() {{
        fighterLinks = await fetch('fighters.json').then(response => response.json());
        eventLinks = await fetch('events.json').then(response => response.json());
    }}

    await loadLinks();  // Ensure links are loaded before searching

    // Filter data and show suggestions based on input
    function updateSuggestions() {{
        const query = searchBar.value.trim().toLowerCase();
        searchResults.innerHTML = ""; // Clear previous results

        if (query === "") return;

        // Combine players and teams for search
        const combinedLinks = {{ ...fighterLinks, ...eventLinks }};
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
        <input type="text" id="search-bar" placeholder="Search for fighters or events...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
        <h1>{event_name}</h1>
        <h2>{event_type}</h2>
        <h2>{location} - {date}</h2>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    
    <div id="event-container">
    <table id="event-table">
        <thead>
            <tr>
                <th>Fight</th>
                <th>Weight Class</th>
                <th>Fight Duration</th>
                <th>Scheduled Rounds</th>
                <th>Result</th>
                <th>Fighter</th>
                <th></th>
                <th>Significant Strikes</th>
                <th>Strike Accuracy</th>
                <th>SSLPM</th>
                <th>Strike Defense</th>
                <th>Takedowns</th>
                <th>Takedown Accuracy</th>
                <th>Takedown Defense</th>
                <th>Fighter</th>
                <th></th>
                <th>Significant Strikes</th>
                <th>Strike Accuracy</th>
                <th>SSLPM</th>
                <th>Strike Defense</th>
                <th>Takedowns</th>
                <th>Takedown Accuracy</th>
                <th>Takedown Defense</th>
            </tr>
        </thead>
        <tbody>
        '''

        # Add rows for each game in the team's gamelog
        for _, row in event_data.iterrows():
            rates = calculate_rates(row)
            html_content += f'''
            <tr>
                <td style="text-align:left"><a href="/ufc/fights/{row['fightID']}.html" target="_blank">{row['fight']}</a></td>
                <td style="text-align:left">{row['weight_class']}</td>
                <td style="text-align:left">{row['fight_duration']}</td>
                <td style="text-align:left">{int(scheduled_rounds) if str(scheduled_rounds).isdigit() else scheduled_rounds}</td>
                <td style="text-align:left">{row['result']}</td>
                <td style="text-align:left"><a href="/ufc/fighters/{row['fighterID']}.html" target="_blank">{row['fighter']}</a></td>
                <td>{row['outcome']}</td>
                <td>{int(row['SigStr'])}</td>
                <td>{rates['StrAccuracy']:.2f}%</td>
                <td>{rates['SLPM']:.2f}</td>
                <td>{rates['StrDef']:.2f}%</td>
                <td>{int(row['takedown'])}</td>
                <td>{rates['takedownAcc']:.2f}%</td>
                <td>{rates['takedownDef']:.2f}%</td>
                
                <td style="text-align:left"><a href="/ufc/fighters/{row['oppID']}.html" target="_blank">{row['opp']}</a></td>
                <td>{row['oppOutcome']}</td>
                <td>{int(row['opp_SigStr'])}</td>
                <td>{rates['opp_StrAccuracy']:.2f}%</td>
                <td>{rates['opp_SLPM']:.2f}</td>
                <td>{rates['opp_StrDef']:.2f}%</td>
                <td>{int(row['opp_takedown'])}</td>
                <td>{rates['opp_takedownAcc']:.2f}%</td>
                <td>{rates['opp_takedownDef']:.2f}%</td>
            </tr>
            '''

        # Close HTML content
        html_content += '''
                </tbody>
            </table>
            </div>
        </body>
        </html>
        '''

        # Write to HTML file
        with open(event_filename, 'w') as file:
            file.write(html_content)

    print("Event Pages created successfully.")

# **Run the Functions**
create_event_directory(fight_data, output_dir)
create_event_pages(fight_data, output_dir)
