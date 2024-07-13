const imgThumbs = document.querySelectorAll(".img-thumbs");
const previewProduct = document.querySelector("#product-preview");
const showcase = document.querySelector(".showcase");
const productPreviewShowcase = document.querySelector("#product-preview-showcase");
const closeShowcase = document.querySelector(".close-showcase");
const buyNowBtn = document.querySelector("#buy-now-btn");
const rentNowBtn = document.querySelector("#rent-now-btn");
const menuToggle = document.querySelector(".menu-toggle");
const closeMenu = document.querySelector(".close-menu");
const overlay = document.querySelector(".overlay");
const linksMenu = document.querySelector(".links");

// Update the main image when clicking on thumbnails
imgThumbs.forEach(imgThumb => {
    imgThumb.addEventListener("click", () => {
        imgThumbs.forEach(thumb => thumb.classList.remove("active"));
        imgThumb.classList.add("active");
        previewProduct.src = imgThumb.querySelector("img").src;  // Update main image
    });
});

// Show the modal with the main image when it's clicked
previewProduct.addEventListener("click", () => {
    productPreviewShowcase.src = previewProduct.src;  // Set modal image source to main image source
    showcase.style.display = "flex";  // Show the modal
});

// Close the modal
closeShowcase.addEventListener("click", () => {
    showcase.style.display = "none";
});

// Menu toggle functionality
menuToggle.addEventListener("click", () => {
    linksMenu.style.left = "0";
    overlay.style.display = "block";
});

// Close menu functionality
closeMenu.addEventListener("click", () => {
    linksMenu.style.left = "-200px";
    overlay.style.display = "none";
});

// Buy now button functionality
if (buyNowBtn) {
    buyNowBtn.addEventListener("click", () => {
        const url = buyNowBtn.getAttribute('data-url');
        const type = buyNowBtn.getAttribute('data-type');
        const carId = buyNowBtn.getAttribute('data-car-id');
        window.location.href = `${url}?type=${type}&car_id=${carId}`;
    });
}

// Rent now button functionality
if (rentNowBtn) {
    rentNowBtn.addEventListener("click", () => {
        const url = rentNowBtn.getAttribute('data-url');
        const type = rentNowBtn.getAttribute('data-type');
        const carId = rentNowBtn.getAttribute('data-car-id');
        window.location.href = `${url}?type=${type}&car_id=${carId}`;
    });
}

