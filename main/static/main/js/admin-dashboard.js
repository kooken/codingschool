function setReviewedAt(submissionId) {
    const now = new Date();
    const reviewedAtField = document.getElementById('reviewed_at_' + submissionId);
    const currentDateTime = now.toISOString().slice(0, 16);
    reviewedAtField.value = currentDateTime;
}

document.addEventListener('DOMContentLoaded', function() {
    const columnHeaders = document.querySelectorAll('.toggle-column');

    columnHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const columnId = header.getAttribute('data-target');
            const columnCards = document.querySelectorAll(`#${columnId} .submission-card`);

            columnCards.forEach(card => {
                if (card.style.display === 'none') {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});