import time
import unittest
from parsers import Ozon


class TestWildberries(unittest.TestCase):

    def setUp(self):
        self.ozon = Ozon()
        self.keyword = "гантели разборные"
        self.error_keyword = "blahblahblah"

    def test_not_implicit_goods(self):
        time.sleep(1)
        self.ozon.find_all_goods(self.keyword)
        self.assertEqual(10, len(self.ozon.goods_links))

    def test_not_explicit_goods(self):
        time.sleep(1)
        self.ozon.find_all_goods(self.keyword, 60)
        self.assertEqual(60, len(self.ozon.goods_links))

    def test_empty_page(self):
        time.sleep(1)
        self.ozon.find_all_goods(self.error_keyword)
        self.assertEqual(0, len(self.ozon.goods_links))


if __name__ == "__main__":
    unittest.main()
