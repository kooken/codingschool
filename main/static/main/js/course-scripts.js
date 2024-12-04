function toggleLeftPanel() {
    const leftPanel = document.querySelector('.left-panel');
    const rightPanel = document.querySelector('.right-panel');
    const toggleButton = document.querySelector('.toggle-panel-button');

    leftPanel.classList.toggle('hidden');
    rightPanel.classList.toggle('full-width');

    if (leftPanel.classList.contains('hidden')) {
        toggleButton.textContent = "Show Lessons";
    } else {
        toggleButton.textContent = "Hide Lessons";
    }
}

function toggleVideoVisibility() {
    const videoFrame = document.querySelector('.video-frame');
    const button = document.querySelector('.toggle-video-button');

    if (videoFrame.classList.contains('hidden')) {
        videoFrame.classList.remove('hidden');
        button.textContent = 'Hide Video';
    } else {
        videoFrame.classList.add('hidden');
        button.textContent = 'Show Video';
    }
}

function toggleSection(sectionId, button, sectionClass, buttonClass) {
    console.log("Looking for sections with class:", sectionClass);
    console.log("Looking for buttons with class:", buttonClass);

    const targetSection = document.getElementById(sectionId);

    if (!targetSection) {
        console.error("Target section not found:", sectionId);
        return;
    }

    const isCurrentlyVisible = targetSection.classList.contains("active");
    console.log("Target section is active:", isCurrentlyVisible);

    document.querySelectorAll(".section").forEach((section, index) => {
        if (section.classList.contains("active")) {
            console.log(`Hiding section #${index}:`, section.id);
        }
        section.classList.remove("active");
    });

    document.querySelectorAll(`.${buttonClass}`).forEach((btn, index) => {
        if (btn.classList.contains("active")) {
            console.log(`Remove button activity #${index}:`, btn.textContent);
        }
        btn.classList.remove("active");
    });

    if (!isCurrentlyVisible) {
        console.log("Making section active:", sectionId);
        targetSection.classList.add("active");
        button.classList.add("active");
    } else {
        console.log("Section is already active.");
    }

    const activeSection = document.querySelector(".section.active");
    const activeButton = document.querySelector(`.${buttonClass}.active`);
    console.log("Current active session:", activeSection ? activeSection.id : "Нет");
    console.log("Current active button:", activeButton ? activeButton.textContent : "Нет");
}


document.querySelectorAll('input[type="radio"]').forEach(radio => {
    if (radio.checked) {
        const selectedLabel = radio.closest('label');
        if (selectedLabel) selectedLabel.style.color = '#b07afe';
    }

    radio.addEventListener('change', function () {
        const questionName = this.name;
        document.querySelectorAll(`input[name="${questionName}"]`).forEach(r => {
            const label = r.closest('label');
            if (label) label.style.color = '';
        });

        const selectedLabel = this.closest('label');
        if (selectedLabel) selectedLabel.style.color = '#b07afe';
    });
});

document.getElementById('test-form').addEventListener('submit', function (e) {
e.preventDefault();

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
            document.getElementById('attempts-count').textContent = `Attempts: ${data.attempts}`;
            document.getElementById('score-percentage').textContent = `Max Score: ${data.percentage}%`;

            document.getElementById('test-form').style.display = 'none';

            alert('Test submitted successfully!');
        } else {
            alert('Submission failed. Please try again.');
        }
    })
    .catch(error => console.error('Error:', error));
});