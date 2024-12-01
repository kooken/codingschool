 function toggleLeftPanel() {
        const leftPanel = document.querySelector('.left-panel');
        const rightPanel = document.querySelector('.right-panel');
        const toggleButton = document.querySelector('.toggle-button');

        leftPanel.classList.toggle('hidden');
        rightPanel.classList.toggle('full-width');

        if (leftPanel.classList.contains('hidden')) {
            toggleButton.textContent = "Show Lessons";
        } else {
            toggleButton.textContent = "Hide Lessons";
        }
    }

    function toggleTestSection(testId) {
        const testSection = document.getElementById(testId);
        if (testSection.style.display === "none") {
            testSection.style.display = "block";
        } else {
            testSection.style.display = "none";
        }
    }

    function toggleHomeworkSection(homeworkId) {
        const homeworkSection = document.getElementById(homeworkId);
        if (homeworkSection.style.display === "none") {
            homeworkSection.style.display = "block";
        } else {
            homeworkSection.style.display = "none";
        }
    }

    function toggleCommentsSection(commentsId) {
        const commentsSection = document.getElementById(commentsId);
        if (commentsSection.style.display === "none") {
            commentsSection.style.display = "block";
        } else {
            commentsSection.style.display = "none";
        }
    }

    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        // При загрузке страницы подсвечиваем уже выбранные ответы
        if (radio.checked) {
            const selectedLabel = radio.closest('label');
            if (selectedLabel) selectedLabel.style.color = '#b07afe'; // Задаем цвет текста
        }

        // Событие изменения радиокнопки
        radio.addEventListener('change', function () {
            // Сброс подсветки у всех кнопок в рамках текущего вопроса
            const questionName = this.name;
            document.querySelectorAll(`input[name="${questionName}"]`).forEach(r => {
                const label = r.closest('label');
                if (label) label.style.color = ''; // Убираем цвет текста
            });

            // Подсвечиваем выбранный вариант
            const selectedLabel = this.closest('label');
            if (selectedLabel) selectedLabel.style.color = '#b07afe'; // Задаем цвет текста
        });
    });

    document.getElementById('test-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Отмена стандартной отправки формы

    const formData = new FormData(this);

    fetch(this.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Test submitted successfully.") {
                // Обновляем данные о попытках и процентах
                document.getElementById('attempts-count').textContent = `Attempts: ${data.attempts}`;
                document.getElementById('score-percentage').textContent = `Max Score: ${data.percentage}%`;

                // Прячем форму
                document.getElementById('test-form').style.display = 'none';

                alert('Test submitted successfully!');
            } else {
                alert('Submission failed. Please try again.');
            }
        })
        .catch(error => console.error('Error:', error));
});