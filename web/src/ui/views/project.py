from uuid import UUID

import flet as ft
import flet_easy as fs

from src.api.services.project_service import project_service
from src.conf import database
from src.ui.components.field import ThesisText
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.layout import ThesisLayout
from src.ui.utils import is_uuid

r = fs.AddPagesy(route_prefix='/projects')


@r.page(route='/{id}', protected_route=True)
async def project(data: fs.Datasy, id: UUID):
    id = is_uuid(id)
    if not id:
        return data.page.go('/not-found')
    async with database.session_maker() as session:
        project = await project_service.get_by_id(session, id)
    if not project:
        return data.page.go('/not-found')
    # if project.mysql_account:
    #     extra = [ft.Column([ThesisText(value='Данные Mysql'), ft.Row([ThesisText(
    #         value=project.mysql_account.login), ThesisText(value=project.mysql_account.password)])])]
    # else:
    #     extra = []

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
    return await ThesisLayout(data).build(
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
                ft.Row(
                    [ThesisText(value=f'Базовый Образ: {project.project_image.name}')]),
            ],),
        ],  spacing=20), width=None, height=None)
    )
