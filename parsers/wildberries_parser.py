import re
import time
import random
from tqdm import tqdm
from typing import Optional, Union, Literal
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from helpers.parsers_helpers import open_scroller
from getuseragent import UserAgent

from parsers_dataclasses import WildberriesProduct


class Wildberries:

    __version__ = "0.1.2"

    def __init__(self):
        """version = 0.2"""
        self.page = None
        self.goods_links: set[str] = set()
        self.parsing_result: list[dict] = []
        self.base_link = "https://www.wildberries.ru"
        self.scroller = open_scroller()

    def _get_goods_links(self, number_of_goods: Union[Literal['max'], int] = 10) -> None:
        """Сбор всех ссылок на товары. Либо собирается максимальное количество товаров, либо явно
        указанное количество (по умолчанию=10).
        version = 0.2
        """
        tag_href = 'href'
        href_next_page = "Следующая страница"
        selector_next_page = f':text("{href_next_page}")'
        self.page.wait_for_selector('.catalog-page')
        while not self.page.is_visible('.custom-slider__list'):  # пока не видно блок с рекомендуемыми товарами
            self.page.evaluate(self.scroller)  # прокрутка до конца страницы
        links = self.page.query_selector_all('div.product-card-list a[draggable="false"]')
        links = set(map(lambda link: link.get_attribute(tag_href), links))
        if number_of_goods == 'max':
            self.goods_links.update(links)
            if self.page.is_visible(selector_next_page):
                self.page.goto(self.page.get_by_text(text=href_next_page).get_attribute(tag_href))
                self._get_goods_links(number_of_goods)
        else:
            for link in links:
                if len(self.goods_links) < number_of_goods:
                    self.goods_links.add(link)
                else:
                    break
            if len(self.goods_links) < number_of_goods and self.page.is_visible(selector_next_page):
                self.page.goto(self.page.get_by_text(text=href_next_page).get_attribute(tag_href))
                self._get_goods_links(number_of_goods)

    @staticmethod
    def __parse_seller_descr(descr: str) -> tuple:
        """Парсинг доп информации о поставщике - уровень поставщика, сколько товаров продано, сколько времени на рынке
        version = 0.1
        """
        descr = descr.replace("\n", " ")
        level = re.search(r".+(?=  У)", descr)
        level = level.group(0) if level else None
        sold_goods = re.search(r"(?:(?<=  )|(?<=^))[\d\s]+(?=  Т)", descr).group(0)
        on_market = re.search(r"(?<=[он]  ).+(?=  Н)", descr).group(0)
        return level, sold_goods, on_market

    def _get_good_descr(self, page_link: str) -> None:
        """Сбор информации о товаре на его странице
        version = 0.2
        """
        title_selector = 'h1[class="product-page__title"]'
        seler_info_div = '.seller-info__more.hide-mobile'
        self.page.goto(page_link)
        self.page.wait_for_selector(title_selector)
        title = self.page.query_selector(title_selector)
        product = WildberriesProduct(page_link, title)
        product.seller = self.page.query_selector('a[data-name-for-wba="Item_Seller_Info_GoToShop"]')
        product.brand = self.page.query_selector('div[class="product-page__header"]')
        product.article = self.page.query_selector('span[id="productNmId"]')
        product.price_wb_wallet = self.page.query_selector('span[class="price-block__wallet-price"]')
        product.price = self.page.query_selector('ins[class="price-block__final-price wallet"]')
        product.old_price = self.page.query_selector('del[class="price-block__old-price"]')
        product.score = self.page.query_selector('div[class="product-page__common-info"]')
        product.reviews = self.page.query_selector('span[class="product-review__count-review '
                                                   'j-wba-card-item-show j-wba-card-item-observe"]')
        product.category = self.page.query_selector('div[class="breadcrumbs__container"]')
        seller_goods_data_link = "href{:selectedNomenclature^brandAndSubjectUrl}{on $analitic.proceedAndSave 'IBC'}"
        product.seller_goods = self.page.query_selector(f'a[data-link="{seller_goods_data_link}"]')
        product.same_category = self.page.query_selector('a[class="product-page__link j-wba-card-item '
                                                         'j-wba-card-item-show j-wba-card-item-observe"]')
        product.refund = self.page.query_selector('li[class="advantages__item advantages__item--refund"]')
        time.sleep(random.uniform(.3, .6))
        if self.page.is_visible(seler_info_div):  # проверяем, что есть блок с описанием продавца
            self.page.hover(seler_info_div)  # наведение мышкой на значок подробностей о продавце
            seller_status = self.page.locator('.seller-params__list').inner_text()
            product.seller_score = self.page.query_selector('span[class="address-rate-mini"]')
            product.seller_lvl, product.sold_goods, product.on_market = self.__parse_seller_descr(seller_status)
        self.page.click('text="Все характеристики и описание"')
        self.page.wait_for_timeout(random.randint(150, 400))  # ждём, когда прогрузится открытый блок описания
        product.description = self.page.query_selector('p[class="option__text"]')
        self.parsing_result.append(product.dict())  # создание итогового словаря по товару

    def find_all_goods(self, keyword: str, number_of_goods: Union[Literal['max'], int] = 10) -> None:
        """Поиск всех ссылок на товары по ключевому слову
        version = 0.1.2
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
            context = browser.new_context(user_agent=UserAgent().Random())
            self.page = context.new_page()
            self.page.goto(self.base_link)
            time.sleep(random.uniform(1, 2))
            input_field = self.page.get_by_placeholder("Найти на Wildberries").first
            input_field.type(keyword, delay=random.uniform(.1, .5))
            input_field.press(key='Enter', delay=random.randint(100, 500))  # запуск процесса поиска
            try:  # проверка, что по запросу ничего не найдено
                time.sleep(random.uniform(1, 2))  # задержка при загрузке страницы
                self.page.wait_for_selector('text="Попробуйте поискать по-другому или сократить запрос"', timeout=1_000)
            except TimeoutError:  # если по запросу найдены товары
                self._get_goods_links(number_of_goods)  # получение ссылок на все страницы по поиску
            finally:
                browser.close()

    def describe_all_goods(self) -> Optional[list[dict]]:
        """Создание итогового датасета характеристик всех найденных товаров
        version = 0.1
        """
        if len(self.goods_links):  # проверка, что ссылки на товары были найдены
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context()
                self.page = context.new_page()
                for link in tqdm(self.goods_links, ascii=True):  # сбор данных всех товаров
                    self._get_good_descr(link)
                browser.close()
            return self.parsing_result
        return None
