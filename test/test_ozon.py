import time
import unittest
from parsers import Ozon
from getuseragent import UserAgent
from playwright.sync_api import sync_playwright
from helpers.parsers_helpers import LAUNCH_ARGS


class TestWildberries(unittest.TestCase):

    def setUp(self):
        self.ozon = Ozon()
        self.keyword = "гантели разборные"
        self.error_keyword = "blahblahblah"

    def __test_product(self, link):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=LAUNCH_ARGS)
            context = browser.new_context(user_agent=UserAgent("chrome+firefox").Random())
            self.ozon.page = context.new_page()
            self.ozon._get_good_descr(link)
            browser.close()

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

    def test_one_product(self):
        time.sleep(1)
        self.__test_product('https://www.ozon.ru/product/ganteli-razbornye-nabor-2-ganteli-po-20-kg-shtanga'
                            '-tsement-plastik-metal-obshchiy-ves-40kg-259855059/?__rr=1&advert'
                            '=502zKeKFvgJ7CKGWutSLxYaIXVbUhP1b7fbj5Mq-mqUN'
                            '-jsnmkWXUPoFPL7osUC3zE7rvGb9zKgRHyUiv58TMuCPfO9wgnhVo11OUL7ulJRFDThe9M2WzJQhDov3Fua'
                            '49GtwO6I-7xVJqx8lLe2IrEBQ8iuMw4KFQNxoejkIMLFb9fCLx0joZOTnvtsVVJKzMUkQ6gsZANHVByhWb-'
                            'n6WhSYKgPZjWOtZ_ykPblSK0mgBfVYbf23RbV0dR6rcWXtFXcTgUV68Q2coMd9ybF1ExhhiMmfNhGK6S3l1'
                            'f1wpeS1bVwfySYNcYSve1YoN2E5RJgn2vtJKy55z1WPd0YW8esEzhL8KX8GqCXrwlPuw42PGNaATcBBwf6T'
                            'Ne05SpWg&avtc=1&avte=2&avts=1722161757&keywords=гантели+разборные')


if __name__ == "__main__":
    unittest.main()
