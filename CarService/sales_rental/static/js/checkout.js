function calculateTotal() {
    const rentalPricePerDay = parseFloat(document.getElementById('rentalPricePerDay').value);
    const startDate = new Date(document.getElementById('startdate').value);
    const endDate = new Date(document.getElementById('enddate').value);
    const totalPriceElement = document.getElementById('totalPrice');
    const rentalDaysDisplay = document.getElementById('rentalDaysDisplay');

    if (startDate && endDate && startDate < endDate) {
        const timeDifference = endDate - startDate;
        const rentalDays = Math.ceil(timeDifference / (1000 * 3600 * 24)); // Ensure full day calculation
        const totalPrice = rentalPricePerDay * rentalDays;
        totalPriceElement.innerText = `$${totalPrice.toFixed(2)}`;
        rentalDaysDisplay.innerText = rentalDays;
    } else {
        totalPriceElement.innerText = "Invalid date range";
        rentalDaysDisplay.innerText = 0;
    }
}

function validateForm() {
    const currentDateTime = new Date();
    const startDateInput = document.getElementById('startdate');
    const endDateInput = document.getElementById('enddate');
    const pickUpDateInput = document.getElementById('pickupdate');
    const transactionType = document.querySelector('input[name="transaction_type"]').value;

    if (transactionType === "rent") {
        if (startDateInput) {
            const startDate = new Date(startDateInput.value);
            if (startDate < currentDateTime) {
                alert("Start date cannot be before the current time.");
                return false;
            }

            if (endDateInput) {
                const endDate = new Date(endDateInput.value);
                if (endDate < startDate) {
                    alert("End date cannot be before the start date.");
                    return false;
                }
            }
        }
    } else {
        if (pickUpDateInput) {
            const pickUpDate = new Date(pickUpDateInput.value);
            if (pickUpDate < currentDateTime) {
                alert("Pickup date cannot be before the current time.");
                return false;
            }
        }
    }

    return true;
}

