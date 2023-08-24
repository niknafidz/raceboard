// Function to fetch and process CSV data
function fetchData() {
    fetch('scanned_data_log.csv')
        .then(response => response.text())
        .then(data => {
            const rows = data.split('\n');
            const category1000 = [];
            const category600 = [];
            const category400 = [];
            const racerMap = new Map(); // Store racer data by name

            rows.forEach(row => {
                const [dateTime, idNumber, name, cc, totalTimeSec, lastLapTimeSec, totalTime, lastLapTime, lapRound] = row.split(',');

                const racer = {
                    name,
                    totalTime,
                    lastLapTime,
                    lapRound: parseInt(lapRound),
                };

                // Check if racer already exists in the map
                if (racerMap.has(name)) {
                    // Update lap data if needed
                    const existingRacer = racerMap.get(name);
                    if (lapRound > existingRacer.lapRound) {
                        existingRacer.totalTime = totalTime;
                        existingRacer.lastLapTime = lastLapTime;
                        existingRacer.lapRound = lapRound;
                    } else if (lapRound === existingRacer.lapRound && totalTimeSec < existingRacer.totalTimeSec) {
                        existingRacer.totalTime = totalTime;
                        existingRacer.lastLapTime = lastLapTime;
                    }
                } else {
                    racerMap.set(name, racer);

                    // Categorize the racer only if it's not already in the category
                    switch (cc) {
                        case '1000 cc':
                            category1000.push(racer);
                            break;
                        case '600 cc':
                            category600.push(racer);
                            break;
                        case '400 cc':
                            category400.push(racer);
                            break;
                    }
                }
            });

            // Sort racers within each category based on lap round and total time
            category1000.sort((a, b) => compareRacers(a, b));
            category600.sort((a, b) => compareRacers(a, b));
            category400.sort((a, b) => compareRacers(a, b));

            // Display the leaderboard in HTML tables
            displayLeaderboard('category-1000-body', category1000);
            displayLeaderboard('category-600-body', category600);
            displayLeaderboard('category-400-body', category400);
        });
}

// Function to compare racers based on lap round and total time
function compareRacers(a, b) {
    if (a.lapRound !== b.lapRound) {
        return b.lapRound - a.lapRound; // Sort by lap round descending
    } else {
        // If lap rounds are the same, sort by total time ascending
        return parseFloat(a.totalTimeSec) - parseFloat(b.totalTimeSec);
    }
}


// Function to display the leaderboard data in HTML table
function displayLeaderboard(tableId, data) {
    const tableBody = document.getElementById(tableId);
    tableBody.innerHTML = '';

    // Calculate the lap round of the number one ranked racer
    const numberOneLapRound = data.length > 0 ? parseInt(data[0].lapRound) : 0;

    data.forEach((racer, index) => {
        const rank = index + 1;
        const lapRound = parseInt(racer.lapRound);

        const lapsBehind = index === 0 ? '' : `(${numberOneLapRound - lapRound} laps behind)`;
        const lastLapTimeWithLapsBehind = `${racer.lastLapTime} ${lapsBehind}`;

        const newRow = `
            <tr>
                <td>${rank}</td>
                <td>${racer.name}</td>
                <td>${racer.totalTime} / ${racer.lapRound} laps </td>
                <td>${lastLapTimeWithLapsBehind}</td>
            </tr>
        `;
        tableBody.insertAdjacentHTML('beforeend', newRow);
    });
}





// Fetch and process data when the page loads
fetchData();
