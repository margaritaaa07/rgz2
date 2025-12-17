document.addEventListener('DOMContentLoaded', function() {
    const tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltips.map(function (el) {
        return new bootstrap.Tooltip(el);
    });

    const popovers = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popovers.map(function (el) {
        return new bootstrap.Popover(el);
    });

    const currentYear = new Date().getFullYear();
    const yearElements = document.querySelectorAll('.current-year');
    yearElements.forEach(el => {
        el.textContent = currentYear;
    });
});

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container:first-of-type') || document.body;
    container.prepend(alertDiv);

    setTimeout(() => {
        if (alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

function toggleWeekSelection(element) {
    const weekId = element.dataset.weekId;
    const isSelected = element.classList.contains('selected');
    
    if (isSelected) {
        const weekNumber = element.querySelector('.week-number').textContent.replace('Неделя ', '');
        confirmAction(`Отменить отпуск на неделю ${weekNumber}?`, function() {
            const form = element.querySelector('form');
            if (form) form.submit();
        });
    } else {
        const weekNumber = element.querySelector('.week-number').textContent.replace('Неделя ', '');
        confirmAction(`Выбрать неделю ${weekNumber} для отпуска?`, function() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/save_vacation';
            
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = document.querySelector('input[name="csrf_token"]')?.value || '';
            
            const weekInput = document.createElement('input');
            weekInput.type = 'hidden';
            weekInput.name = 'week_number';
            weekInput.value = weekNumber;
            
            form.appendChild(csrfInput);
            form.appendChild(weekInput);
            document.body.appendChild(form);
            form.submit();
        });
    }
}

function filterTable(tableId, inputId, columnIndex) {
    const input = document.getElementById(inputId);
    const filter = input.value.toUpperCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        const cell = rows[i].getElementsByTagName('td')[columnIndex];
        if (cell) {
            const txtValue = cell.textContent || cell.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    }
}