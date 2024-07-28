def open_scroller():
    """Js функция для симуляции прокрутки страницы
    version = 0.1
    """
    with open("../helpers/scrollFunc.js", 'r') as file:
        return file.read()


LAUNCH_ARGS = ['--disable-blink-features=AutomationControlled']
