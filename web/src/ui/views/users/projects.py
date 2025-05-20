import json
from secrets import token_urlsafe
from uuid import UUID

import flet as ft
import flet_easy as fs

from src.api.services.project_service import project_service
from src.conf import database, uploadfile_queue
from src.ui.components.btn import ThesisButton
from src.ui.components.dropdown import ThesisDropdown
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
                ft.Text(project.view_created_at, width=150),
            ]),
                on_click=lambda e: data.page.go(
                    f'/users/me/projects/{e.control.data['id']}'),
                data={'id': str(project.id)}
            )
            for project in projects],
        scroll=True
    )
    project_card.controls.insert(0, ft.Container(
        ft.Row([ft.Text('Название проекта', width=150),
                ft.Text('Шаблон проекта:', width=150),
                ft.Text('Дата создания', width=150),
                ])))

    return await StudentLayout(data).build(
        ft.Container(ft.Container(
            project_card,), margin=15, alignment=ft.alignment.top_left, height=800,)
    )


def is_uuid(value: str):
    try:
        return UUID(value)
    except ValueError:
        return


@r.page(route="/create")
async def create_project(data: fs.Datasy):
    async with database.session_maker() as session:
        templates = await project_service.get_project_templates(session)

    project_name = ft.Ref[ft.TextField]()

    token = await data.page.client_storage.get_async("token")
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
    mysql_checkbox = ft.Ref[ft.Checkbox]()

    def on_upload(e: ft.FilePickerUploadEvent):
        nonlocal file_picker
        if not e.error:
            return

        error = e.error[len("Upload endpoint returned code "):]
        status_code = int(error[:3])
        if status_code == 500:
            message.current.value = 'Ошибка повторите позже'
        # only this trick available for communication
        elif status_code == 418:
            response = json.loads(error[5:])['detail']

            project_url = response['url']
            data.page.launch_url(project_url)
        else:
            response = json.loads(error[5:])
            match response['detail']:
                case 'Project exists':
                    message.current.value = 'Проект с таким же именем уже существует'
                case 'Template not found':
                    message.current.value = 'Шаблон приложения не найден'
                case 'Limit is full':
                    message.current.value = 'Вы исчерпали свою квоту! Не хватает места'
                case 'File with no size':
                    message.current.value = 'Отправлен файл без размера'
                case _:
                    message.current.value = 'Что-то пошло не так, попробуйте ещё раз'

        message.current.visible = True
        data.page.overlay.remove(file_picker)
        file_picker = ft.FilePicker(
            on_result=on_result, on_upload=on_upload)
        data.page.overlay.append(file_picker)
        upload_btn.current.visible = True
        mysql_checkbox.current.disabled = False
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
        mysql_checkbox.current.disabled = True
        if file_picker.result is None and file_picker.result.files is None and not template_id:
            return

        upload_list = []
        for f in file_picker.result.files:
            upload_url = '&create_mysql=true' if mysql_checkbox.current.value else ''
            upload_list.append(
                ft.FilePickerUploadFile(
                    f.name,
                    upload_url=f"/upload?token={token}&project_name={project_name.current.value}&template_id={template_id}&queue_token={queue_token}"+upload_url,
                )
            )
        file_picker.upload(upload_list)

        upload_btn.current.visible = False
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
        ft.Column([
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

                                ThesisDropdown(
                                    ft.Icons.DASHBOARD_CUSTOMIZE, 'Шаблоны проектов:',
                                    on_dropdown_change=on_dropdown_change, options=options),

                                ft.Checkbox(
                                    ref=mysql_checkbox,
                                    label=ThesisText(value='Нужно создать mysql базу данных?')),

                                ThesisTextField(
                                    "Название", ref=project_name),
                            ],
                            spacing=20,
                            expand=True

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
            )], alignment=ft.MainAxisAlignment.CENTER),

    )


@r.page(route='/{id}')
async def project(data: fs.Datasy, id: UUID):
    id = is_uuid(id)
    if not id:
        return data.page.go('/not-found')
    async with database.session_maker() as session:
        project = await project_service.get_by_id(session, id)
    if not project:
        return data.page.go('/not-found')
    if project.mysql_account:
        extra = [ft.Column([ThesisText(value='Данные Mysql'), ft.Row([ThesisText(
            value=project.mysql_account.login), ThesisText(value=project.mysql_account.password)])])]
    else:
        extra = []

    async def delete_project(e):
        data.page.close(confirm_deleting)

    confirm_deleting = ft.AlertDialog(
        modal=True,
        title=ThesisText(value=f'Удалить проект {project.name}?'),
        actions=[
            ft.TextButton('Да', on_click=delete_project),
            ft.TextButton(
                'Нет', on_click=lambda _: data.page.close(confirm_deleting)),
        ]

    )
    return await StudentLayout(data).build(
        ThesisPanel(content=ft.Column([
            ft.Row([
                ft.Row(
                    [ThesisText(value=f'Проект: {project.name}', weight=ft.FontWeight.BOLD, size=30)]),
                ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED,
                              on_click=lambda _: data.page.open(confirm_deleting)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Column([
                ft.Row(
                    [ThesisText(value=f'Создан: {project.view_created_at}')]),
                ft.Row(
                    [ThesisText(value=f'Размер проекта: {project.byte_size}')]),
                ft.Row(
                    [ThesisText(value=f'URL: {project.project_url}', selectable=True)]),
                *extra,
                ft.Row(
                    [ThesisText(value=f'Базовый Образ: {project.project_template.name}')]),
            ],),
        ],  spacing=20), width=None, height=None)
    )
