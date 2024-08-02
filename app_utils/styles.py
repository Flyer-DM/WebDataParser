import flet as ft


MAIN_BTN_STYLE = ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: ft.colors.WHITE,
                    ft.ControlState.FOCUSED: ft.colors.BLUE,
                    ft.ControlState.DEFAULT: ft.colors.PURPLE_500,
                },
                bgcolor={
                    ft.ControlState.HOVERED: ft.colors.PURPLE_500,
                    ft.ControlState.FOCUSED: ft.colors.BLUE,
                    ft.ControlState.DEFAULT: ft.colors.WHITE,
                },
                animation_duration=1000,
)

MAIN_BTN_WIDTH = 150
SCND_BTN_WIDHT = 300


def add_object(to_add):
    result = ft.Row(
        [
            ft.Column([to_add],
                      alignment=ft.MainAxisAlignment.START,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return result


def add_snack_bar(page: ft.Page, text, color):
    snack_bar = ft.SnackBar(ft.Text(text), bgcolor=color)
    page.snack_bar = snack_bar
    page.snack_bar.open = True

