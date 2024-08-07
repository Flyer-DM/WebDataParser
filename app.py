import flet as ft
from app_utils import MAIN_BTN_STYLE, MAIN_BTN_WIDTH, SCND_BTN_WIDHT, BACK_BTN_STYLE
from app_utils import add_snack_bar
from app_utils import add_object
from data_export import ExportData
from parsers import PARSERS


def main(page: ft.Page):
    page.title = "WebDataParser 0.1dev"
    page.window.width = 500
    page.window.height = 300
    page.window.center()

    header = ft.Text("Сайты для парсинга", size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    btn_wildberries = ft.ElevatedButton("Wildberries",
                                        on_click=go_to_wildberries, style=MAIN_BTN_STYLE, width=MAIN_BTN_WIDTH)
    btn_ozon = ft.ElevatedButton("Ozon",
                                 on_click=go_to_ozon, style=MAIN_BTN_STYLE, width=MAIN_BTN_WIDTH)

    main_container = add_object(header, btn_ozon, btn_wildberries)
    page.add(main_container)


def ozon_page(e):
    def start_search_ozon(e):
        page = e.page
        page.controls.clear()
        page.controls.append(search_product(e, "Ozon"))
        page.update()

    btn_main = ft.ElevatedButton("Назад",
                                 on_click=go_to_main, style=BACK_BTN_STYLE, width=BACK_BTN_STYLE)
    btn_search = ft.ElevatedButton("Поиск товаров по названию",
                                   on_click=start_search_ozon, style=MAIN_BTN_STYLE, width=SCND_BTN_WIDHT)

    return add_object(btn_main, btn_search)


def wildberries_page(e):
    def start_search_wildberries(e):
        page = e.page
        page.controls.clear()
        page.controls.append(search_product(e, "Wildberries"))
        page.update()

    btn_main = ft.ElevatedButton("Назад",
                                 on_click=go_to_main, style=BACK_BTN_STYLE, width=MAIN_BTN_WIDTH)
    btn_search = ft.ElevatedButton("Поиск товаров по названию",
                                   on_click=start_search_wildberries, style=MAIN_BTN_STYLE, width=SCND_BTN_WIDHT)

    return add_object(btn_main, btn_search)


def main_page(e):
    page = e.page
    page.window.width = 500
    page.window.height = 300
    header = ft.Text("Сайты для парсинга", size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    btn_wildberries = ft.ElevatedButton("Wildberries",
                                        on_click=go_to_wildberries, style=MAIN_BTN_STYLE, width=MAIN_BTN_WIDTH)
    btn_ozon = ft.ElevatedButton("Ozon",
                                 on_click=go_to_ozon, style=MAIN_BTN_STYLE, width=MAIN_BTN_WIDTH)
    return add_object(header, btn_ozon, btn_wildberries)


def go_to_main(e):
    page = e.page
    page.controls.clear()
    page.controls.append(main_page(e))
    page.update()


def go_to_ozon(e):
    page = e.page
    page.controls.clear()
    page.controls.append(ozon_page(e))
    page.update()


def go_to_wildberries(e):
    page = e.page
    page.controls.clear()
    page.controls.append(wildberries_page(e))
    page.update()


def search_product(e, site_name):
    page: ft.Page = e.page
    page.window.width = 500
    page.window.height = 600
    page.window.center()

    available_exporters = tuple(ExportData.exporters.keys())
    txt = available_exporters[0]

    btn_main = ft.ElevatedButton("На главную",
                                 on_click=go_to_main, style=BACK_BTN_STYLE, width=BACK_BTN_STYLE)

    product_name = ft.TextField(label="Название товара")
    product_amount = ft.TextField(label="Количество товаров для поиска", value='10')
    file_ext = ft.Dropdown(
        label=f"Расширение для экспорта данных ({txt} по умолчанию)",
        value=txt,
        options=[ft.dropdown.Option(key) for key in available_exporters]
    )
    export_file = ft.TextField(label="Имя файла для сохранения (Дата/Время по умолчанию)")
    export_folder = ft.TextField(label="Папка для экспорта данных (\"Загрузки\" по умолчанию)",
                                 read_only=True)

    def parse_products(e):
        page: ft.Page = e.page
        parser = PARSERS[site_name]
        if not (product := product_name.value):
            add_snack_bar(page, "Введите наименование товара", ft.colors.RED)
        elif (not (amount := product_amount.value) == 'max') and (not amount.isdigit()):
            add_snack_bar(page, "Количество товаров должно быть целым числом или 'max'", ft.colors.RED)
        else:
            btn_start_search.disabled, btn_select_folder.disabled = True, True
            page.add(pb := add_object(ft.ProgressBar(width=200, color="purple", bgcolor="#eeeeee")))
            parser.find_all_goods(product, int(amount))
            page.remove(pb)
            links = len(parser.goods_links)
            to_wait = links * parser.PARSER_ONE_PRODUCT_MEAN_TIME
            add_snack_bar(page, f"Найдено товаров: {links} по запросу \"{product}\"", ft.colors.BLUE)
            page.add(text_field := add_object(ft.Text(f"Примерное время ожидания: {to_wait} секунд")))
            page.add(pb := add_object(ft.ProgressBar(width=200, color="purple", bgcolor="#eeeeee")))
            parsing_result = parser.describe_all_goods()
            page.remove(text_field)
            exporter = ExportData(file_ext.value, parsing_result, site_name,
                                  filename if (filename := export_file.value) else None,
                                  path if (path := export_folder.value) else None)
            exporter.export()
            add_snack_bar(page, f"{len(parser.goods_links)} записей сохранено в папку {exporter.exporter.path}",
                          ft.colors.GREEN)
            page.remove(pb)
            btn_start_search.disabled, btn_select_folder.disabled = False, False
        page.update()

    def save_file_result(e: ft.FilePickerResultEvent):
        export_folder.value = e.path if e.path else None
        export_folder.update()

    save_file_dialog = ft.FilePicker(on_result=save_file_result)
    page.overlay.append(save_file_dialog)
    btn_select_folder = ft.ElevatedButton("Выбрать папку", on_click=lambda _: save_file_dialog.get_directory_path(),
                                          style=MAIN_BTN_STYLE, width=SCND_BTN_WIDHT)
    btn_start_search = ft.ElevatedButton("Начать поиск", on_click=parse_products,
                                         style=MAIN_BTN_STYLE, width=SCND_BTN_WIDHT)
    return ft.Column(
        controls=[btn_main, product_name, product_amount, file_ext, export_file, export_folder, btn_select_folder,
                  btn_start_search],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


if __name__ == '__main__':
    ft.app(target=main)
