// Function to initialize a player's chart
function initializeChart(fighterId, chartData, bettingLine, defaultStat) {
	const processedData = chartData.map(d => ({
        ...d,
        [defaultStat]: d[defaultStat] === 0 ? 0.02 : d[defaultStat]
    }));
	
    window[`allData_${fighterId}`] = processedData;
    window[`currentStat_${fighterId}`] = defaultStat;
    window[`Line_${fighterId}`] = bettingLine;
    window[`chart_${fighterId}`] = null;

    const ctx = document.getElementById(`chart_${fighterId}`).getContext('2d');
    window[`chart_${fighterId}`] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: processedData.map(d => formatLabel(d)),
            datasets: [{
                label: defaultStat,
                data: processedData.map(d => d[defaultStat] || 0.0),
                backgroundColor: getBackgroundColors(processedData, defaultStat, bettingLine, fighterId),
                borderColor: getBorderColors(processedData, defaultStat, bettingLine, fighterId),
                borderWidth: 0.15,
                barPercentage: 1.0,
                categoryPercentage: 1.0,
				yAxisID: 'y',
				stack: 'combined'
            }]
        },
        options: getChartOptions(fighterId, bettingLine, defaultStat)
    });
}


function formatLabel(data) {
    const date = new Date(data.date);
    const formattedDate = `${date.getMonth() + 1}/${date.getDate()}/${String(date.getFullYear()).slice(-2)}`;
    
    // Return an array to create a multiline label
    return [formattedDate];
}

// Chart options with multiline labels enabled
function getChartOptions(fighterId, line, stat) {
    return {
        plugins: {
            legend: { 
				display: false 
			},
            title: {
                display: true,
                text: stat,
                font: { 
					size: 14,
					family: 'Verdana'
				},
				color: '#333333',
				padding: 4
            },
            annotation: {
                annotations: {
                    line1: {
                        type: 'line',
                        yMin: line,
                        yMax: line,
                        borderColor: '#333333',
                        borderWidth: 1.5
                    }
                }
            }
        },
        scales: {
            y: { 
				grid: { 
                    display: true,
					color: '#dfe1e2'
                },
				ticks: {
					font: {
						size: 10,
						family: 'Verdana'
					},
					color: '#333333',
					padding: 6 
				},
				beginAtZero: true, 
                stepSize: 1.0 
            },
            y1: { 
				display: false, // Hidden by default until TOI is toggled on
                position: 'right',
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'TOI'
                },
                grid: {
                    drawOnChartArea: false // Avoids overlapping grid lines
                }
			},
			x: { 
                grid: { 
                    display: false 
                },
                ticks: {
                    autoSkip: true,
                    maxRotation: 0,
                    minRotation: 0,
					font: {
						size: 9,
						family: 'Verdana'
					},
					color: '#333333',
					padding: 0 
                }
            }
        }
    };
}



// Get background colors for the chart bars based on stats
function getBackgroundColors(data, stat, line, fighterId) {
    return data.map(d => (d[stat] === 0 ? '#c01616' : (d[stat] >= line ? '#16c049' : '#c01616')));
}

// Get border colors for the chart bars
function getBorderColors(data, stat, line, fighterId) {
    return data.map(d => (d[stat] === 0 ? '#421f1f' : (d[stat] >= line ? '#304f3a' : '#421f1f')));
}


// Update the selected stat in the chart
function updateStat(fighterId, selectedStat) {
    const chart = window[`chart_${fighterId}`];
    const data = window[`allData_${fighterId}`];
    const line = window[`Line_${fighterId}`];

    window[`currentStat_${fighterId}`] = selectedStat;
    chart.data.datasets[0].data = data.map(d => d[selectedStat] || 0.0);
    chart.data.datasets[0].label = selectedStat;
    chart.options.plugins.title.text = selectedStat;
    chart.data.datasets[0].backgroundColor = getBackgroundColors(data, selectedStat, line, fighterId);
    chart.update();
}

// Update the betting line and adjust the chart annotation
function updateLine(fighterId, newLine) {
    const chart = window[`chart_${fighterId}`];
    const data = chart.data.datasets[0].data; // Use the current dataset without altering the original

    // Update the global line value
    window[`Line_${fighterId}`] = parseFloat(newLine);

    // Update the displayed line value text
    document.getElementById(`lineValue_${fighterId}`).innerText = newLine;

    // Update the annotation line on the chart
    chart.options.plugins.annotation.annotations.line1.yMin = newLine;
    chart.options.plugins.annotation.annotations.line1.yMax = newLine;

    // Update bar colors based on the new line value
    chart.data.datasets[0].backgroundColor = data.map(value => (value >= newLine ? '#16c049' : '#c01616'));
    chart.update();
}

// Apply filters (team, home/away, date range) to the chart
// Modified applyFilters function
// Modified applyFilters function
function applyFilters(fighterId) {
    const originalData = window[`allData_${fighterId}`]; // Use the original data as the base
    const stat = window[`currentStat_${fighterId}`];
    const line = window[`Line_${fighterId}`];

    const teamFilter = document.getElementById(`teamFilter_${fighterId}`).value;
    const homeAwayFilter = document.getElementById(`homeAwayFilter_${fighterId}`).value;
    const startDate = document.getElementById(`startDate_${fighterId}`).value;
    const endDate = document.getElementById(`endDate_${fighterId}`).value;

    // Check for recent games filter
    const recentGamesFilter = window[`recentGames_${fighterId}`] || null;
    const seasonFilter = window[`seasonFilter_${fighterId}`] || null;

    // Apply filters to the data based on all criteria
    let filteredData = originalData.filter(d => {
        const isTeamMatch = (teamFilter === 'all') || (d.opponent === teamFilter);
        const isLocationMatch = (homeAwayFilter === 'all') || 
                                (homeAwayFilter === 'home' && d.location === 'home') || 
                                (homeAwayFilter === 'away' && d.location === 'away');
        const isDateInRange = (!startDate || new Date(d.date) >= new Date(startDate)) &&
                              (!endDate || new Date(d.date) <= new Date(endDate));
        return isTeamMatch && isLocationMatch && isDateInRange;
    });

    // If recent games filter is active, slice the data to the last N games after other filters
    if (recentGamesFilter) {
        filteredData = filteredData.slice(-recentGamesFilter);
    } else if (seasonFilter) {
        filteredData = filteredData.filter(d => d.season === seasonFilter);
    }
	
    // Update chart with the filtered data and reset the colors
    const chart = window[`chart_${fighterId}`];
    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = filteredData.map(d => (d[stat] >= line ? '#16c049' : '#c01616'));
    chart.update();
}

// Modified showRecentGames to work with the main applyFilters function
function showRecentGames(fighterId, numGames) {
    window[`recentGames_${fighterId}`] = numGames; // Store recent games filter
	window[`seasonFilter_${fighterId}`] = null;
    applyFilters(fighterId); // Apply all filters together
}


// Modified showAllGames to reset all filters
function showAllGames(fighterId) {
    window[`recentGames_${fighterId}`] = null; // Clear recent games filter
    window[`seasonFilter_${fighterId}`] = null; // Clear season filter
    applyFilters(fighterId); // Apply all filters with no recent or season constraints
}


// Reset the filters and the betting line
function clearFilters(fighterId) {
    // Reset filter inputs to default values
    document.getElementById(`startDate_${fighterId}`).value = "";
    document.getElementById(`endDate_${fighterId}`).value = "";

    // Use original unfiltered data to reset chart
    const originalData = window[`allData_${fighterId}`];
    const stat = window[`currentStat_${fighterId}`];
    const line = window[`Line_${fighterId}`];

    const chart = window[`chart_${fighterId}`];
    chart.data.labels = originalData.map(d => formatLabel(d));
    chart.data.datasets[0].data = originalData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = originalData.map(d => (d[stat] >= line ? '#16c049' : '#c01616'));
    chart.update();
}

// Update the chart display with new filtered data
function updateChart(fighterId, filteredData, stat, line) {
    const chart = window[`chart_${fighterId}`];
    if (!chart) return; // Exit if the chart does not exist

    // Update chart data and labels with filtered data
    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = getBackgroundColors(filteredData, stat, line, fighterId);

    // Refresh the chart to reflect changes
    chart.update();
}


function applyFilter(fighterId, filterType, filterValue = null) {
    const originalData = window[`allData_${fighterId}`];
    const stat = window[`currentStat_${fighterId}`];
    const line = window[`Line_${fighterId}`];

    let filteredData = [...originalData];

    if (filterType === "recent" && filterValue) {
        filteredData = filteredData.slice(-filterValue);
    } else if (filterType === "all") {
        filteredData = originalData;
    }

    // Call updateChart with filtered data
    updateChart(fighterId, filteredData, stat, line);
}

// Function to reset the betting line and move the slider to the default value
function resetLine(fighterId, defaultLine) {
    updateLine(fighterId, defaultLine); // Update displayed line value and chart annotation
    
    // Set the slider's position to the default value
    document.getElementById(`lineSlider_${fighterId}`).value = defaultLine;
}
