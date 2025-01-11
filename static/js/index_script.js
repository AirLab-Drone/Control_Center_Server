
function loadData(type) {
    const contentArea = document.getElementById('content-area');
    if (type === "Thermal") {
        fetch('/thermal_content')
            .then(response => response.text())
            .then(data => {
                contentArea.innerHTML = data;
            })
            .catch(error => {
                console.error('Error loading thermal content:', error);
                contentArea.innerHTML = '<p>Failed to load Thermal Camera content.</p>';
            });
        startThermalUpdates(); // 啟動溫度更新
    } else if (type === "Drone") {
        stopThermalUpdates();

        fetch('/drone_content')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.text();
            })
            .then(data => {
                contentArea.innerHTML = data;
                loadDroneData(); // 加載 Drone 數據
            })
            .catch(error => {
                console.error('Error loading drone content:', error);
                contentArea.innerHTML = '<p>Failed to load Drone content.</p>';
            });
    } else if (type === "UPS") {
        stopThermalUpdates();

        fetch('/ups_content')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            contentArea.innerHTML = data;
            
        })
        .catch(error => {
            console.error('Error loading drone content:', error);
            contentArea.innerHTML = '<p>Failed to load UPS content.</p>';
        });



    } else {
        stopThermalUpdates();
        contentArea.innerHTML = `<h2>${type} Data</h2><p>Coming soon...</p>`;
    }
}



