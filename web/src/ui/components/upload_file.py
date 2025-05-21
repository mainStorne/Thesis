import json
from typing import Any, Callable

import flet as ft

from .btn import ThesisButton


class UploadProjectComponent:

    def __init__(self, data, on_result: Callable[[Callable[[str], Any]], Any], on_500_server_error: Callable[[], Any], on_error: Callable[[int, str], Any], on_success: Callable[[dict], Any]):
        self.on_error = on_error
        self.handle_result = self._handle_result(on_result)
        self.on_500_server_error = on_500_server_error
        self.on_success = on_success
        self.data = data
        self.upload_btn = ft.Ref[ft.Button]()
        self.file_picker = ft.FilePicker(
            self.handle_result, self.handle_upload)
        self.data.page.overlay.append(self.file_picker)

    def pick_files(self):
        return self.file_picker.pick_files(
            allow_multiple=False, allowed_extensions=["zip"])

    def _handle_result(self, on_result):
        @on_result
        def wrapped(upload_url: str):
            if self.file_picker.result is None and self.file_picker.result.files is None:
                return

            upload_list = []
            for f in self.file_picker.result.files:
                upload_list.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url
                    )
                )
            self.file_picker.upload(upload_list)
            self.upload_btn.current.disabled = True

        return lambda _: wrapped()

    def handle_upload(self, e: ft.FilePickerUploadEvent):
        if not e.error:
            return
        # work around on hand filepicker state
        self.data.page.overlay.remove(self.file_picker)
        self.file_picker = ft.FilePicker(
            self.handle_result, self.handle_upload)
        self.data.page.overlay.append(self.file_picker)
        self.data.page.update()
        # only this trick available for communication
        error = e.error[len("Upload endpoint returned code "):]
        status_code = int(error[:3])
        if status_code == 500:
            self.on_500_server_error()
        elif status_code == 418:
            self.on_success(json.loads(error[5:])['detail'])
        else:
            response = json.loads(error[5:])
            self.on_error(status_code, response['detail'])

    def build(self):
        return ThesisButton(
            "Загрузить",
            on_click=lambda _: self.pick_files(),
            ref=self.upload_btn,
        )
