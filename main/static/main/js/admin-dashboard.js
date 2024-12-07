function setReviewedAt(submissionId) {
    const now = new Date();
    const reviewedAtField = document.getElementById('reviewed_at_' + submissionId);
    const currentDateTime = now.toISOString().slice(0, 16);
    reviewedAtField.value = currentDateTime;
}

document.addEventListener("DOMContentLoaded", function () {

    function filterTable() {
        var approvedCheckbox = document.getElementById('approved');
        var pendingCheckbox = document.getElementById('pending');
        var needsRevisionCheckbox = document.getElementById('needs_revision');
        var table = document.getElementById('homeworkTable');
        var rows = table.getElementsByTagName('tr');

        for (var i = 1; i < rows.length; i++) {
            var row = rows[i];
            var status = row.getAttribute('data-status');


            if ((approvedCheckbox.checked && status === 'approved') ||
                (pendingCheckbox.checked && status === 'pending') ||
                (needsRevisionCheckbox.checked && status === 'needs_revision')) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    }

    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', filterTable);
    });
});