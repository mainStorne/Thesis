
import flet as ft
import flet_easy as fs

from src.api.db.resource import ProjectImage
from src.api.services.project_image_service import project_image_service
from src.conf import database
from src.ui.components.field import ThesisText, ThesisTextField
from src.ui.components.list_component import ListComponent
from src.ui.components.panel import ThesisPanel
from src.ui.components.toast_component import ErrorToast, SuccessToast
from src.ui.layouts.layout import ThesisLayout

r = fs.AddPagesy(route_prefix='/images')


@r.page(route="", protected_route=True)
async def my_projects(data: fs.Datasy):
    async with database.session_maker() as session:
        images = await project_image_service.list(session)

    list_component = ListComponent()
    for image in images:
        list_component.append(
            content=ft.Row([
                ThesisText(value=image.name)
            ])
        )

    return await ThesisLayout(data).build(
        ThesisPanel(
            content=list_component
        )
    )


@r.page(route="/create", protected_route=True)
async def create_project_image(data: fs.Datasy):
    dockerfile_definition = ft.Ref[ft.Markdown]()
    project_image_name = ft.Ref[ft.Text]()

    async def create_project_image(e):
        try:
            async with database.session_maker() as session:
                await project_image_service.create_database(session, ProjectImage(name=project_image_name.current.value,
                                                                                  dockerfile=dockerfile_definition.current.value))
        except Exception:
            data.page.open(ErrorToast("Ошибка попробуйте позже!"))
        else:
            data.page.open(SuccessToast("Образ создан!"))

    return await ThesisLayout(data).build(
        ft.Container(ft.Container(
            ThesisPanel(
                content=ft.Column([
                    ThesisTextField(
                        "Название образа", ref=project_image_name),
                    ThesisTextField(label_text='Dockerfile Текст', ref=dockerfile_definition,
                                    multiline=True
                                    ),
                    ft.Button(
                        text='Создать', on_click=create_project_image
                    )
                ],
                    spacing=20,
                    expand=True
                )
            )), margin=15)
    )
