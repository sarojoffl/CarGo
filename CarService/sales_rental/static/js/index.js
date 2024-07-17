document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('menu-btn');
    const closeBtn = document.getElementById('close-btn');
    const sidebar = document.querySelector('aside');

    menuBtn.addEventListener('click', () => {
        sidebar.style.display = 'block';
    });

    closeBtn.addEventListener('click', () => {
        sidebar.style.display = 'none';
    });
});

