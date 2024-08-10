def open_scroller():
    """Js функция для симуляции прокрутки страницы
    version = 0.1.3
    """
    return """const scrollStep = 10;
const scrollInterval = 10;

const scrollHeight = document.documentElement.scrollHeight;
let currentPosition = 0;
const interval = setInterval(() => {
    window.scrollBy(0, scrollStep);
    currentPosition += scrollStep;

    if (currentPosition >= scrollHeight) {
        clearInterval(interval);
    }
}, scrollInterval);"""


LAUNCH_ARGS = ['--disable-blink-features=AutomationControlled']
