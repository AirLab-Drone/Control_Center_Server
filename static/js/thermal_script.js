// let temperatureUpdateInterval = null;
let cameraStatusInterval = null;

function checkThermalCameraStatus(source, imageElementId, temperatureElementId) {
    const imageElement = document.getElementById(imageElementId);

    fetch(`/thermal_camera_status/${source}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "online") {
                imageElement.src = `/video_feed/${source}`;
            } else {
                imageElement.src = `/static/no_signal.png`;
            }
        })
        .catch(error => {
            console.error(`Error checking status for ${source}:`, error);
            imageElement.src = `/static/no_signal.png`;
        });

    const temperatureElement = document.getElementById(temperatureElementId);

    fetch(`/latest_temperature/${source}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.temperature !== "None") {
                temperatureElement.innerText = `${data.temperature} °C`;
            } else {
                temperatureElement.innerText = "N/A";
            }
        })
        .catch(error => {
            console.error(`Error fetching temperature for ${source}:`, error);
            temperatureElement.innerText = "Error";
        });
}

// function fetchTemperature(source, elementId) {


//     fetch(`/latest_temperature/${source}`)
//         .then(response => response.json())
//         .then(data => {
//             if (data.temperature !== "None") {
//                 document.getElementById(elementId).innerText = `${data.temperature} °C`;
//             } else {
//                 document.getElementById(elementId).innerText = "N/A";
//             }
//         })
//         .catch(error => {
//             console.error(`Error fetching temperature for ${source}:`, error);
//         });
// }

// 啟動所有的更新定時器
function startThermalUpdates() {
    // 清除已有的定時器
    stopThermalUpdates();

    // 啟動檢查狀態的定時器（每 1 秒執行一次）
    cameraStatusInterval = setInterval(function() {
        checkThermalCameraStatus('ipt430m', 'image_ipt430m', 'temperature_ipt430m');
        checkThermalCameraStatus('ds4025ft', 'image_ds4025ft', 'temperature_ds4025ft');
    }, 5000);

    // // 啟動更新溫度的定時器（每 0.5 秒執行一次）
    // temperatureUpdateInterval = setInterval(function() {
    //     fetchTemperature('ipt430m', 'temperature_ipt430m');
    //     fetchTemperature('ds4025ft', 'temperature_ds4025ft');
    // }, 500);
}

// 停止所有的更新定時器
function stopThermalUpdates() {
    // if (temperatureUpdateInterval) {
    //     clearInterval(temperatureUpdateInterval);
    //     temperatureUpdateInterval = null;
    // }
    if (cameraStatusInterval) {
        clearInterval(cameraStatusInterval);
        cameraStatusInterval = null;
    }
}