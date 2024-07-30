import re
from typing import Optional, Union
from dataclasses import dataclass, field, asdict
from playwright.sync_api._generated import ElementHandle


@dataclass
class OzonProduct:

    __version__ = "0.1.1"
    __base_link = "https://www.ozon.ru"

    page_link: str = field(init=True)  # ссылка на страницу товара
    title: str = field(init=False)  # название товара
    article: int = field(init=False)  # артикул товара
    category: str = field(init=False)  # категория товара
    ozon_card_price: Optional[int] = field(init=False)  # цена с картой озон
    price: int = field(init=False)  # цена без карты озон
    old_price: Optional[int] = field(init=False)  # цена без скидки
    score: Optional[float] = field(init=False)  # средняя оценка товара
    reviews: Optional[int] = field(init=False)  # количество отзывов на товар
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
        super().__setattr__(key, value)
