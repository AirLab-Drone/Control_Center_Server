let currentPage = 1; // 當前頁數
const perPage = 20; // 每頁顯示的資料筆數

// 加載 UP Squared 數據
function loadUpsData(page = 1) {
    fetch(`/ups_data?page=${page}&per_page=20`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#ups-data-table tbody');
            const paginationContainer = document.querySelector('#pagination');

            // 確保 DOM 元素存在
            if (!tableBody) {
                console.error('Table body not found!');
                return;
            }
            if (!paginationContainer) {
                console.error('Pagination container not found!');
                return;
            }

            // 清空現有內容
            tableBody.innerHTML = '';
            paginationContainer.innerHTML = '';

            // 插入數據到表格
            data.data.forEach(status => {
                // 動態設置狀態顏色
                const serviceStatusClass = status.up_squared_service === "Online" ? "text-success" : "text-danger";
                const rgbStatusClass = status.rgb_status === "Active" ? "text-success" : "text-danger";
                const thermalStatusClass = status.thermal_status === "Active" ? "text-success" : "text-danger";

                // 格式化 error_code，如果是 JSON 字串就解析，否則直接顯示
                let errorCodeDisplay = "No Error";
                try {
                    const errorCodes = JSON.parse(status.error_code);
                    if (Array.isArray(errorCodes) && errorCodes.length > 0) {
                        errorCodeDisplay = errorCodes.join(", "); // 將錯誤碼用逗號分隔
                    }
                } catch (e) {
                    if (status.error_code) {
                        errorCodeDisplay = status.error_code; // 如果不是 JSON 格式，直接顯示
                    }
                }

                // 插入行
                const row = `
                    <tr>
                        <td>${status.id}</td>
                        <td>${status.date}</td>
                        <td>${status.upload_time}</td>
                        <td class="${serviceStatusClass}">${status.up_squared_service}</td>
                        <td class="${rgbStatusClass}">${status.rgb_status}</td>
                        <td class="${thermalStatusClass}">${status.thermal_status}</td>
                        <td>${errorCodeDisplay}</td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });

            // 更新分頁按鈕
            updatePagination(data.pagination);
        })
        .catch(error => {
            console.error('Error loading UP Squared data:', error);
        });
}


// 更新分頁按鈕
function updatePagination(pagination) {
    const paginationContainer = document.querySelector('#pagination');
    paginationContainer.innerHTML = ''; // 清空現有按鈕

    const { current_page, total_pages } = pagination;

    // 創建最前頁按鈕
    const firstButton = document.createElement('button');
    firstButton.textContent = '<< 最前頁';
    firstButton.className = 'btn btn-secondary m-1';
    firstButton.disabled = current_page === 1; // 如果是第一頁則禁用
    firstButton.addEventListener('click', () => loadUpsData(1));
    paginationContainer.appendChild(firstButton);

    // 創建上一頁按鈕
    const prevButton = document.createElement('button');
    prevButton.textContent = '< 上一頁';
    prevButton.className = 'btn btn-secondary m-1';
    prevButton.disabled = current_page === 1; // 如果是第一頁則禁用
    prevButton.addEventListener('click', () => loadUpsData(current_page - 1));
    paginationContainer.appendChild(prevButton);

    // 計算頁數按鈕範圍
    const startPage = Math.max(1, current_page - 1); // 最小從1開始
    const endPage = Math.min(total_pages, current_page + 1); // 最大到總頁數結束

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = 'btn btn-secondary m-1';
        pageButton.disabled = i === current_page; // 當前頁禁用按鈕
        pageButton.addEventListener('click', () => loadUpsData(i));
        paginationContainer.appendChild(pageButton);
    }

    // 創建下一頁按鈕
    const nextButton = document.createElement('button');
    nextButton.textContent = '下一頁 >';
    nextButton.className = 'btn btn-secondary m-1';
    nextButton.disabled = current_page === total_pages; // 如果是最後一頁則禁用
    nextButton.addEventListener('click', () => loadUpsData(current_page + 1));
    paginationContainer.appendChild(nextButton);

    // 創建最末頁按鈕
    const lastButton = document.createElement('button');
    lastButton.textContent = '最末頁 >>';
    lastButton.className = 'btn btn-secondary m-1';
    lastButton.disabled = current_page === total_pages; // 如果是最後一頁則禁用
    lastButton.addEventListener('click', () => loadUpsData(total_pages));
    paginationContainer.appendChild(lastButton);

    // 輸入跳轉功能
    const jumpContainer = document.createElement('div');
    jumpContainer.className = 'd-inline-block m-1';
    const jumpInput = document.createElement('input');
    jumpInput.type = 'number';
    jumpInput.className = 'form-control d-inline-block';
    jumpInput.style.width = '80px';
    jumpInput.placeholder = 'Page';
    jumpInput.min = 1;
    jumpInput.max = total_pages;

    const jumpButton = document.createElement('button');
    jumpButton.textContent = 'Go';
    jumpButton.className = 'btn btn-secondary m-1';
    jumpButton.addEventListener('click', () => {
        const targetPage = parseInt(jumpInput.value);
        if (!isNaN(targetPage) && targetPage >= 1 && targetPage <= total_pages) {
            loadUpsData(targetPage);
        } else {
            alert(`Please enter a valid page number (1-${total_pages})`);
        }
    });

    jumpContainer.appendChild(jumpInput);
    jumpContainer.appendChild(jumpButton);
    paginationContainer.appendChild(jumpContainer);
}
