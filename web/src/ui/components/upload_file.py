import json
from typing import Any, Callable

import flet as ft

from src.ui.components.toast_component import SuccessToast

from .btn import ThesisButton
from .console_log import ConsoleLogComponent


class UploadFileComponent:

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


class UploadProjectComponent:

    def __init__(self, data, on_error: Callable[[str], Any], build_upload_hook: Callable[[], str]):
        self.data = data
        self.on_error = on_error
        self.build_upload_hook = build_upload_hook
        self.upload_project_component = UploadFileComponent(
            data, on_result=self.on_result, on_500_server_error=self.handle_500_server_error, on_success=self.handle_success,
            on_error=self.handle_error)
        self.console_log_component = ConsoleLogComponent(data)

    def on_result(self, handler):
        def wrapped():
            self.console_log_component.log_btn.current.visible = False
            upload_url = self.build_upload_hook()
            # status_text.current.visible = False
            # if not template_id:
            #     return
            # prefix_url = '/student' if user.student else '/teacher'
            # upload_url = f"{prefix_url}/upload?token={token}&project_name={project_name.current.value}&template_id={template_id}&queue_token={console_log_component.queue_token}"

            handler(upload_url)
            self.data.page.run_task(self.console_log_component.on_message)
            self.data.page.update()

        return wrapped

    def handle_error_text(self, func):
        def wrapped(*args, **kwargs):
            func(*args, **kwargs)
            # status_text.current.visible = True
            self.upload_project_component.upload_btn.current.disabled = False
            self.data.page.update()

        return wrapped

    @handle_error_text
    def handle_500_server_error(self):
        self.on_error('Ошибка повторите позже')

    @handle_error_text
    def handle_success(self, response: dict):
        self.data.page.open(SuccessToast(
            'Проект успешно загружен! Создаю проект...'))
        project_url = response['url']
        self.data.page.launch_url(project_url)

    @handle_error_text
    def handle_error(self, status_code: int, detail: str):
        match detail:
            case 'Project exists':
                msg = 'Проект с таким же именем уже существует'
            case 'Template not found':
                msg = 'Шаблон приложения не найден'
            case 'Limit is full':
                msg = 'Вы исчерпали свою квоту! Не хватает места'
            case 'File with no size':
                msg = 'Отправлен файл без размера'
            case 'Zipfile errro':
                msg = 'Отправленный файл должен быть ZIP формата'
            case 'Project name is wrong':
                msg = 'Имя дожно содержать только ASCII-символы'
            case _:
                msg = 'Что-то пошло не так, попробуйте ещё раз'

        self.on_error(msg)
