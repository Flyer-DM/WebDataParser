import re
from typing import Optional, Union
from dataclasses import dataclass, field, asdict
from playwright.sync_api._generated import ElementHandle


@dataclass(slots=True)
class WildberriesProduct:

    __version__ = "0.3.1"
    __base_link = "https://www.wildberries.ru"

    page_link: str = field(init=True)  # ссылка на страницу товара
    title: str = field(init=True)  # название товара
    seller: str = field(init=False)  # название продавца
    seller_score: Optional[float] = field(init=False, default=None)  # средняя оценка продавца
    brand: Optional[str] = field(init=False)  # бренд товара
    article: int = field(init=False)  # артикул товара
    price_wb_wallet: Optional[int] = field(init=False)  # цена товара с wb кошельком
    price: Optional[int] = field(init=False)  # цена товара со скидкой
    old_price: Optional[int] = field(init=False)  # старая цена товара
    score: Optional[float] = field(init=False)  # средняя оценка товара
    reviews: Optional[int] = field(init=False)  # количество отзывов на товар
    category: Optional[str] = field(init=False)  # категория товара
    seller_goods: Optional[str] = field(init=False)  # ссылка на товары бренда
    same_category: str = field(init=False)  # ссылка на товары той же категории
    refund: Optional[str] = field(init=False)  # возможность возврата
    seller_lvl: Optional[str] = field(init=False, default=None)  # уровень продавца
    sold_goods: Optional[int] = field(init=False, default=None)  # сколько товаров было продано продавцом
    on_market: Optional[str] = field(init=False, default=None)  # сколько продавец на рынке
    description: str = field(init=False)  # описание товара

    def dict(self):
        """version = 0.2"""
        return {k: v for k, v in asdict(self).items()}

    def __setattr__(self, key: str, value: Optional[Union[str, ElementHandle]]):
        """version = 0.5"""
        if key in ("title", "refund", "description"):
            value = self.__inner_text(value)
        elif key == "seller":
            value = value if (value := self.__inner_text(value)) else "WILDBERRIES"
        elif key in ("price_wb_wallet", "price", "old_price", "reviews"):
            value = self.__format_number(self.__inner_text(value))
        elif key in ("seller_goods", "same_category"):
            value = self.__href(value)
        elif key == "article":
            value = int(self.__inner_text(value))
        elif key == "brand":
            value = value if (value := self.__inner_text(value.query_selector('a'))) != '' else None
        elif key == "score":
            value = re.search(r'[\d\s\.]+(?=\n)', value) if (value := self.__inner_text(value)) else None
            value = float(value[0]) if value else None
        elif key == "seller_score":
            value = float(value) if (value := self.__inner_text(value)) else None
        elif key == "category":
            value = self.__inner_text(value).replace('\n', '/')
        super(WildberriesProduct, self).__setattr__(key, value)

    @staticmethod
    def __inner_text(value: Optional[ElementHandle]) -> Optional[str]:
        """Получение текстового содержимого тега
        version = 0.2.1
        """
        return value.inner_text() if value else None

    @staticmethod
    def __href(value: Optional[ElementHandle]) -> Optional[str]:
        """Получение строковых ссылок из атрибутов, содержащих их
        version = 0.2
        """
        value = value.get_attribute('href') if value else None
        return (WildberriesProduct.__base_link + value) if value else None

    @staticmethod
    def __format_number(number: str) -> Optional[int]:
        """Форматирование целочисленных атрибутов с присутствием нечисловых символов
        version = 0.3
        """
        return int(number) if (number := re.sub(r'[^\d]', '', number) if number else None) else None

    def parse_seller_descr(self, seller_data: Optional[ElementHandle]) -> None:
        """Парсинг доп информации о поставщике - уровень поставщика, сколько товаров продано, сколько времени на рынке
        version = 0.1
        """
        if seller_data:
            level = re.search(r".+(?=  У)", seller_data := seller_data.inner_text().replace("\n", " "))
            self.seller_lvl = level[0] if level else None
            self.sold_goods = int(re.sub(r'[^\d]', '', re.search(r"(?:(?<=  )|(?<=^))[\d\s]+(?=  Т)", seller_data)[0]))
            self.on_market = re.search(r"(?<=[он]  ).+(?=  Н)", seller_data)[0]
