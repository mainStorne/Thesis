import json
from secrets import token_urlsafe
from uuid import UUID

import flet as ft
import flet_easy as fs

from src.api.services.project_service import project_service
from src.conf import database, uploadfile_queue
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisText, ThesisTextField
from src.ui.components.log_panel import ThesisListPanel
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.student import StudentLayout

r = fs.AddPagesy(route_prefix='/users/me/projects')


@r.page(route="")
async def my_projects(data: fs.Datasy):
    token = await data.page.client_storage.get_async("token")
    async with database.session_maker() as session:
        projects = (await project_service.get_student_projects(session, token)).all()

    project_card = ft.Column(
        controls=[
            ft.Container(ft.Row([ft.Text(project.name, width=150, overflow=ft.TextOverflow.ELLIPSIS, tooltip=ft.Tooltip(
                project.name, enable_feedback=True)),
                ft.Text(project.project_template.name, width=150),
                ft.Text(project.created_at.strftime(
                    r'%Y.%d.%m, %H:%M:%S'), width=150),
            ]),
                on_click=lambda e: data.page.go(
                    f'/users/me/projects/{e.control.data['id']}'),
                data={'id': project.id}
            )
            for project in projects],
    )
    project_card.controls.insert(0, ft.Container(
        ft.Row([ft.Text('Название проекта', width=150),
                ft.Text('Шаблон проекта:', width=150),
                ft.Text('Дата создания', width=150),
                ])))

    return await StudentLayout(data).build(
        ft.Container(ft.Container(
            project_card,), margin=15, alignment=ft.alignment.top_left)
    )


@r.page(route="/create")
async def create_project(data: fs.Datasy):
    async with database.session_maker() as session:
        templates = await project_service.get_project_templates(session)

    project_name = ft.Ref[ft.TextField]()

    token = await data.page.client_storage.get_async("token")
    progressbar = ft.Ref[ft.ProgressBar]()
    queue_token = token_urlsafe(4)
    queue = uploadfile_queue[queue_token]
    upload_btn = ft.Ref()
    template_id: None | UUID = None
    message = ft.Ref[ft.Markdown]()
    list_panel = ThesisListPanel(width=500, )
    console_log = ft.AlertDialog(
        title=ft.Text("Сборка проекта"),
        content=list_panel,
        alignment=ft.alignment.center,
        title_padding=ft.padding.all(25),
        scrollable=True,
    )
    log_btn = ft.Ref[ft.Button]()

    def on_upload(e: ft.FilePickerUploadEvent):
        nonlocal file_picker

        if e.error:
            error = e.error[len("Upload endpoint returned code "):]
            status_code = int(error[:3])
            if status_code == 500:
                message.current.value = 'Ошибка повторите позже'
            # only this trick available for communication
            if status_code == 418:
                progressbar.current.visible = False
                error_body = json.loads(error[5:])['detail']
                message.current.value = f'Приложения успешно загружено [Перейдите по адресу]({error_body['url']})'
                upload_btn.current.visible = True
            else:
                error_body = json.loads(error[5:])
                match error_body['detail']:
                    case 'Project exists':
                        message.current.value = 'Проект с таким же именем уже существует'
                    case 'Template not found':
                        message.current.value = 'Шаблон приложения не найден'
                    case 'Limit is full':
                        message.current.value = 'Вы исчерпали свою квоту! Не хватает места'
                    case 'File with no size':
                        message.current.value = 'Отправлен файл без размера'

            message.current.visible = True
            progressbar.current.visible = False
            data.page.overlay.remove(file_picker)
            file_picker = ft.FilePicker(
                on_result=on_result, on_upload=on_upload)
            data.page.overlay.append(file_picker)
            upload_btn.current.visible = True

        else:
            progressbar.current.value = e.progress

        data.page.update()

    def on_dropdown_change(e: ft.ControlEvent):
        nonlocal template_id
        template_id = e.control.value

    async def on_message(*args):
        nonlocal queue, message

        result = await queue.get()
        log_btn.current.visible = True
        data.page.open(console_log)
        while True:
            result = await queue.get()
            list_panel.add_message(result)

    def on_result(e: ft.FilePickerResultEvent):
        message.current.visible = False
        log_btn.current.visible = False
        if file_picker.result is None and file_picker.result.files is None and not template_id:
            return

        upload_list = []
        for f in file_picker.result.files:
            upload_list.append(
                ft.FilePickerUploadFile(
                    f.name,
                    upload_url=f"/upload?token={token}&name={project_name.current.value}&template_id={template_id}&queue_token={queue_token}",
                )
            )
        file_picker.upload(upload_list)

        upload_btn.current.visible = False
        progressbar.current.visible = True
        data.page.run_task(on_message)
        data.page.update()

    file_picker = ft.FilePicker(on_result=on_result, on_upload=on_upload)
    data.page.overlay.append(file_picker)

    options = [
        ft.DropdownOption(key=template.id,
                          text=template.name,
                          style=ft.ButtonStyle(
                              bgcolor=ft.Colors.WHITE,
                              padding=0,
                              shape=ft.ContinuousRectangleBorder()
                          ),
                          text_style=ft.TextStyle(
                              color=ft.Colors.BLACK),
                          content=ThesisText(value=template.name, text_align=ft.TextAlign.CENTER)) for template in templates]

    return await StudentLayout(data).build(
        ThesisPanel(
            content=ft.Column(
                [
                    ft.Column(
                        [
                            ft.Markdown(ref=message, visible=False,
                                        on_tap_link=lambda e: data.page.launch_url(
                                            e.data),
                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                        selectable=True),
                            ft.ProgressRing(value=0, bgcolor="#eeeeee", width=20,
                                            height=20, visible=False, ref=progressbar),
                            ft.Dropdown(leading_icon=ft.Icon(ft.Icons.DASHBOARD_CUSTOMIZE, color=ft.Colors.BLACK), label='Шаблоны проектов:', label_style=ft.TextStyle(color=ft.Colors.BLACK), text_style=ft.TextStyle(
                                color=ft.Colors.BLACK), on_change=on_dropdown_change,  options=options,
                                expand=True,
                            ),

                            ThesisTextField("Название", ref=project_name),
                        ],
                        spacing=20,
                    ),
                    ThesisButton(
                        "Загрузить",
                        on_click=lambda _: file_picker.pick_files(
                            allow_multiple=False, allowed_extensions=["zip"]),
                        ref=upload_btn,
                    ),
                    ThesisButton(
                        "Посмотреть логи сборки",
                        on_click=lambda _: data.page.open(console_log),
                        visible=False,
                        ref=log_btn,
                    ),
                ],
                spacing=10,
            ),
        )

    )
