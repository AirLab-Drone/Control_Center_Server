let DroneChart = null;

function loadDroneData() {
    fetch('/drone_data')
        .then(response => response.json())
        .then(data => {
            // 初始化圖表
            drawChart(data);

            const accordion = document.querySelector('.accordion');
            accordion.innerHTML = ''; // 清空原有內容

            // 動態生成折疊區域
            data.forEach(item => {
                const section = document.createElement('div');
                section.className = 'accordion-item';
                section.innerHTML = `
                    <div class="accordion-header">
                        <span>Upload Time: ${formatTimeWithoutSeconds(item.upload_time)} </span>
                        <div class="error-code-header"
                            data-bs-toggle="tooltip"
                            data-bs-html="true"
                            data-bs-placement="top"
                            data-error-code='${item.error_code}' 
                            title=""
                            <strong>Error Code:</strong> ${JSON.parse(item.error_code).join(', ')}
                        </div>
                    </div>
                    <div class="accordion-content">
                        <p><strong>Upload Time:</strong> ${item.upload_time}</p>
                        <p><strong>Battery Voltage:</strong> ${item.battery_voltage ?? 'N/A'}</p>
                        <p><strong>Battery Current:</strong> ${item.battery_current ?? 'N/A'}</p>
                        <p><strong>GPS HDOP:</strong> ${item.gps_hdop ?? 'N/A'}</p>
                        <p><strong>GPS Satellites Visible:</strong> ${item.gps_satellites_visible ?? 'N/A'}</p>
                        <p><strong>Attitude Roll:</strong> ${item.attitude_roll ?? 'N/A'}</p>
                        <p><strong>Attitude Pitch:</strong> ${item.attitude_pitch ?? 'N/A'}</p>
                        <p><strong>Attitude Yaw:</strong> ${item.attitude_yaw ?? 'N/A'}</p>
                        <p><strong>Servo Output 1:</strong> ${item.servo_output_1 ?? 'N/A'}</p>
                        <p><strong>Servo Output 2:</strong> ${item.servo_output_2 ?? 'N/A'}</p>
                        <p><strong>Servo Output 3:</strong> ${item.servo_output_3 ?? 'N/A'}</p>
                        <p><strong>Servo Output 4:</strong> ${item.servo_output_4 ?? 'N/A'}</p>
                        <p><strong>Servo Output 5:</strong> ${item.servo_output_5 ?? 'N/A'}</p>
                        <p><strong>Servo Output 6:</strong> ${item.servo_output_6 ?? 'N/A'}</p>
                        <p class="error-code"><strong>Error Code:</strong> ${parseErrorCode(item.error_code)}</p>
                        </div>
                        `;
                        accordion.appendChild(section);

                        // **初始化 Tooltip**
                        const errorCodeHeader = section.querySelector('.error-code-header');
                        if (errorCodeHeader) {
                            new bootstrap.Tooltip(errorCodeHeader);
                        }
            });

        })
        .catch(error => {
            console.error('Error loading drone data:', error);
        });
}


// 格式化時間去掉秒數
function formatTimeWithoutSeconds(datetime) {
    const date = new Date(datetime);

    // 格式化為 "YYYY-MM-DD HH:MM"
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}


function parseErrorCode(errorCode) {
    if (!errorCode) return '<span style="color:rgb(48, 196, 40);">No Error</span>';


    try {
        const codes = JSON.parse(errorCode);
        return codes.map(code => `<span style="color: #d9534f;">${code}</span>`);

    } catch (e) {
        console.error('Error parsing error code:', e);
        return '<span style="color: #d9534f;">Invalid error code format.</span>';
    }
}

// 定義 showErrorCodeDetail 函數（生成 HTML 格式的 Tooltip 內容）
function showErrorCodeDetail(errorCode) {
    if (!errorCode) return '<strong>No Error</strong>';
    try {
        const codes = JSON.parse(errorCode); // 假設 errorCode 是 JSON 格式
        return `<div><span class="tooltiptile">Error Code:</span><br>${codes.map((code) => `${code}: ${ERROR_CODE[code] || 'Unknown Error'}`).join('<br>')}</div>`;
    } catch (e) {
        console.error('Error parsing error code:', e);
        return '<strong>Invalid error code format.</strong>';
    }
}

function drawChart(data) {
    const ctx = document.getElementById('Drone-Status-Chart').getContext('2d');

    if (DroneChart) {
        DroneChart.destroy();
    }

    const labels = data.map(item => formatTimeWithoutSeconds(item.upload_time));
    const datasets = [
        createDataset('Battery Voltage', data.map(item => item.battery_voltage ?? 0), 'rgba(75, 192, 192, 1)'),
        createDataset('Battery Current', data.map(item => item.battery_current ?? 0), 'rgba(255, 99, 132, 1)'),
        createDataset('GPS HDOP', data.map(item => item.gps_hdop ?? 0), 'rgba(255, 206, 86, 1)'),
        createDataset('GPS Satellites Visible', data.map(item => item.gps_satellites_visible ?? 0), 'rgba(153, 102, 255, 1)'),
        createDataset('Attitude Roll', data.map(item => item.attitude_roll ?? 0), 'rgba(255, 159, 64, 1)'),
        createDataset('Attitude Pitch', data.map(item => item.attitude_pitch ?? 0), 'rgba(0, 128, 0, 1)'),
        createDataset('Attitude Yaw', data.map(item => item.attitude_yaw ?? 0), 'rgba(128, 0, 128, 1)'),
        createDataset('Servo Output 1', data.map(item => item.servo_output_1 ?? 0), 'rgba(0, 0, 255, 1)'),
        createDataset('Servo Output 2', data.map(item => item.servo_output_2 ?? 0), 'rgba(255, 0, 0, 1)'),
        createDataset('Servo Output 3', data.map(item => item.servo_output_3 ?? 0), 'rgba(0, 255, 0, 1)'),
        createDataset('Servo Output 4', data.map(item => item.servo_output_4 ?? 0), 'rgba(128, 128, 0, 1)'),
        createDataset('Servo Output 5', data.map(item => item.servo_output_5 ?? 0), 'rgba(128, 0, 0, 1)'),
        createDataset('Servo Output 6', data.map(item => item.servo_output_6 ?? 0), 'rgba(0, 128, 128, 1)'),
    ];

    DroneChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: { 
                legend: { 
                    display: true,
                    position: 'right'
                } 
            },
            scales: {
                x: { display: true, title: { display: true, text: 'Upload Time' } },
                y: { display: true, title: { display: true, text: 'Values' } },
            },
        },
    });
}

function createDataset(label, data, color) {
    return {
        label,
        data,
        borderColor: color,
        borderWidth: 2,
        fill: false,
        hidden: true,
    };
}


document.addEventListener("DOMContentLoaded", function () {
    const container = document.body; // 假設所有動態生成的元素都在 body 或某個容器內

    // 啟用 Bootstrap Tooltip
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 監聽容器上的 mouseover 事件
    container.addEventListener("mouseover", function (event) {
        const target = event.target;

        // 檢查滑鼠是否進入帶有 error-code-header 類別的元素
        if (target.classList.contains("error-code-header")) {
            const errorCode = target.dataset.errorCode; // 從自訂屬性取得錯誤碼資料
            const tooltipContent = showErrorCodeDetail(errorCode); // 產生 Tooltip 內容

            // 設置 Tooltip 內容
            target.setAttribute('data-bs-original-title', tooltipContent);

            // 手動顯示 Tooltip
            const tooltip = bootstrap.Tooltip.getOrCreateInstance(target);
            tooltip.show();

        }
    });

    // 監聽容器上的 mouseout 事件
    container.addEventListener("mouseout", function (event) {
        const target = event.target;

        // 檢查滑鼠是否離開帶有 error-code-header 類別的元素
        if (target.classList.contains("error-code-header")) {
            // 手動隱藏 Tooltip
            const tooltip = bootstrap.Tooltip.getInstance(target);
            if (tooltip) tooltip.hide();
        }
    });
});