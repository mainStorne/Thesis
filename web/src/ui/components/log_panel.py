
import flet as ft


class ThesisLogPanel(ft.Container):

    def __init__(self, **kwargs):

        self._text = ''
        self._listview = ft.Markdown(
            value=self._text,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
            selectable=True)
        super().__init__(**kwargs, content=self._listview, bgcolor=ft.Colors.BLACK)

    def add_message(self, text: str):
        self._text += text + '\n'
        self._listview.value = self._text

        self.page.update()
