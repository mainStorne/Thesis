
import asyncio

import flet as ft
import flet_easy as fs

from src.api.db.users import Account
from src.api.repos.docker_repo import docker_repo
from src.api.services.project_service import project_service
from src.conf import database, log
from src.ui.components.field import ThesisText
from src.ui.components.log_panel import ThesisLogPanel
from src.ui.components.panel import ThesisPanel
from src.ui.components.toast_component import ErrorToast, SuccessToast
from src.ui.components.upload_file import UploadProjectComponent
from src.ui.depends import user
from src.ui.layouts.layout import ThesisLayout
from src.ui.utils import is_uuid

r = fs.AddPagesy(route_prefix='/projects')


@r.page(route='/{id}', protected_route=True)
@user
async def project(data: fs.Datasy, id: str, user: Account):
    token = await data.page.client_storage.get_async("token")
    id = is_uuid(id)
    if not id:
        return data.page.go('/not-found')
    async with database.session_maker() as session:
        project = await project_service.get_by_id(session, id)
    if not project:
        return data.page.go('/not-found')
    log_panel_component = ThesisLogPanel(expand=True)

    async def delete_project(e):
        try:
            async with database.session_maker() as session:
                if user.student:
                    await project_service.delete_student_project(session, user, project)
                else:
                    await project_service.delete_project(session, user, project)

        except Exception as e:
            await log.aexception('error', exc_info=e)
            data.page.open(ErrorToast("Ошибка попробуйте позже!"))
        else:
            data.page.open(SuccessToast("Проект был удален!"))
        finally:
            data.page.close(confirm_deleting)

    async def stream_logs():
        await asyncio.sleep(0.2)
        service_name = project_service.get_service_name(user, project.name)
        async for record in docker_repo.stream_service_log(service_name):
            log_panel_component.add_message(record)

    def build_url_hook():
        prefix_url = '/student' if user.student else '/teacher'
        return f"{prefix_url}/upload?token={token}&project_id={project.id}", 'PUT'

    def on_error(error: str):
        data.page.open(ErrorToast(error))

    upload_project_component = UploadProjectComponent(data, on_error=on_error,
                                                      build_upload_hook=build_url_hook)

    upload_project_component.build().visible = False  # FIX forn now

    confirm_deleting = ft.AlertDialog(
        modal=True,
        title=ft.Text(value=f'Удалить проект {project.name}?'),
        actions=[
            ft.TextButton('Да', on_click=delete_project),
            ft.TextButton(
                'Нет', on_click=lambda _: data.page.close(confirm_deleting)),
        ]
    )
    data.page.run_task(stream_logs)

    return await ThesisLayout(data).build(
        ThesisPanel(content=ft.Column([
            ft.Row([
                ft.Row(
                    [ThesisText(value=f'Проект: {project.name}', weight=ft.FontWeight.BOLD, size=30)]),
                ft.Row([
                    ft.IconButton(ft.Icons.UPDATE, icon_color=ft.Colors.YELLOW,
                                  on_click=lambda _: upload_project_component.upload_project_component.pick_files()),
                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED,
                                  on_click=lambda _: data.page.open(confirm_deleting)),
                ])

            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Column([
                ft.Row(
                    [ThesisText(value=f'Создан: {project.view_created_at}')]),
                ft.Row(
                    [ThesisText(value=f'Размер проекта: {project.byte_size}')]),
                ft.Row(
                    [ft.Container(ThesisText(value=f'URL: {project.project_url}', selectable=True), on_click=lambda e: data.page.launch_url(project.project_url))]),
                ft.Row(
                    [ThesisText(value=f'Базовый Образ: {project.project_image.name}')]),
            ],),
            ft.Container(ft.Column([log_panel_component], scroll=True), expand=True,
                         border=ft.border.all(1, ft.Colors.WHITE38),
                         border_radius=ft.border_radius.all(15),
                         padding=10,),
        ],  spacing=20), width=None, height=None)
    )
