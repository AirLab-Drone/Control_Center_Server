// let temperatureUpdateInterval = null;
let cameraStatusInterval = null;

function checkThermalCameraStatus(source, imageElementId, temperatureElementId) {
    const imageElement = document.getElementById(imageElementId);
    const temperatureElement = document.getElementById(temperatureElementId);

    fetch(`/thermal_camera_stream/${source}`)
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
            if (data.temperature !== "None") {
                temperatureElement.innerText = `${data.temperature} °C`;
            } else {
                temperatureElement.innerText = "N/A";
            }
        })
        .catch(error => {
            console.error(`Error checking status for ${source}:`, error);
            imageElement.src = `/static/no_signal.png`;
            temperatureElement.innerText = "Error";
        });


}


// 啟動所有的更新定時器
function startThermalUpdates() {
    // 清除已有的定時器
    stopThermalUpdates();

    // 啟動檢查狀態的定時器（每 0.5 秒執行一次）
    cameraStatusInterval = setInterval(function() {
        checkThermalCameraStatus('ipt430m', 'image_ipt430m', 'temperature_ipt430m');
        checkThermalCameraStatus('ds4025ft', 'image_ds4025ft', 'temperature_ds4025ft');
    }, 500);
}

// 停止所有的更新定時器
function stopThermalUpdates() {
    if (cameraStatusInterval) {
        clearInterval(cameraStatusInterval);
        cameraStatusInterval = null;
    }
}



