/*
document.addEventListener('DOMContentLoaded', (event) => {
    const addRowButton = document.getElementById('addRowButton');
    const container = document.getElementById('data-rows-container');

    const newRowHTML = `
        <div class="data-row">
            <input type="text" class="col-name-input" placeholder="Tên cột" required name="colum">
            <input type="text" class="col-datatype-input" placeholder="Kiểu dữ liệu" required>
            <div class="col-flags-inputs">
                <input type="checkbox" title="Primary Key">
                <input type="checkbox" title="Not Null">
                <input type="checkbox" title="Auto Increment">
            </div>
            <input type="text" class="col-default-input" placeholder="Giá trị mặc định">
        </div>
    `;

    addRowButton.addEventListener('click', () => {
        const newRow = document.createElement('div');
        newRow.innerHTML = newRowHTML.trim();
        const rowElement = newRow.firstChild; 
        container.appendChild(rowElement);
        let currentCount = parseInt(hiddenCounter.value);
        currentCount++;
        hiddenCounter.value = currentCount;
        console.log(parseInt(hiddenCounter.value))
    });
});

*/



document.addEventListener('DOMContentLoaded', (event) => {
    const addRowButton = document.getElementById('addRowButton');
    const container = document.getElementById('data-rows-container');
    
    // Đảm bảo bạn khai báo/lấy hiddenCounter ở đầu file (giả sử nó tồn tại trong HTML)
    const hiddenCounter = document.getElementById('hiddenCounter'); 

    // Template row, KHÔNG CÓ THUỘC TÍNH NAME ĐƯỢC CHỈ ĐỊNH CỤ THỂ
    const rowTemplateHTML = `
        <div class="data-row">
            <input type="text" class="col-name-input" placeholder="Tên cột" required>
            <input type="text" class="col-datatype-input" placeholder="Kiểu dữ liệu" required>
            <div class="col-flags-inputs">
                <input type="checkbox" title="Primary Key">
                <input type="checkbox" title="Not Null">
                <input type="checkbox" title="Auto Increment">
            </div>
        </div>
    `;

    addRowButton.addEventListener('click', () => {
        
        // 1. Tăng và cập nhật biến đếm
        let currentCount = parseInt(hiddenCounter.value) || 0;
        currentCount++;
        hiddenCounter.value = currentCount;
        
        // 2. Tạo phần tử DOM từ template
        const newRowContainer = document.createElement('div');
        newRowContainer.innerHTML = rowTemplateHTML.trim();
        const rowElement = newRowContainer.firstChild; 
        
        // 3. Tìm TẤT CẢ các input trong hàng mới
        const inputs = rowElement.querySelectorAll('input');

        // 4. Cập nhật thuộc tính 'name' cho TỪNG input
        inputs.forEach(input => {
            let baseName = '';
            
            // Xác định tên cơ bản dựa trên class hoặc type/title
            if (input.classList.contains('col-name-input')) {
                baseName = 'col_name';
            } else if (input.classList.contains('col-datatype-input')) {
                baseName = 'col_datatype';
            } else if (input.classList.contains('col-default-input')) {
                baseName = 'col_default';
            } else if (input.type === 'checkbox') {
                // Sử dụng chữ viết tắt (PK, NN, AI) làm tên cơ bản
                baseName = input.title.replace(/\s/g, ''); 
            }
            
            // Gán thuộc tính 'name' duy nhất (ví dụ: 'col_name_1', 'NN_2', ...)
            if (baseName) {
                input.name = `${baseName}_${currentCount}`;
            }
            
            // Thêm thuộc tính required cho tên và kiểu dữ liệu
            if (input.classList.contains('col-name-input') || input.classList.contains('col-datatype-input')) {
                input.setAttribute('required', 'required');
            }
        });

        // 5. Thêm hàng mới đã có tên vào container
        container.appendChild(rowElement);
        console.log(`Đã thêm hàng ${currentCount} với tên bắt đầu từ: col_name_${currentCount}`);
    });
});