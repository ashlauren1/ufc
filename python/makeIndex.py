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

# Write out to JSON with proper formatting
with open("fighters.json", "w") as f:
    json.dump(fighter_links, f, indent=4)

with open("events.json", "w") as f:
    json.dump(event_links, f)

print("fighters.json and events.json created successfully!")


# Ensure output directory exists
os.makedirs(output_dir_rank_index, exist_ok=True)


# **Part 1: Generate Game Directory (index.html)**
def create_rank_directory(rankings_data, output_file_path):
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>UFC!</title>
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
            const table = document.getElementById("rank-index");
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
        <input type="text" id="search-bar" placeholder="Search fighters...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
        <h1>Rankings</h1>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    <div id="rank-index-container">
    <p class="rank-index">* No Contest</p>
        <table id="rank-index">
            <thead>
                <tr>
                    <th>Division</th>
                    <th>Rk</th>
                    <th>Fighter</th>
                    <th>Record<br>(W-L-D)</th>
                    <th>Style</th>
                    <th>SS Avg</th>
                    <th>SS Acc</th>
                    <th>SLPM</th>
                    <th>SS Def.</th>
                    <th>TD Avg</th>
                    <th>TD Acc.</th>
                    <th>TD Def.</th>
                </tr>
            </thead>
            <tbody>
    """

    # Populate the table with each unique game
    for _, row in rankings_data.iterrows():
        weight_class = row['weight_class']
        rk = row['rk']
        fighter = row['fighter']
        fighter_id = row['fighterID']
        record = row['record']
        ko_tko = row['KO_TKO']
        age = row['age']
        height = row['height']
        reach = row['reach']
        style = row['style']
        sig_str_avg = row['SigStrAvg']
        str_acc = row['StrAcc']
        slpm = row['SLPM']
        str_def = row['StrDef']
        td_avg = row['TDAvg']
        td_def = row['TDDef']


        html_content += f"""
                <tr>
                    <td style="text-align:left">{weight_class}</td>
                    <td>{rk}</td>
                    <td style="text-align:left"><a href="/ufc/fighters/{fighter_id}.html">{fighter}</a></td>
                    <td>{record}</td>
                    <td style="text-align:left">{style}</td>
                    <td>{sig_str_avg}</td>
                    <td>{row['StrAcc']:.2f}%</td>
                    <td>{slpm}</td>
                    <td>{row['StrDef']:.2f}%</td>
                    <td>{td_avg}</td>
                    <td>{row['TDAcc']:.2f}%</td>
                    <td>{row['TDDef']:.2f}%</td>
                </tr>
        """

    # Close the table and HTML tags
    html_content += """
                </tbody>
            </table>
        </div>
    <div class="footer"></div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Game directory created at {output_file_path}")


# Create game directory
output_file_path = os.path.join(output_dir_rank_index, "index.html")
create_rank_directory(rankings_data, output_file_path)
