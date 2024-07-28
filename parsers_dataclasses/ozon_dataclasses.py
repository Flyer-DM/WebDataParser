from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class OzonProduct:

    __version__ = "0.1a"
    __base_link = "https://www.ozon.ru"

    page_link: str = field(init=True)  # ссылка на страницу товара
    title: Optional[str] = field(init=False)  # название товара
    article: Optional[int] = field(init=False)  # артикул товара
    category: Optional[str] = field(init=False)  # категория товара
    ozon_card_price: Optional[int] = field(init=False)  # цена с картой озон
    price: Optional[int] = field(init=False)  # цена без карты озон
    old_price: Optional[int] = field(init=False)  # цена без скидки
    score_data: Optional[float] = field(init=False)  # средняя оценка товара
    reviews: Optional[int] = field(init=False)  # количество отзывов на товар
    seller: Optional[str] = field(init=False)  # продавец товара
    seller_href: Optional[str] = field(init=False)  # ссылка на другие товары продавца
    refund: Optional[str] = field(init=False)  # наличие возврата
    description: Optional[str] = field(init=False)  # описание возврата

    def dict(self):
        """version = 0.1"""
        return {k: v for k, v in asdict(self).items()}
