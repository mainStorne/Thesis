from uuid import UUID

import flet as ft
import flet_easy as fs

from src.api.db.users import Account
from src.api.services.project_service import project_service
from src.conf import database
from src.ui.components.dropdown import ThesisDropdown
from src.ui.components.field import ThesisText, ThesisTextField
from src.ui.components.list_component import ListComponent
from src.ui.components.panel import ThesisPanel
from src.ui.components.upload_file import UploadProjectComponent
from src.ui.depends import user
from src.ui.layouts.layout import ThesisLayout

r = fs.AddPagesy(route_prefix="/users/me/projects")


@r.page(route="", protected_route=True)
async def my_projects(data: fs.Datasy):
    token = await data.page.client_storage.get_async("token")
    async with database.session_maker() as session:
        projects = (await project_service.get_user_projects(session, token)).all()

    list_component = ListComponent()
    list_component.append(
        ft.Row(
            [
                ThesisText(value="Название проекта", width=150),
                ThesisText(value="Шаблон проекта:", width=150),
                ThesisText(value="Дата создания", width=150),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    )

    for project in projects:
        list_component.append(
            content=ft.Row(
                [
                    ThesisText(
                        value=project.name,
                        width=150,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        tooltip=ft.Tooltip(project.name, enable_feedback=True),
                    ),
                    ThesisText(value=project.project_image.name, width=150),
                    ThesisText(value=project.view_created_at, width=150),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            on_click=lambda e: data.page.go(f"/projects/{e.control.data['id']}"),
            data={"id": str(project.id)},
        )

    return await ThesisLayout(data).build(ThesisPanel(content=list_component))


@r.page(route="/create", protected_route=True)
@user
async def create_project(data: fs.Datasy, user: Account):
    token = await data.page.client_storage.get_async("token")
    async with database.session_maker() as session:
        templates = await project_service.get_project_images(session)

    status_text = ft.Ref[ft.Markdown]()
    project_name = ft.Ref[ft.TextField]()
    template_id: None | UUID = None

    def build_url_hook():
        status_text.current.visible = False
        if not template_id:
            return
        prefix_url = "/student" if user.student else "/teacher"
        return (
            f"{prefix_url}/upload?token={token}&project_name={project_name.current.value}&template_id={template_id}",
            "POST",
        )

    def on_error(error: str):
        status_text.current.value = error
        status_text.current.visible = True
        data.page.update()

    upload_project_component = UploadProjectComponent(data, on_error=on_error, build_upload_hook=build_url_hook)

    def on_dropdown_change(e: ft.ControlEvent):
        nonlocal template_id
        template_id = e.control.value

    options = [
        ft.DropdownOption(
            key=template.id,
            text=template.name,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, padding=0, shape=ft.ContinuousRectangleBorder()),
            text_style=ft.TextStyle(color=ft.Colors.BLACK),
            content=ThesisText(value=template.name, text_align=ft.TextAlign.CENTER),
        )
        for template in templates
    ]

    return await ThesisLayout(data).build(
        ft.Column(
            [
                ThesisPanel(
                    content=ft.Column(
                        [
                            ft.Column(
                                [
                                    ft.Markdown(
                                        ref=status_text,
                                        visible=False,
                                        on_tap_link=lambda e: data.page.launch_url(e.data),
                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                        selectable=True,
                                    ),
                                    ThesisDropdown(
                                        ft.Icons.DASHBOARD_CUSTOMIZE,
                                        "Шаблоны проектов:",
                                        on_dropdown_change=on_dropdown_change,
                                        options=options,
                                    ),
                                    ThesisTextField("Название", ref=project_name),
                                ],
                                spacing=20,
                                expand=True,
                            ),
                            upload_project_component.build(),
                        ],
                        spacing=10,
                    ),
                )
            ],
            expand=True,
        )
    )
