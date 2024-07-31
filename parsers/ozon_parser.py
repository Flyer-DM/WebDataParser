import time
import random
from typing import Union, Literal, Optional
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from getuseragent import UserAgent
from helpers.parsers_helpers import *
from tqdm import tqdm

from parsers_dataclasses import OzonProduct


class Ozon:

    __version__ = "0.3"

    def __init__(self):
        """version = 0.2"""
        self.page = None
        self.goods_links: set[str] = set()
        self.parsing_result: list[dict] = []
        self.scroller = open_scroller()
        self.base_link = "https://www.ozon.ru"

    def _get_goods_links(self, number_of_goods: Union[Literal['max'], int] = 10) -> None:
        """Сбор всех ссылок на товары. Либо собирается максимальное количество товаров, либо явно
        указанное количество (по умолчанию=10).
        version = 0.1.1
        """
        id_paginator_content = "#paginatorContent"
        tag_href = 'href'
        href_next_page = "Дальше"
        selector_next_page = f':text("{href_next_page}")'
        self.page.wait_for_selector(id_paginator_content)
        all_products = self.page.query_selector(id_paginator_content)
        next_page_link = all_products.evaluate_handle('element => element.nextElementSibling').query_selector('a')
        next_page_link = self.base_link + next_page_link.get_attribute(tag_href)
        links = set(all_products.query_selector_all('.tile-hover-target'))
        if number_of_goods == 'max':
            self.goods_links.update({self.base_link + link.get_attribute(tag_href) for link in links})
            if self.page.is_visible(selector_next_page):
                self.page.goto(next_page_link)
                self._get_goods_links(number_of_goods)
        else:
            for link in links:
                if len(self.goods_links) < number_of_goods:
                    self.goods_links.add(self.base_link + link.get_attribute(tag_href))
                else:
                    break
            if len(self.goods_links) < number_of_goods and self.page.is_visible(selector_next_page):
                self.page.goto(next_page_link)
                self._get_goods_links(number_of_goods)

    def _get_good_descr(self, page_link: str) -> None:
        """Сбор информации о товаре на его странице
        version = 0.2.1
        """
        href = 'href'
        reload_button = "#reload-button"
        seller_selector = 'div[data-widget="webCurrentSeller"]'
        title_selector = 'div[data-widget="webProductHeading"]'
        score_data_selector = 'div[data-widget="webSingleProductScore"]'
        self.page.goto(page_link)
        time.sleep(random.uniform(.5, 2))  # ожидание загрузки страница анти-бот защиты (для первой ссылки в списке)
        if self.page.is_visible(reload_button):
            self.page.click("#reload-button")
        try:  # проверка, что страница не блокируется страницей с ограничением возраста
            self.page.wait_for_selector(title_selector, timeout=5_000)
            product = OzonProduct(page_link)
            product.title = self.page.query_selector(title_selector)
            product.article = self.page.query_selector('button[data-widget="webDetailSKU"]')
            product.category = self.page.query_selector('div[data-widget="breadCrumbs"]')
            prices = self.page.query_selector('div[data-widget="webPrice"]').query_selector_all('span')
            product.parse_prices(prices)
            self.page.wait_for_selector(score_data_selector, timeout=5_000)
            score_data = self.page.query_selector(score_data_selector).inner_text()
            product.parse_score_data(score_data)
            while not self.page.is_visible(seller_selector):
                self.page.evaluate(self.scroller)
            seller_data = self.page.query_selector(seller_selector).query_selector_all('a')
            product.seller = seller_data[1].inner_text()
            product.seller_href = seller_data[0].get_attribute(href)
            product.refund = self.page.query_selector(seller_selector).query_selector_all('li')[-1].inner_text()
            product.description = self.page.query_selector('div[data-widget="webDescription"]')
            self.parsing_result.append(product.dict())
        except TimeoutError:
            pass

    def find_all_goods(self, keyword: str, number_of_goods: Union[Literal['max'], int] = 10) -> None:
        """Поиск всех ссылок на товары по ключевому слову
        version = 0.1.2
        """
        empty_selector = """
      Простите, по вашему запросу товаров сейчас нет.
    """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=LAUNCH_ARGS)
            context = browser.new_context(user_agent=UserAgent("chrome+firefox").Random())
            self.page = context.new_page()
            self.page.goto(self.base_link)  # открытие ссылки сайта
            time.sleep(random.uniform(1, 3))
            self.page.click("#reload-button")
            time.sleep(random.uniform(2, 3))
            self.page.get_by_placeholder("Искать на Ozon").type(keyword, delay=random.uniform(.1, .5))
            self.page.query_selector('button[aria-label="Поиск"]').click(delay=random.randint(100, 500))
            try:  # проверка, что по запросу ничего не найдено
                self.page.wait_for_selector(f'text="{empty_selector}"', timeout=3_000)
            except TimeoutError:  # если по запросу найдены товары
                self._get_goods_links(number_of_goods)
            finally:
                browser.close()

    def describe_all_goods(self) -> Optional[list[dict]]:
        """Создание итогового датасета характеристик всех найденных товаров
        version = 0.1
        """
        if len(self.goods_links):  # проверка, что ссылки на товары были найдены
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=LAUNCH_ARGS)
                context = browser.new_context(user_agent=UserAgent("chrome+firefox").Random())
                self.page = context.new_page()
                for link in tqdm(self.goods_links, ascii=True):  # сбор данных всех товаров
                    time.sleep(random.random())
                    self._get_good_descr(link)
                browser.close()
            return self.parsing_result
        return None
