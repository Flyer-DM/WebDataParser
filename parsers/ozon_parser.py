import time
from typing import Union, Literal
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError


class Ozon:
    __version__ = "0.1"

    def __init__(self):
        """version = 0.1"""
        self.page = None
        self.goods_links: set[str] = set()
        self.base_link = "https://www.ozon.ru"

    def _get_goods_links(self, number_of_goods: Union[Literal['max'], int] = 10) -> None:
        """Сбор всех ссылок на товары. Либо собирается максимальное количество товаров, либо явно
        указанное количество (по умолчанию=10).
        version = 0.1
        """
        id_paginator_content = "#paginatorContent"
        tag_href = 'href'
        href_next_page = "Дальше"
        class_next_page = '.e6o'
        selector_next_page = f':text("{href_next_page}")'
        self.page.wait_for_selector(id_paginator_content)
        all_products = self.page.query_selector(id_paginator_content)
        links = set(all_products.query_selector_all('.tile-hover-target'))
        if number_of_goods == 'max':
            self.goods_links.update({self.base_link + link.get_attribute(tag_href) for link in links})
            if self.page.is_visible(selector_next_page):
                next_link = self.base_link + self.page.query_selector(class_next_page).get_attribute(tag_href)
                self.page.goto(next_link)
                self._get_goods_links(number_of_goods)
        else:
            for link in links:
                if len(self.goods_links) < number_of_goods:
                    self.goods_links.add(self.base_link + link.get_attribute(tag_href))
                else:
                    break
            if len(self.goods_links) < number_of_goods and self.page.is_visible(selector_next_page):
                next_link = self.base_link + self.page.query_selector(class_next_page).get_attribute(tag_href)
                self.page.goto(next_link)
                self._get_goods_links(number_of_goods)

    def find_all_goods(self, keyword: str, number_of_goods: Union[Literal['max'], int] = 10) -> None:
        """Поиск всех ссылок на товары по ключевому слову
        version = 0.1
        """
        empty_selector = """
      Простите, по вашему запросу товаров сейчас нет.
    """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
            context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                     '(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
            self.page = context.new_page()
            self.page.goto(self.base_link)  # открытие ссылки сайта
            self.page.click("#reload-button")
            time.sleep(1)  # задержка для симуляции человеческого поведения
            self.page.get_by_placeholder("Искать на Ozon").type(keyword, delay=.3)  # задержка в печати
            self.page.query_selector('button[aria-label="Поиск"]').click()
            try:  # проверка, что по запросу ничего не найдено
                self.page.wait_for_selector(f'text="{empty_selector}"', timeout=3_000)
            except TimeoutError:  # если по запросу найдены товары
                self._get_goods_links(number_of_goods)
            finally:
                browser.close()
