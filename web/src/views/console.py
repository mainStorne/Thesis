import json

import flet as ft
import flet_easy as fs

from src.layouts.base import BaseLayout

r = fs.AddPagesy()


@r.page(route="/console/", title="Консоль")
async def console_page(data: fs.Datasy):
    token = await data.page.client_storage.get_async('token')
    progressbar = ft.Ref[ft.ProgressBar]()
    uploadbtn = ft.Ref()
    error_text = ft.Ref[ft.Text]()

    def on_upload(e: ft.FilePickerUploadEvent):
        if e.error:
            error = e.error[len("Upload endpoint returned code "):]
            status_code = error[:3]
            error_body = json.loads(error[5:])
            match error_body['detail']:
                case 'Quota filled':
                    error_text.current.value = 'Вы превысили свою квоту'
                case 'Archive error':
                    error_text.current.value = 'При архивации произошла ошибка'

                case _:
                    error_text.current.value = 'Ошибка, попробуйте позже'
            error_text.current.visible = True
            progressbar.current.visible = False
            uploadbtn.current.visible = True
        else:
            progressbar.current.value = e.progress
            if e.progress == 1:
                error_text.current.visible = False
                uploadbtn.current.visible = True

        data.page.update()

    def on_result(e: ft.FilePickerResultEvent):
        upload_list = []
        if file_picker.result != None and file_picker.result.files != None:
            for f in file_picker.result.files:
                upload_list.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=f'/upload?token={token}&name={f.name}',
                    )
                )
            file_picker.upload(upload_list)

            uploadbtn.current.visible = False
            progressbar.current.visible = True
        data.page.update()

    file_picker = ft.FilePicker(on_result=on_result, on_upload=on_upload)
    data.page.overlay.append(file_picker)

    return await BaseLayout(data).build(
        ft.Column([
            ft.Text(ref=error_text, visible=False),
            ft.ProgressRing(value=0, bgcolor="#eeeeee",
                            width=20, height=20, visible=False, ref=progressbar),
            ft.Button('Загрузить', on_click=lambda _: file_picker.pick_files(
                allow_multiple=False, allowed_extensions=['zip']), ref=uploadbtn),
        ], expand=True)
    )
