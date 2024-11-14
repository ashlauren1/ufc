import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\ufc\data"
output_dir_fight_index = r"C:\Users\ashle\Documents\Projects\ufc\fights"

# Ensure output directory exists
os.makedirs(output_dir_fight_index, exist_ok=True)

# Load game logs data
gamelogs_csv = os.path.join(data_dir, "gamelogs.csv")
fight_data = pd.read_csv(gamelogs_csv, low_memory=False)

unique_fights = fight_data.drop_duplicates(subset=['fightID'])


# **Part 1: Generate Game Directory (index.html)**
def create_game_directory(fight_data, output_file_path):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fight Directory</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="stylesheet.css">
        <link rel="icon" type="image/x-icon" href="favicon.ico">

        <script>
        document.addEventListener("DOMContentLoaded", function () {
            const table = document.getElementById("fight-index");
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
        <h1>Fight Directory</h1>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    <div id="index-container">
        <table id="fight-index">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Event</th>
                    <th>Location</th>
                    <th>Fight</th>
                    <th>Weight Class</th>
                    <th>Fight Duration</th>
                    <th>Result</th>
                    <th>Fighter</th>
                    <th></th>
                    <th>Fighter</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
    """

    # Populate the table with each unique game
    for _, row in unique_fights.iterrows():
        date = row['date']
        event = row['event']
        event_id = row['eventID']
        fight_location = row['location']
        weight_class = row['weight_class']
        fight_name = row['fight']
        fight_id = row['fightID']
        result = row['result']
        fight_duration = row['fight_duration']
        fighter_name = row['fighter']
        fighter_id = row['fighterID']
        outcome = row['outcome']
        opp_name = row['opp']
        opp_id = row['oppID']
        opp_outcome = row['oppOutcome']

        html_content += f"""
                <tr>
                    <td style="text-align:left">{date}</td>
                    <td style="text-align:left"><a href="/ufc/events/{event_id}.html">{event}</td>
                    <td style="text-align:left">{fight_location}</td>
                    <td style="text-align:left"><a href="/ufc/fights/{fight_id}.html">{fight_name}</td>
                    <td style="text-align:left">{weight_class}</td>
                    <td style="text-align:left">{fight_duration}</td>
                    <td style="text-align:left">{result}</td>
                    <td style="text-align:left"><a href="/ufc/fighters/{fighter_id}.html">{fighter_name}</a></td>
                    <td style="text-align:center">{outcome}</td>
                    <td style="text-align:left"><a href="/ufc/fighters/{opp_id}.html">{opp_name}</a></td>
                    <td style="text-align:center">{opp_outcome}</td>
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
output_file_path = os.path.join(output_dir_fight_index, "index.html")
create_game_directory(fight_data, output_file_path)

