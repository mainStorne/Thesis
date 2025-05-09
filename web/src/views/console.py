import flet as ft
import flet_easy as fs

from src.layouts.base import BaseLayout

r = fs.AddPagesy(route_prefix='/console')


# We add a page
@r.page(route="", title="Консоль")
async def index_page(data: fs.Datasy):
    token = await data.page.client_storage.get_async('token')

    def on_result(e: ft.FilePickerResultEvent):
        print("Selected files:", e.files)
        print("Selected file or directory:", e.path)
        upload_list = []
        if file_picker.result != None and file_picker.result.files != None:
            for f in file_picker.result.files:
                upload_list.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=f'/upload?token={token}',
                    )
                )
            file_picker.upload(upload_list)

    file_picker = ft.FilePicker(on_result=on_result)
    data.page.overlay.append(file_picker)
    data.page.update()
    # file_picker.upload()
    # ft.FilePickerUploadFile()
    login = fs.Ref()

    return await BaseLayout(data).build(
        ft.Column([
            ft.TextField(label='Логин', ref=login),
            ft.Button('Загрузить', on_click=lambda _: file_picker.pick_files()),
        ])
    )
