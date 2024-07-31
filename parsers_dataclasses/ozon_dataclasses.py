import re
from typing import Optional, Union, List, Literal
from dataclasses import dataclass, field, asdict
from playwright.sync_api._generated import ElementHandle


@dataclass(slots=True)
class OzonProduct:

    __version__ = "0.2"
    __base_link = "https://www.ozon.ru"

    page_link: str = field(init=True)  # ссылка на страницу товара
    title: str = field(init=False)  # название товара
    article: int = field(init=False)  # артикул товара
    category: str = field(init=False)  # категория товара
    ozon_card_price: Optional[int] = field(init=False, default=None)  # цена с картой озон
    price: int = field(init=False)  # цена без карты озон
    old_price: Optional[int] = field(init=False, default=None)  # цена без скидки
    score: Optional[float] = field(init=False, default=None)  # средняя оценка товара
    reviews: Optional[int] = field(init=False, default=None)  # количество отзывов на товар
    seller: str = field(init=False)  # продавец товара
    seller_href: str = field(init=False)  # ссылка на другие товары продавца
    refund: str = field(init=False)  # наличие возврата
    description: Optional[str] = field(init=False)  # описание возврата

    def dict(self):
        """version = 0.1"""
        return {k: v for k, v in asdict(self).items()}

    def __setattr__(self, key: str, value: Optional[Union[int, float, str, ElementHandle]]):
        """version = 0.1"""
        if key == 'title':
            value = value.query_selector('h1').inner_text()
        elif key == 'article':
            value = int(re.sub(r'[^\d]', '', value.query_selector('div').inner_text()))
        elif key == 'category':
            value = value.inner_text().replace('\n', '/')
        elif key == 'description':
            value = value.inner_text()
            value = re.sub(r' Показать полностью$', '', re.sub(r'^Описание ', '', value.replace('\n', ' ')))
            value = None if value == 'Показать полностью' else value
        super(OzonProduct, self).__setattr__(key, value)

    def parse_score_data(self, score_data: Union[str, Literal['Нет отзывов']]) -> None:
        """Парсинг средней оценки и количества отзывов
        version = 0.1
        """
        if score_data != 'Нет отзывов':
            if score := re.search(r'.+(?= •)', score_data):  # если есть средняя оценка
                self.score = float(score.group(0))  # есть и средняя оценка и количество отзывов
            self.reviews = int(re.search(r'(?<=• ).+(?= )', score_data).group(0).replace(' ', ''))

    def parse_prices(self, prices: List[ElementHandle]) -> None:
        """Парсинг трёх видов цен из блока с ценами - цена с картой ozon, обычная цена, старая цена
        version = 0.1
        """
        empty, digit, spec_symbol = '', r'[^\d]', r'\\u2009'
        prices = list(map(lambda p: p.inner_text(), prices))
        if len(prices) > 2:
            ozon_card_price, price, old_price = prices[1], prices[3], prices[4]
            ozon_card_price = int(re.sub(digit, empty, re.sub(spec_symbol, empty, ozon_card_price)))
            price = int(re.sub(digit, empty, re.sub(spec_symbol, empty, price)))
            if re.search(r'\d+', old_price):
                old_price = int(re.sub(digit, empty, re.sub(spec_symbol, empty, old_price)))  # все возможные цены
                self.ozon_card_price, self.price, self.old_price = ozon_card_price, price, old_price
            self.ozon_card_price, self.price = ozon_card_price, price  # цены, кроме старой
        elif len(prices) == 1:
            self.price = int(re.sub(digit, empty, re.sub(spec_symbol, empty, prices[0])))  # только цена без карты
        else:
            price = int(re.sub(digit, empty, re.sub(spec_symbol, empty, prices[0])))
            old_price = int(re.sub(digit, empty, re.sub(spec_symbol, empty, prices[1])))
            self.price, self.old_price = price, old_price  # цены, кроме цены с картой
