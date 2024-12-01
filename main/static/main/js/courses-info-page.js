 console.log('JavaScript loaded');

    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            console.log('Clicked tab:', tab);

            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(content => content.classList.remove('active'));

            tab.classList.add('active');

            const contentToShow = document.getElementById(tab.dataset.tab);
            console.log('Showing content:', contentToShow);

            if (contentToShow) {
                contentToShow.classList.add('active');
            }
        });
    });

    if (tabs.length > 0) {
        tabs[0].classList.add('active');
        const firstContent = document.getElementById(tabs[0].dataset.tab);
        if (firstContent) {
            firstContent.classList.add('active');
        }
    }