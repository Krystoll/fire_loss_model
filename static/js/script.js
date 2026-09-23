/* ============================================================
   РАНДОМИЗАЦИЯ ВСЕХ ЗНАЧЕНИЙ
   ============================================================ */
function randomizeAllValues() {
    const inputs = document.querySelectorAll('.randomizable');
    const button = document.querySelector('.btn-random-all');

    if (button) {
        button.classList.add('pulse-animation');
        setTimeout(() => button.classList.remove('pulse-animation'), 600);
    }

    inputs.forEach(input => {
        if (input.name && input.name.startsWith('norm_bound_')) {
            input.value = (Math.random() * 1).toFixed(2);
        } else {
            input.value = Math.random().toFixed(2);
        }

        // Визуальный отклик
        input.style.background = '#FFF0F0';
        setTimeout(() => { input.style.background = ''; }, 400);
    });

    showNotification('Все значения успешно рандомизированы!', 'success');
}

/* ============================================================
   УВЕДОМЛЕНИЯ
   ============================================================ */
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 50);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 400);
    }, 3000);
}

/* ============================================================
   ОВЕРЛЕЙ ЗАГРУЗКИ ПРИ ОТПРАВКЕ ФОРМ
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const overlay = document.getElementById('loadingOverlay');
            if (!overlay) return;

            const text = overlay.querySelector('p');
            if (form.id === 'polarPlotForm') {
                text.textContent = 'Построение полярных диаграмм...';
            } else {
                text.textContent = 'Идёт расчёт модели...';
            }
            overlay.classList.add('active');
        });
    });

    // Приветствие в консоли
    console.log(
        '%c🔥 Модель ущерба от пожаров готова к работе',
        'color: #E63946; font-size: 16px; font-weight: bold;'
    );

    // Подсветка при фокусе
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.style.background = '#FFF9F9';
        });
        input.addEventListener('blur', () => {
            input.parentElement.style.background = '';
        });
    });
});