import re
import time
from typing import Optional
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from helpers.parsers_helpers import open_scroller
from tqdm import tqdm


class Wildberries:

    __version__ = "0.1.1"

    def __init__(self):
        """version = 0.2"""
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
    def __format_price(price: str) -> str:
        """Форматирование цены товара
        version = 0.1
        """
        price = price.encode('ascii', errors='ignore')
        return "{0:,}".format(int(price)).replace(",", " ")

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
        version = 0.1
        """
        title_selector = 'h1[class="product-page__title"]'
        self.page.goto(page_link)
        self.page.wait_for_selector(title_selector)
        title = self.page.query_selector(title_selector)
        seller = self.page.query_selector('a[class="product-page__header-brand j-wba-card-item '
                                          'j-wba-card-item-show j-wba-card-item-observe"]')
        article = self.page.query_selector('span[id="productNmId"]')
        price_wb_wallet = self.page.query_selector('span[class="price-block__wallet-price"]')
        price = self.page.query_selector('ins[class="price-block__final-price wallet"]')
        full_price = self.page.query_selector('del[class="price-block__old-price"]')
        score = self.page.query_selector('span[class="product-review__rating '
                                         'address-rate-mini address-rate-mini--sm"]')
        reviews = self.page.query_selector('span[class="product-review__count-review '
                                           'j-wba-card-item-show j-wba-card-item-observe"]')
        category = self.page.query_selector('div[class="breadcrumbs__container"]')
        producers_goods_data_link = "href{:selectedNomenclature^brandAndSubjectUrl}{on $analitic.proceedAndSave 'IBC'}"
        producers_goods = self.page.query_selector(f'a[data-link="{producers_goods_data_link}"]')
        if producers_goods is not None:
            producers_goods = self.base_link[:-1] + producers_goods.get_attribute('href')
        same_category = self.page.query_selector('a[class="product-page__link j-wba-card-item '
                                                 'j-wba-card-item-show j-wba-card-item-observe"]')
        if same_category is not None:
            same_category = self.base_link[:-1] + same_category.get_attribute('href')
        refund = self.page.query_selector('li[class="advantages__item advantages__item--refund"]')
        self.page.hover('.seller-info__more.hide-mobile')  # наведение мышкой на значок подробностей о продавце
        seller_status = self.page.locator('.seller-params__list')
        seller_lvl = sold_goods = on_market = None
        if seller_status is not None:
            seller_status = seller_status.inner_text()
            seller_lvl, sold_goods, on_market = self.__parse_seller_descr(seller_status)
        self.page.click('text="Все характеристики и описание"')
        self.page.wait_for_timeout(50)
        description = self.page.query_selector('p[class="option__text"]')
        # создание итогового словаря по товару
        self.parsing_result.append({
            "Ссылка на товар": page_link,
            "Наименование товара": title.inner_text() if title is not None else None,
            "Продавец": seller.inner_text() if seller is not None else None,
            "Уровень продавца": seller_lvl,
            "Продавец продал товаров": sold_goods,
            "Продавец на рынке": on_market,
            "Артикул": article.inner_text() if article is not None else None,
            "Цена с wb кошельком": self.__format_price(
                price_wb_wallet.inner_text()) if price_wb_wallet is not None else None,
            "Цена": self.__format_price(price.inner_text()) if price is not None else None,
            "Старая цена": self.__format_price(full_price.inner_text()) if full_price is not None else None,
            "Средняя оценка": score.inner_text() if score is not None else None,
            "Количество отзывов": reviews.inner_text() if reviews is not None else None,
            "Категория товара": category.inner_text().replace("\n", "/") if category is not None else None,
            "Товары производителя": producers_goods,
            "Товары той же категории": same_category,
            "Возврат товара": refund.inner_text() if refund is not None else None,
            "Описание товара": description.inner_text() if description is not None else None
        })

    def find_all_goods(self, keyword: str, number_of_pages: int) -> None:
        """Поиск всех ссылок на товары по ключевому слову
        version = 0.1.1
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            self.page = context.new_page()
            self.page.goto(self.base_link)  # открытие ссылки сайта
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
