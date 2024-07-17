const lowCostCars = ['Ford Fiesta', 'Chevrolet Spark', 'Nissan Versa', 'Hyundai Accent'];

    document.getElementById('search-btn').addEventListener('click', function() {
        const suggestions = document.getElementById('search-suggestions');
        suggestions.innerHTML = '';

        lowCostCars.forEach(car => {
            const p = document.createElement('p');
            p.textContent = car;
            suggestions.appendChild(p);
        });

        suggestions.style.display = 'block';
    });

    document.addEventListener('click', function(e) {
        const suggestions = document.getElementById('search-suggestions');
        if (!document.querySelector('.search-button').contains(e.target)) {
            suggestions.style.display = 'none';
        }
    });

    // Toggle mobile menu
    const menuToggle = document.getElementById('mobile-menu');
    const nav = document.querySelector('nav');

    menuToggle.addEventListener('click', function() {
        nav.classList.toggle('active');
    });
});

