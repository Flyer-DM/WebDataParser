import re
import time
from typing import Optional
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from tqdm import tqdm
from helpers.parsers_helpers import open_scroller

from parsers_dataclasses import WildberriesProduct


class Wildberries:

    __version__ = "0.1.1"

    def __init__(self):
        """version = 0.1.1"""
        self.page = None
        self.pages_links: list[str | Optional[int]] = []
        self.goods_links: list[str] = []
        self.parsing_result: list[dict] = []
        self.base_link = "https://www.wildberries.ru/"
        self.scroller = open_scroller()
        self.PAGE_SCROLL_SIZE = 15

    def _get_goods_links(self, page_link: str) -> list[str]:
        """Нахождение всех ссылок на товары на всей странице
        version = 0.1
        """
        self.page.goto(page_link)
        self.page.wait_for_selector(".catalog-page")
        for _ in range(self.PAGE_SCROLL_SIZE):  # прокрутка до конца страницы
            self.page.evaluate(self.scroller)
        time.sleep(1)  # остановка для полной загрузки страницы
        elements = self.page.query_selector_all('div.product-card-list a[draggable="false"]')
        elements = list(map(lambda el: el.get_attribute('href'), elements))
        return elements

    def _get_next_page_link(self, page_link: str) -> None:
        """Получение ссылки на следующую страницу с текущей
        version = 0.1
        """
        self.page.goto(page_link)
        self.page.wait_for_selector(".catalog-page")
        for _ in range(self.PAGE_SCROLL_SIZE):  # прокрутка до конца страницы
            self.page.evaluate(self.scroller)
        try:
            self.page.wait_for_selector('text="Следующая страница"', timeout=3_000)
            element = self.page.get_by_text(text="Следующая страница")
            self.pages_links.append(element.get_attribute('href'))
        except TimeoutError:  # если страницы для поиска закончились
            self.pages_links.append(0)

    def _get_all_pages_links(self, number_of_pages):
        """Добавление в список всех ссылок на страницы
        version = 0.1
        """
        self.pages_links.append(self.page.url)  # ссылка на первую страницу каталога
        if number_of_pages > 1:
            for i in range(number_of_pages - 1):
                page_link = self.pages_links[i]
                if isinstance(page_link, str):
                    self._get_next_page_link(page_link)  # получение ссылки на следующую страницу
                else:  # если страницы для поиска закончились (меньше заданного кол-ва)
                    self.pages_links.pop()  # удаление нуля в конце
                    break

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
        version = 0.1.1
        """
        title_selector = 'h1[class="product-page__title"]'
        self.page.goto(page_link)
        self.page.wait_for_selector(title_selector)
        title = self.page.query_selector(title_selector)
        product = WildberriesProduct(page_link, title)
        product.seller = self.page.query_selector('a[class="product-page__header-brand j-wba-card-item '
                                                  'j-wba-card-item-show j-wba-card-item-observe"]')
        product.article = self.page.query_selector('span[id="productNmId"]')
        product.price_wb_wallet = self.page.query_selector('span[class="price-block__wallet-price"]')
        product.price = self.page.query_selector('ins[class="price-block__final-price wallet"]')
        product.full_price = self.page.query_selector('del[class="price-block__old-price"]')
        product.score = self.page.query_selector('span[class="product-review__rating '
                                                 'address-rate-mini address-rate-mini--sm"]')
        product.reviews = self.page.query_selector('span[class="product-review__count-review '
                                                   'j-wba-card-item-show j-wba-card-item-observe"]')
        product.category = self.page.query_selector('div[class="breadcrumbs__container"]')
        producers_goods_data_link = "href{:selectedNomenclature^brandAndSubjectUrl}{on $analitic.proceedAndSave 'IBC'}"
        product.producers_goods = self.page.query_selector(f'a[data-link="{producers_goods_data_link}"]')
        product.same_category = self.page.query_selector('a[class="product-page__link j-wba-card-item '
                                                         'j-wba-card-item-show j-wba-card-item-observe"]')
        product.refund = self.page.query_selector('li[class="advantages__item advantages__item--refund"]')
        self.page.hover('.seller-info__more.hide-mobile')  # наведение мышкой на значок подробностей о продавце
        seller_status = self.page.locator('.seller-params__list')
        seller_lvl = sold_goods = on_market = None
        if seller_status is not None:
            seller_status = seller_status.inner_text()
            seller_lvl, sold_goods, on_market = self.__parse_seller_descr(seller_status)
        product.seller_lvl, product.sold_goods, product.on_market = seller_lvl, sold_goods, on_market
        self.page.click('text="Все характеристики и описание"')
        self.page.wait_for_timeout(50)
        product.description = self.page.query_selector('p[class="option__text"]')
        # создание итогового словаря по товару
        self.parsing_result.append(product.dict())

    def find_all_goods(self, keyword: str, number_of_pages: int) -> None:
        """Поиск всех ссылок на товары по ключевому слову
        version = 0.1.1
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            self.page = context.new_page()
            self.page.goto(self.base_link, timeout=1000, wait_until="load")  # открытие ссылки сайта
            self.page.wait_for_selector('input[id="searchInput"]')  # поиск поля input
            search_input = self.page.locator('input[id="searchInput"]')  # помещение курсора в input
            search_input.fill(keyword, timeout=300)
            search_input.press('Enter')  # запуск процесса поиска
            try:  # проверка, что по запросу ничего не найдено
                self.page.wait_for_selector('text="Попробуйте поискать по-другому или сократить запрос"', timeout=1_000)
            except TimeoutError:  # если по запросу найдены товары
                self._get_all_pages_links(number_of_pages)  # получение ссылок на все страницы по поиску
                for link in self.pages_links:
                    self.goods_links.extend(self._get_goods_links(link))
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
