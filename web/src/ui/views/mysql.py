
import flet as ft
import flet_easy as fs

from src.api.services.project_service import project_service
from src.conf import database
from src.ui.layouts.layout import ThesisLayout

r = fs.AddPagesy(route_prefix='/users/me/mysql')


@r.page(route="/create", protected_route=True)
async def create_mysql(data: fs.Datasy):
    #     mysql = await mysql_repo.on_create_project(student_project)
    #     session.add(mysql)
    #     await session.commit()

    token = await data.page.client_storage.get_async("token")
    async with database.session_maker() as session:
        projects = (await project_service.get_user_projects(session, token)).all()

    project_card = ft.Column(
        controls=[
            ft.Container(ft.Row([ft.Text(project.name, width=150, overflow=ft.TextOverflow.ELLIPSIS, tooltip=ft.Tooltip(
                project.name, enable_feedback=True)),
                ft.Text(project.project_image.name, width=150),
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

    return await ThesisLayout(data).build(
        ft.Container(ft.Container(
            project_card,), margin=15, alignment=ft.alignment.top_left, height=800,)
    )
