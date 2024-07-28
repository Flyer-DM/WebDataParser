import re
import time
import random
from typing import Union, Literal, Optional
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from getuseragent import UserAgent
from helpers.parsers_helpers import *
from tqdm import tqdm


class Ozon:

    __version__ = "0.2"

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

    def _get_good_descr(self, page_link: str) -> None:
        """Сбор информации о товаре на его странице
        version = 0.1a
        """
        href = 'href'
        seller_selector = 'div[data-widget="webCurrentSeller"]'
        self.page.goto(page_link)
        self.page.click("#reload-button")
        self.page.wait_for_selector('div[data-widget="webProductHeading"]')
        print(f'{page_link=}')
        title = self.page.query_selector('div[data-widget="webProductHeading"]').query_selector('h1').inner_text()
        print(f'{title=}')
        article = self.page.query_selector('button[data-widget="webDetailSKU"]').query_selector('div').inner_text()
        article = re.sub(r'[^\d]', '', article)
        print(f'{article=}')
        category = self.page.query_selector('div[data-widget="breadCrumbs"]').inner_text().replace('\n', '/')
        print(f'{category=}')
        prices = self.page.query_selector('div[data-widget="webPrice"]').query_selector_all('span')
        prices = list(map(lambda p: p.inner_text(), prices))
        ozon_card_price, price, old_price = prices[1], prices[3], prices[4]
        ozon_card_price = int(re.sub(r'[^\d]', '', re.sub(r'\\u2009', '', ozon_card_price)))
        print(f'{ozon_card_price=}')
        price = int(re.sub(r'[^\d]', '', re.sub(r'\\u2009', '', price)))
        print(f'{price=}')
        old_price = int(re.sub(r'[^\d]', '', re.sub(r'\\u2009', '', old_price)))
        print(f'{old_price=}')
        score_data = self.page.query_selector('div[data-widget="webSingleProductScore"]').inner_text()
        score = float(re.search(r'.+(?= •)', score_data).group(0))
        print(f'{score=}')
        reviews = int(re.search(r'(?<=• ).+(?= )', score_data).group(0).replace(' ', ''))
        print(f'{reviews=}')
        while not self.page.is_visible(seller_selector):
            self.page.evaluate(self.scroller)
        seller_data = self.page.query_selector(seller_selector).query_selector_all('a')
        seller = seller_data[1].inner_text()
        print(f'{seller=}')
        seller_href = seller_data[0].get_attribute(href)
        print(f'{seller_href=}')
        refund = self.page.query_selector(seller_selector).query_selector_all('li')[-1].inner_text()
        print(f'{refund=}')
        seller_data = self.page.query_selector('div[data-widget="webDescription"]').inner_text()
        seller_data = re.sub(r' Показать полностью$', '', re.sub(r'^Описание ', '', seller_data.replace('\n', ' ')))
        print(f'{seller_data=}')

    def find_all_goods(self, keyword: str, number_of_goods: Union[Literal['max'], int] = 10) -> None:
        """Поиск всех ссылок на товары по ключевому слову
        version = 0.1.1
        """
        empty_selector = """
      Простите, по вашему запросу товаров сейчас нет.
    """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=LAUNCH_ARGS)
            context = browser.new_context(user_agent=UserAgent("chrome+firefox").Random())
            self.page = context.new_page()
            self.page.goto(self.base_link)  # открытие ссылки сайта
            time.sleep(random.uniform(.1, 3))
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
