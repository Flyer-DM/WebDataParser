import flet as ft
from app_utils.funcs import search_product
from app_utils.styles import MAIN_BTN_STYLE, SCND_BTN_WIDHT


def go_to_wildberries(e):
    page = e.page
    page.controls.clear()
    page.controls.append(wildberries_page(e))
    page.update()


def wildberries_page(e):
    def start_search_wildberries(e):
        page = e.page
        page.controls.clear()
        page.controls.append(search_product(e, "Wildberries"))
        page.update()

    btn_search = ft.ElevatedButton("Поиск товаров по названию",
                                   on_click=start_search_wildberries, style=MAIN_BTN_STYLE, width=SCND_BTN_WIDHT)

    return ft.Row(
        [
            ft.Column(
                controls=[btn_search],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
