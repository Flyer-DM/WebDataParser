import time
import pprint
import unittest
from parsers import Ozon
from getuseragent import UserAgent
from playwright.sync_api import sync_playwright
from helpers.parsers_helpers import LAUNCH_ARGS


class TestOzon(unittest.TestCase):

    def setUp(self):
        self.ozon = Ozon()
        self.keyword = "гантели разборные"
        self.error_keyword = "blahblahblah"

    def __test_product(self, link):
        pp = pprint.PrettyPrinter(indent=4)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=LAUNCH_ARGS)
            context = browser.new_context(user_agent=UserAgent("chrome+firefox").Random())
            self.ozon.page = context.new_page()
            self.ozon._get_good_descr(link)
            pp.pprint(self.ozon.parsing_result)
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

    def test_many_products(self):
        time.sleep(1)
        self.ozon.find_all_goods(self.keyword, number_of_goods=50)
        pprint.PrettyPrinter(indent=4).pprint(self.ozon.describe_all_goods())
        self.assertNotEqual(0, len(self.ozon.parsing_result))

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

    def test_second_product(self):
        time.sleep(1)
        self.__test_product('https://www.ozon.ru/product/polotentse-dlya-litsa-ruk-lavsan-28x38-sm-raznotsvetnyy-3-sht'
                            '-1640509000/?advert=d5Yq1oat619zv0QWYL_BItEmMqvxJ-zPgjFcPJANGCCqp-'
                            'U573dxV97K59h7QuEMKeuiSwqrkqz89U85-l-u2WINf-3dk73iBUBF3yexrsqeR0EfxpUIuUetNcz-'
                            'dDw3l1utJBVKm4f65Lia-zOMjyHzB2aC09asAINM4jdRVrG0y_KYNQoMwi1Oyt_r_XJj8kwL2lHireJv_'
                            'qFGY6KadRuf77DSwc6nYPadP2HBCuSSCRv8TspHJIK8uD4Ia_'
                            'goIBb2XahOV0cfeTJZufYWD4lUdV1jZYox0cdZWgS-'
                            'rBawGBqIfraDvZHHYPCSyUPSp5vdfkhnS0VwCnia4sGm8uJf6Zbb4Q6UmXZvm7NFlc5fWEQ&avtc=1&avte='
                            '2&avts=1722247095&keywords=%D0%BF%D0%BE%D0%BB%D0%BE%D1%82%D0%B5%D0%BD%D1%86%D0%B0+'
                            '%D0%BA%D1%83%D1%85%D0%BE%D0%BD%D0%BD%D1%8B%D0%B5')

    def test_third_product(self):
        time.sleep(1)
        self.__test_product('https://www.ozon.ru/product/nosovye-platochki-semya-i-komfort-siren-3-sloya-10sht-h3sht-'
                            '1582316998/?asb=JRrLrfQ439zOnGrAbm1QthyYJuEtPs634mnNsJFanP0%253D&asb2=mJsQREIkQwVwMeMk_'
                            'PPzyp8011kE1aUiUPa9inwldBj4K3oc3sDamJ1Q2skC5uS7TPCxD35PJt9rKzhoXz4gIQ&avtc=1&avte=2&avts='
                            '1722249508&keywords=%D0%BE%D0%B4%D0%BD%D0%BE%D1%80%D0%B0%D0%B7%D0%BE%D0%B2%D1%8B%D0%B5+'
                            '%D0%BF%D0%BB%D0%B0%D1%82%D0%BA%D0%B8')

    def test_fourth_product(self):
        time.sleep(1)
        self.__test_product('https://www.ozon.ru/product/floom-bumazhnye-platki-10-sht-1259633693/?asb=%252Bdrc97kz%'
                            '252FCAs6D%252FyyagqoMGYUAQWWjC02N9NT%252Fe4jF4%253D&asb2=S4EEm5UMHgKepW-'
                            'Xo1iva0kdUnG3x99F6Wypb7tU3q0v_tKM0XoQ0WZE9H1Al_iHprtpK5l73PjmHn_yJOBKfw&avtc=2&avte='
                            '1&avts=1722251068&keywords=%D0%BE%D0%B4%D0%BD%D0%BE%D1%80%D0%B0%D0%B7%D0%BE%D0%B2%D1%'
                            '8B%D0%B5+%D0%BF%D0%BB%D0%B0%D1%82%D0%BA%D0%B8')


if __name__ == "__main__":
    unittest.main()
