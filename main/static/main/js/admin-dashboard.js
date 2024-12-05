function setReviewedAt(submissionId) {
    const now = new Date();
    const reviewedAtField = document.getElementById('reviewed_at_' + submissionId);
    const currentDateTime = now.toISOString().slice(0, 16);
    reviewedAtField.value = currentDateTime;
}