from uuid import UUID

import flet as ft
import flet_easy as fs

from src.api.services.project_service import project_service
from src.conf import database
from src.ui.components.console_log import ConsoleLogComponent
from src.ui.components.dropdown import ThesisDropdown
from src.ui.components.field import ThesisText, ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.components.upload_file import UploadProjectComponent
from src.ui.layouts.student import StudentLayout
from src.ui.utils import is_uuid

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


@r.page(route="/create")
async def create_project(data: fs.Datasy):
    token = await data.page.client_storage.get_async("token")
    async with database.session_maker() as session:
        templates = await project_service.get_project_templates(session)

    status_text = ft.Ref[ft.Markdown]()
    mysql_checkbox = ft.Ref[ft.Checkbox]()
    project_name = ft.Ref[ft.TextField]()
    template_id: None | UUID = None

    def on_result(handler):
        def wrapped():
            status_text.current.visible = False
            console_log_component.log_btn.current.visible = False
            mysql_checkbox.current.disabled = True
            if not template_id:
                return
            upload_url = '&create_mysql=true' if mysql_checkbox.current.value else ''
            upload_url = f"/upload?token={token}&project_name={project_name.current.value}&template_id={template_id}&queue_token={console_log_component.queue_token}"+upload_url
            handler(upload_url)
            data.page.run_task(console_log_component.on_message)
            data.page.update()

        return wrapped

    def handle_error_text(func):
        def wrapped(*args, **kwargs):
            func(*args, **kwargs)
            status_text.current.visible = True
            upload_project_component.upload_btn.current.disabled = False
            mysql_checkbox.current.disabled = False
            data.page.update()

        return wrapped

    @handle_error_text
    def handle_500_server_error():
        status_text.current.value = 'Ошибка повторите позже'

    @handle_error_text
    def handle_success(response: dict):
        project_url = response['url']
        data.page.launch_url(project_url)

    @handle_error_text
    def handle_error(status_code: int, detail: str):
        match detail:
            case 'Project exists':
                status_text.current.value = 'Проект с таким же именем уже существует'
            case 'Template not found':
                status_text.current.value = 'Шаблон приложения не найден'
            case 'Limit is full':
                status_text.current.value = 'Вы исчерпали свою квоту! Не хватает места'
            case 'File with no size':
                status_text.current.value = 'Отправлен файл без размера'
            case _:
                status_text.current.value = 'Что-то пошло не так, попробуйте ещё раз'

    upload_project_component = UploadProjectComponent(

        data, on_result=on_result, on_500_server_error=handle_500_server_error, on_success=handle_success,
        on_error=handle_error)
    console_log_component = ConsoleLogComponent(data)

    def on_dropdown_change(e: ft.ControlEvent):
        nonlocal template_id
        template_id = e.control.value

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

                                ft.Markdown(ref=status_text, visible=False,
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
                        upload_project_component.build(),
                        console_log_component.build(),
                    ],
                    spacing=10,
                ),
                height=350,
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
