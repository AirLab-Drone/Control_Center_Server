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
                        <span>Upload Time: ${item.upload_time} </span>
                        <p class="error-code"><strong>Error Code:</strong> ${item.error_code}</p>
                    </div>
                    <div class="accordion-content">
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
            });
        })
        .catch(error => {
            console.error('Error loading drone data:', error);
        });
}

function parseErrorCode(errorCode) {
    if (!errorCode) return 'No error codes.';


    try {
        const codes = JSON.parse(errorCode);
        return codes.map(code => `<span style="color: #d9534f;">${code}: ${ERROR_CODE[code] || 'Unknown Error'}</span>`).join('<br>');
    } catch (e) {
        console.error('Error parsing error code:', e);
        return 'Invalid error code format.';
    }
}

function drawChart(data) {
    const ctx = document.getElementById('Drone-Status-Chart').getContext('2d');

    if (DroneChart) {
        DroneChart.destroy();
    }

    const labels = data.map(item => item.upload_time);
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
            plugins: { legend: { display: true } },
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
    };
}