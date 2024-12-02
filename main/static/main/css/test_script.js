document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.getElementById('body');

    const header = document.querySelector('header');

    const savedTheme = localStorage.getItem('theme') || 'light';
    body.classList.add(savedTheme);
    header.classList.add(savedTheme);
    themeToggle.checked = savedTheme === 'dark';

    themeToggle.addEventListener('change', () => {
        const isDark = themeToggle.checked;
        if (isDark) {
            body.classList.add('dark');
            body.classList.remove('light');
            header.classList.add('dark');
            header.classList.remove('light');
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.add('light');
            body.classList.remove('dark');
            header.classList.add('light');
            header.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    });
});