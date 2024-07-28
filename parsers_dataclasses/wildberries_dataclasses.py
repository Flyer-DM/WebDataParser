import re
from typing import Optional, Union
from dataclasses import dataclass, field, asdict
from playwright.sync_api._generated import ElementHandle


@dataclass
class WildberriesProduct:

    __version__ = "0.1.2"
    __base_link = "https://www.wildberries.ru"

    page_link: str = field(init=True)  # ссылка на страницу товара
    title: str = field(init=True)  # название товара
    seller: str = field(init=False)  # название продавца
    article: int = field(init=False)  # артикул товара
    price_wb_wallet: int = field(init=False)  # цена товара с wb кошельком
    price: int = field(init=False)  # цена товара со скидкой
    full_price: int = field(init=False)  # начальная цена товара
    score: Optional[float] = field(init=False)  # средняя оценка товара
    reviews: Optional[int] = field(init=False)  # количество отзывов
    category: str = field(init=False)  # категория товара
    producers_goods: str = field(init=False)  # ссылка на товары производителя
    same_category: str = field(init=False)  # ссылка на товары той же категории
    refund: Optional[str] = field(init=False)  # возможность возврата
    seller_lvl: Optional[str] = field(init=False, default=None)  # уровень продавца
    sold_goods: Optional[str] = field(init=False, default=None)  # сколько товаров было продано продавцом
    on_market: Optional[str] = field(init=False, default=None)  # сколько продавец на рынке
    description: str = field(init=False)  # описание товара

    def dict(self):
        """version = 0.2"""
        return {k: v for k, v in asdict(self).items()}

    def __setattr__(self, key: str, value: Optional[Union[str, ElementHandle]]):
        """version = 0.2"""
        if key in ("seller", "title", "refund", "description"):
            value = self.__inner_text(value)
        elif key in ("price_wb_wallet", "price", "full_price", "reviews"):
            value = self.__format_number(self.__inner_text(value))
        elif key in ("producers_goods", "same_category"):
            value = self.__href(value)
        elif key == "article":
            value = int(self.__inner_text(value))
        elif key == "score":
            value = self.__inner_text(value)
            value = re.search(r'[\d\s\.]+(?=\n)', value) if value is not None else None
            value = float(value.group(0)) if value is not None else None
        elif key == "category":
            value = self.__inner_text(value).replace('\n', '/')
        elif key == "sold_goods":
            value = self.__format_number(value)
        super().__setattr__(key, value)

    @staticmethod
    def __inner_text(value: Optional[ElementHandle]) -> Optional[str]:
        """Получение текстового содержимого тега
        version = 0.1.1
        """
        return value.inner_text() if value is not None else None

    @staticmethod
    def __href(value: Optional[ElementHandle]) -> str:
        """Получение строковых ссылок из атрибутов, содержащих их
        version = 0.1.1
        """
        return WildberriesProduct.__base_link + value.get_attribute('href')

    @staticmethod
    def __format_number(number: str) -> Optional[int]:
        """Форматирование целочисленных атрибутов с присутствием нечисловых символов
        version = 0.2
        """
        return int(re.sub(r'[^\d]', '', number)) if number is not None else None
