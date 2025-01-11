$(document).ready(function () {
    // 獲取 Canvas 元素並提取數據
    const canvas = document.getElementById('status-chart');

    if (!canvas) {
        console.error("Canvas element with id 'status-chart' not found!");
        return; // 防止後續程式繼續執行
    }

    const onlineCount = parseInt(canvas.getAttribute('data-online'), 10);
    const offlineCount = parseInt(canvas.getAttribute('data-offline'), 10);

    // 初始化 Chart.js 圖表
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Online', 'Offline'],
            datasets: [{
                label: 'UP Squared Service Status',
                data: [onlineCount, offlineCount],
                backgroundColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)']
            }]
        },
        options: {
            responsive: true,
        }
    });
});
