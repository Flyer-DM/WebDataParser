import flet as ft
from app_utils import MAIN_BTN_STYLE, MAIN_BTN_WIDTH
from app_utils import go_to_wildberries
from app_utils import go_to_ozon


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

    main_page = ft.Row(
        [
            ft.Column(
                [
                    header,
                    btn_ozon,
                    btn_wildberries
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(main_page)


if __name__ == '__main__':
    ft.app(target=main)
