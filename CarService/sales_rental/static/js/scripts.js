document.addEventListener('DOMContentLoaded', function() {
    // Fetch car listings for sale
    fetch('/api/cars/sale')
        .then(response => response.json())
        .then(data => {
            const saleList = document.getElementById('car-sale-list');
            data.forEach(car => {
                const carItem = document.createElement('div');
                carItem.classList.add('car-item');
                carItem.innerHTML = `
                    <h3>${car.name}</h3>
                    <p>$${car.price}</p>
                    <button onclick="addToCart('${car.name}', ${car.price})">Add to Cart</button>
                `;
                saleList.appendChild(carItem);
            });
        });

    // Fetch car listings for rent
    fetch('/api/cars/rent')
        .then(response => response.json())
        .then(data => {
            const rentalList = document.getElementById('car-rental-list');
            data.forEach(car => {
                const carItem = document.createElement('div');
                carItem.classList.add('car-item');
                carItem.innerHTML = `
                    <h3>${car.name}</h3>
                    <p>$${car.price}/day</p>
                    <button onclick="addToCart('${car.name}', ${car.price})">Add to Cart</button>
                `;
                rentalList.appendChild(carItem);
            });
        });

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

