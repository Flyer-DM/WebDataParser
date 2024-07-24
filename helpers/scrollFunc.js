const scrollStep = 10;
const scrollInterval = 10;

const scrollHeight = document.documentElement.scrollHeight;
let currentPosition = 0;
const interval = setInterval(() => {
    window.scrollBy(0, scrollStep);
    currentPosition += scrollStep;

    if (currentPosition >= scrollHeight) {
        clearInterval(interval);
    }
}, scrollInterval);