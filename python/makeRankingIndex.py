import pandas as pd
import os
import re
from datetime import datetime
from tqdm import tqdm
import json

# File paths
metrics_file_path = r"C:\Users\ashle\Documents\Projects\ufc\data\gamelogs.csv"
rosters_file_path = r"C:\Users\ashle\Documents\Projects\ufc\data\rosters.csv"
rankings_file_path = r"C:\Users\ashle\Documents\Projects\ufc\data\rankings.csv"
output_dir_rank_index = r"C:\Users\ashle\Documents\Projects\ufc"

rosters_data = pd.read_csv(rosters_file_path)
metrics_data = pd.read_csv(metrics_file_path,  parse_dates=["date"], low_memory=False)
rankings_data = pd.read_csv(rankings_file_path, low_memory=False)

fighter_links = {f"{row['fighter']} ({row['fighterID']})".lower(): f"/ufc/fighters/{row['fighterID']}.html" 
                for _, row in rosters_data.iterrows()}


event_links = {row['event'].lower(): f"/ufc/events/{row['eventID']}.html" 
              for _, row in metrics_data.drop_duplicates('eventID').iterrows()}
              
fight_links = {row['fight'].lower(): f"/ufc/fights/{row['fightID']}.html" 
              for _, row in metrics_data.drop_duplicates('fightID').iterrows()}


# Write out to JSON with proper formatting
with open("fighters.json", "w") as f:
    json.dump(fighter_links, f, indent=4)

with open("events.json", "w") as f:
    json.dump(event_links, f)
    
with open("fights.json", "w") as f:
    json.dump(fight_links, f)


print("fighters.json and events.json created successfully!")

# Ensure output directory exists
os.makedirs(output_dir_rank_index, exist_ok=True)

def create_rank_directory(rankings_data, output_file_path):
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>UFC Rankings</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <script src="fighters.json"></script>
    <script src="events.json"></script>
    
<script>
    document.addEventListener("DOMContentLoaded", function () {
        const tables = document.querySelectorAll(".weight-class-rankings");

        tables.forEach((table) => {
            const headers = table.querySelectorAll("thead th");
            const rows = Array.from(table.querySelectorAll("tbody tr"));

            // Add sorting functionality to table headers
            headers.forEach((header, index) => {
                header.style.cursor = "pointer";
                header.addEventListener("click", function () {
                    sortTable(table, index);
                });
            });

            function sortTable(table, columnIndex) {
                const rows = Array.from(table.querySelectorAll("tbody tr"));
                const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
                table.dataset.sortDirection = direction;

                // Special handling for the 'Record' column (index 2)
                if (columnIndex === 2) { // Record column (W-L-D)
                    rows.sort((a, b) => {
                        const recordA = a.cells[columnIndex].textContent.trim();
                        const recordB = b.cells[columnIndex].textContent.trim();

                        // Extract wins, losses, and draws from the W-L-D format, ignoring NC
                        const [winsA, lossesA, drawsA] = parseRecord(recordA);
                        const [winsB, lossesB, drawsB] = parseRecord(recordB);

                        // Debugging: Log parsed values (wins, losses, draws)
                        console.log('Parsed Record A:', winsA, lossesA, drawsA);
                        console.log('Parsed Record B:', winsB, lossesB, drawsB);

                        // Compare wins first
                        if (winsA !== winsB) {
                            return direction === "desc" ? winsA - winsB : winsB - winsA;
                        }

                        // If wins are tied, compare losses (fewer losses is better)
                        if (lossesA !== lossesB) {
                            return direction === "asc" ? lossesA - lossesB : lossesB - lossesA;
                        }

                        // If both wins and losses are tied, compare draws (fewer draws is better)
                        return direction === "asc" ? drawsA - drawsB : drawsB - drawsA;
                    });
                } else {
                    // Generic sorting for other columns (numeric, date, or text columns)
                    const isNumeric = !isNaN(parseFloat(rows[0].cells[columnIndex].textContent.trim()));
                    const isDate = !isNaN(Date.parse(rows[0].cells[columnIndex].textContent.trim()));

                    rows.sort((a, b) => {
                        let valA = a.cells[columnIndex].textContent.trim();
                        let valB = b.cells[columnIndex].textContent.trim();

                        if (isNumeric) {
                            valA = parseFloat(valA);
                            valB = parseFloat(valB);
                        } else if (isDate) {
                            valA = new Date(valA);
                            valB = new Date(valB);
                        } else {
                            valA = valA.toLowerCase();
                            valB = valB.toLowerCase();
                        }

                        if (valA < valB) {
                            return direction === "asc" ? -1 : 1;
                        } else if (valA > valB) {
                            return direction === "asc" ? 1 : -1;
                        }
                        return 0;
                    });
                }

                const tbody = table.querySelector("tbody");
                rows.forEach(row => tbody.appendChild(row)); // Reattach sorted rows
            }
        });

        // Helper function to parse the W-L-D (n NC) format
        function parseRecord(record) {
            // Handle the case where there's (n NC)
            const cleanRecord = record.replace(/\\s*\\(\\d+\\s*NC\\)/, '').trim();
            const [wins, losses, draws] = cleanRecord.split('-').map(Number);
            // Return parsed values
            return [wins, losses, draws];
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
        <h1>Rankings</h1>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    <div id="rank-index-container">
    <div id="rank-page-container">
    <div id="grouped-ranking-container">
"""

    weight_classes_order = [
        "Men's PFP", "Women's PFP", "Flyweight", "Bantamweight", "Featherweight", "Lightweight", "Welterweight", "Middleweight", "Light Heavyweight", "Heavyweight", "Women's Strawweight", "Women's Flyweight", "Women's Bantamweight"
    ]

    grouped_by_weight_class = rankings_data.groupby('weight_class')
    
    weight_classes_in_order = [
        (wc, grouped_by_weight_class.get_group(wc)) 
        for wc in weight_classes_order if wc in grouped_by_weight_class.groups
    ]
    
    for i in range(0, len(weight_classes_in_order), 2):
        html_content += '<div class="row" style="display: flex; justify-content: space-between;">'

        # Process the next two tables (or fewer if at the end)
        for weight_class, group in weight_classes_in_order[i:i+2]:
            html_content += f"""
            <div class="ranking-table" style="flex: 0 0 48%; margin: 0 10px;">
                <h3>{weight_class}</h3>
                <table id="{weight_class.replace(' ', '_').replace("'", "").lower()}" class="weight-class-rankings">
                    <thead>
                        <tr>
                            <th>Rk</th>
                            <th>Fighter</th>
                            <th>Record</th>
                            <th>Style</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for _, row in group.iterrows():
                if str(row['rk']).lower() == "champ":
                    rk_cell = '<tr class="champ-row"><td class="champ-cell">C</td>'
                else:
                    rk_cell = f'<tr><td>{row["rk"]}</td>'
                
                html_content += f"""
                    {rk_cell}
                        <td><a href="/ufc/fighters/{row['fighterID']}.html">{row['fighter']}</a></td>
                        <td>{row['record']}</td>
                        <td>{row['style']}</td>
                    </tr>
                """
            html_content += """
                    </tbody>
                </table>
            </div>
            """
        html_content += '</div>'  # Close the current row

    # Finalize HTML
    html_content += """
    </div>
    </div>
    </div>
    <div class="footer"></div>
</body>
</html>
"""
    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Rankings directory created at {output_file_path}")

output_file_path = os.path.join(output_dir_rank_index, "index.html")
create_rank_directory(rankings_data, output_file_path)
