// scripts.js

// Получение CSRF-токена из cookies
const getCSRFToken = (name = 'csrftoken') => {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
};

const csrftoken = getCSRFToken();

// Настройка AJAX для включения CSRF-токена в заголовки
$.ajaxSetup({
    headers: { 'X-CSRFToken': csrftoken },
    error: function(xhr, status, error) {
        console.error(`AJAX Error: ${status} - ${error}`);
    }
});

// Функция для отображения уведомлений пользователю
const showNotification = (message, type = 'success') => {
    // Типы: success, danger, info, warning
    const notification = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
        </div>
    `);
    $('.container').prepend(notification);
    setTimeout(() => {
        notification.alert('close');
    }, 5000); // Удаление уведомления через 5 секунд
};

// Общая функция для обработки лайков и дизлайков
const handleVote = (action, commentId, button) => {
    $.ajax({
        url: `/comments/${commentId}/${action}/`,
        type: 'POST',
        success: function(data) {
            const { likes_count, dislikes_count, liked, disliked } = data;

            // Обновление счётчиков
            button.find(`.${action === 'like' ? 'likes-count' : 'dislikes-count'}`).text(action === 'like' ? likes_count : dislikes_count);

            // Поиск соответствующей кнопки (лайк/дизлайк)
            const oppositeAction = action === 'like' ? 'dislike' : 'like';
            const oppositeButton = $(`[data-id="${commentId}"].${oppositeAction}-btn`);
            oppositeButton.find(`.${oppositeAction === 'like' ? 'likes-count' : 'dislikes-count'}`).text(oppositeAction === 'like' ? data.likes_count : data.dislikes_count);

            // Визуальное подтверждение для текущей кнопки
            if ((action === 'like' && liked) || (action === 'dislike' && disliked)) {
                button.removeClass(`btn-outline-${action === 'like' ? 'success' : 'danger'}`).addClass(`${action === 'like' ? 'btn-success' : 'btn-danger'}`);
            } else {
                button.removeClass(`${action === 'like' ? 'btn-success' : 'btn-danger'}`).addClass(`btn-outline-${action === 'like' ? 'success' : 'danger'}`);
            }

            // Сброс стилей для противоположной кнопки
            oppositeButton.removeClass(`btn-success btn-danger`).addClass(`btn-outline-${action === 'like' ? 'danger' : 'success'}`);

            // Отображение уведомления
            showNotification(`Вы ${liked ? 'лайкнули' : 'убрали лайк'} комментарий.`, 'success');
        },
        error: function(xhr, status, error) {
            console.error(`Error: ${status} - ${error}`);
            showNotification('Произошла ошибка. Пожалуйста, попробуйте позже.', 'danger');
        }
    });
};

// Использование event delegation для обработки кликов на лайки и дизлайки
$(document).ready(function(){
    // Обработка кликов на кнопки лайка
    $(document).on('click', '.like-btn', function(e){
        e.preventDefault();
        const commentId = $(this).data('id');
        handleVote('like', commentId, $(this));
    });

    // Обработка кликов на кнопки дизлайка
    $(document).on('click', '.dislike-btn', function(e){
        e.preventDefault();
        const commentId = $(this).data('id');
        handleVote('dislike', commentId, $(this));
    });
});
