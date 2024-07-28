import pprint
import time
import unittest
from parsers import Wildberries
from playwright.sync_api import sync_playwright


class TestWildberries(unittest.TestCase):

    def setUp(self):
        self.wb = Wildberries()
        self.keyword = "гантели разборные"
        self.error_keyword = "Текст, не имеющий смысла: blahblahblah"

    def __test_product(self, link):
        pp = pprint.PrettyPrinter(depth=4)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            self.wb.page = context.new_page()
            self.wb._get_good_descr(link)
            self.assertNotEqual([], self.wb.parsing_result)
            pp.pprint(self.wb.parsing_result[0])
            browser.close()

    def test_one_good(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword, 1)
        self.assertEqual(1, len(self.wb.goods_links))

    def test_many_goods(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword, 150)
        self.assertEqual(150, len(self.wb.goods_links))

    def test_empty_page(self):
        time.sleep(1)
        self.wb.find_all_goods(self.error_keyword)
        self.assertEqual(0, len(self.wb.goods_links))

    def test_max_goods(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword, 'max')
        self.assertNotEqual([], self.wb.goods_links)

    def test_overmuch_goods(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword, 1500)
        self.assertNotEqual([], self.wb.goods_links)

    def test_describe_all_goods(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword)
        self.assertEqual(10, len(self.wb.describe_all_goods()))

    def test_first_product(self):
        time.sleep(1)
        self.__test_product("https://www.wildberries.ru/catalog/228691002/detail.aspx")

    def test_second_product(self):
        time.sleep(1)
        self.__test_product("https://www.wildberries.ru/catalog/200178063/detail.aspx")

    def test_third_product(self):
        time.sleep(1)
        self.__test_product("https://www.wildberries.ru/catalog/135548188/detail.aspx")

    def test_fourth_product(self):
        time.sleep(1)
        self.__test_product("https://www.wildberries.ru/catalog/187291954/detail.aspx")


if __name__ == "__main__":
    unittest.main()
