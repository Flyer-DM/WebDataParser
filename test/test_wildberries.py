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

    def test_one_page(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword, 1)
        self.assertEqual(1, len(self.wb.pages_links))
        self.assertNotEqual(0, len(self.wb.goods_links))

    def test_ten_goods(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword, 1)
        self.wb.goods_links = self.wb.goods_links[:10]
        self.assertIsNotNone(self.wb.describe_all_goods())

    def test_empty_page(self):
        time.sleep(1)
        self.wb.find_all_goods(self.error_keyword, 1)
        self.assertEqual(0, len(self.wb.pages_links))

    def test_two_pages(self):
        time.sleep(1)
        self.wb.find_all_goods(self.keyword, 2)
        self.assertEqual(2, len(self.wb.pages_links))
        self.assertNotEqual([], self.wb.goods_links)

    def test_one_product(self):
        time.sleep(1)
        self.__test_product("https://www.wildberries.ru/catalog/228691002/detail.aspx")

    def test_second_product(self):
        time.sleep(1)
        self.__test_product("https://www.wildberries.ru/catalog/200178063/detail.aspx")


if __name__ == "__main__":
    unittest.main()
