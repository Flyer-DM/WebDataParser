import flet as ft
from data_export import ExportData
from parsers import PARSERS
from app_utils.styles import MAIN_BTN_STYLE, SCND_BTN_WIDHT
from app_utils.styles import add_object, add_snack_bar


def search_product(e, site_name):
    page: ft.Page = e.page
    page.window.width = 500
    page.window.height = 600
    page.window.center()

    available_exporters = tuple(ExportData.exporters.keys())
    txt = available_exporters[0]

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
        controls=[product_name, product_amount, file_ext, export_file, export_folder, btn_select_folder,
                  btn_start_search],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
