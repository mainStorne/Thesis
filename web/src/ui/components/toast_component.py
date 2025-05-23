import flet as ft


class SuccessToast(ft.SnackBar):

    def __init__(self, text: str):
        super().__init__(
            ft.Text(text, color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN)


class ErrorToast(ft.SnackBar):

    def __init__(self, text: str):
        super().__init__(
            ft.Text(text, color=ft.Colors.WHITE), bgcolor=ft.Colors.ERROR)


# def toaster(success: SuccessToast, success_text: str):
#     def wrapper(func):

#         async def wrapped(*args, **kwargs):
#             try:
#                 result = await func(*args, **kwargs)
#             except Exception:
#                 pass
