import flet as ft
import json

class Task(ft.Column):
    def __init__(self, task_name, task_delete, task_save, task_category, completed=False, get_category=None):
        super().__init__()
        self.completed = completed
        self.task_name = task_name
        self.task_delete = task_delete
        self.task_save = task_save
        self.task_category = task_category
        self.get_category = get_category

    def build(self):
        self.display_task = ft.Checkbox(
            value=self.completed, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                self.get_category(self.task_category), 
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE_OUTLINED,
                    icon_color=ft.Colors.RED,
                    tooltip="Cancel",
                    on_click=self.cancel_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def update_categories(self, categories):
        dropdown = self.edit_view.controls[1] 
        dropdown.options = [ft.dropdown.Option(cat) for cat in categories]

    # если текущая категория больше не существует — сбрасываем на первую
        if dropdown.value not in categories:
            dropdown.value = categories[0]

        dropdown.update()


    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label or self.task_name
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def cancel_clicked(self, e):
        self.edit_name.value = self.task_name
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def save_clicked(self, e):
        new_name = self.edit_name.value.strip()
        new_category = self.edit_view.controls[1].value  # берём значение из нового Dropdown

        if not new_name:
            self.cancel_clicked(e)
            return

        self.task_name = new_name
        self.task_category = new_category
        self.display_task.label = self.task_name
        self.display_view.visible = True
        self.edit_view.visible = False
        self.task_save()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_save()

    def delete_clicked(self, e):
        self.task_delete(self)


@ft.control()
class VIPTodoApp(ft.Column):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.category = self.all_category()

        # фабрика для создания Dropdown
        def make_category_dropdown(value=None):
            return ft.Dropdown(
                label="Категория",
                value=value or self.category[0],
                options=[ft.dropdown.Option(cat) for cat in self.category]
            )

        self.make_category_dropdown = make_category_dropdown

        self.task_input = ft.TextField(
            label="Название задачи",
            autofocus=True,
            on_submit=self.handle_confirm,
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^[a-zA-Zа-яА-Я0-9\s\-_.,]*$",
                replacement_string=""
            ),
        )

        self.error_text = ft.Text(color=ft.Colors.RED_400, size=12, visible=False)

        # FIX: теперь создаётся новый Dropdown
        self.category_dropdown = self.make_category_dropdown()

        self.add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Новая задача"),
            content=ft.Column([self.task_input, self.category_dropdown, self.error_text], tight=True),
            actions=[
                ft.Button("Отмена", on_click=self.handle_dismiss),
                ft.Button("Создать", on_click=self.handle_confirm)
            ],
        )

        # отдельный Dropdown для удаления категории
        self.delete_category_dropdown = self.make_category_dropdown()

        self.add_category_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Добавить категорию"),
            content=ft.TextField(label="Название категории", autofocus=True),
            actions=[
                ft.Button("Отмена", on_click=self.handle_add_category_dismiss),
                ft.Button("Добавить", on_click=self.handle_add_category_confirm)
            ],
        )

        self.delete_category_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Удалить категорию"),
            content=self.delete_category_dropdown,
            actions=[
                ft.Button("Отмена", on_click=self.handle_delete_category_dismiss),
                ft.Button("Удалить", on_click=self.handle_delete_category_confirm)
            ],
        )

        self.tasks = ft.Column()

        self.filter = ft.TabBar(
            scrollable=True,
            tabs=[ft.Tab(label=cat) for cat in self.category]
        )

        self.filter_tabs = ft.Tabs(
            length=len(self.filter.tabs),
            selected_index=0,
            on_change=lambda e: self.update(),
            content=self.filter
        )

        self.category_button = ft.Button("Добавить категорию", on_click=self.add_category_show)
        self.delete_category_button = ft.Button("Удалить категорию", on_click=self.delete_category_show)

        self.controls = [
            ft.Row(
                [ft.Text("✓ VIP Tasks", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, font_family="cause-regular")],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            self.filter_tabs,
            ft.Row([self.category_button, self.delete_category_button], alignment=ft.MainAxisAlignment.CENTER),
            self.tasks,
        ]

    def did_mount(self):
        self.page.overlay.append(self.add_dialog)
        self.page.overlay.append(self.add_category_dialog)
        self.page.overlay.append(self.delete_category_dialog)
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=self.show_add_dialog,
        )
        self.page.update()
        self.old_task()

    def before_update(self):
        status = self.filter.tabs[self.filter_tabs.selected_index].label
        for task in self.tasks.controls:
            task.visible = (status == "Все" or status == task.task_category)

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.save()

    def save(self):
        with open("tasks.json", "w", encoding="utf-8") as file:
            json.dump(
                [{"name": t.task_name, "category": t.task_category, "completed": t.completed}
                 for t in self.tasks.controls],
                file, ensure_ascii=False, indent=4
            )

        with open("category.json", "w", encoding="utf-8") as file:
            json.dump(self.category, file, ensure_ascii=False, indent=4)

        self.update()
        self.update_tabs()

    def get_category(self, value=None):
        return self.make_category_dropdown(value)

    def handle_delete_category_confirm(self, e):
        category_name = self.delete_category_dropdown.value
        if category_name in self.category:
            if category_name == self.category[0]:
                self.delete_category_dialog.open = False
                return

            self.category.remove(category_name)

            for task in self.tasks.controls:
                if task.task_category == category_name:
                    task.task_category = self.category[0]

            self.update_tabs()
            self.save()

        self.delete_category_dialog.open = False
        self.delete_category_dialog.update()

    def delete_category_show(self, e):
        self.delete_category_dialog.open = True
        self.delete_category_dialog.update()

    def handle_delete_category_dismiss(self, e):
        self.delete_category_dialog.open = False
        self.delete_category_dialog.update()

    def handle_add_category_confirm(self, e):
        category_name = self.add_category_dialog.content.value.strip()
        if not category_name:
            return

        self.category.append(category_name)
        self.add_category_dialog.content.value = ""
        self.add_category_dialog.open = False
        self.add_category_dialog.update()
        self.update_tabs()
        self.save()

    def add_category_show(self, e):
        self.add_category_dialog.open = True
        self.add_category_dialog.update()

    def handle_add_category_dismiss(self, e):
        self.add_category_dialog.content.value = ""
        self.add_category_dialog.open = False
        self.add_category_dialog.update()

    def handle_confirm(self, e):
        task_name = self.task_input.value.strip()
        if not task_name:
            self.error_text.value = "Поле не может быть пустым"
            self.error_text.visible = True
            self.error_text.update()
            return

        self.task_add(task_name, task_category=self.category_dropdown.value)

        self.task_input.value = ""
        self.error_text.visible = False
        self.add_dialog.open = False
        self.add_dialog.update()
        self.save()

    def show_add_dialog(self, e):
        self.add_dialog.open = True
        self.add_dialog.update()

    def handle_dismiss(self, e):
        self.task_input.value = ""
        self.error_text.visible = False
        self.task_input.update()

        self.add_dialog.open = False
        self.add_dialog.update()

    def old_task(self):
        try:
            with open("tasks.json", "r", encoding="utf-8") as file:
                ideas = json.load(file)
        except:
            ideas = []

        for dct in ideas:
            self.task_add(dct["name"], task_category=dct["category"], completed=dct["completed"])

    def all_category(self):
        try:
            with open("category.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return ["Все"]

    def update_tabs(self):
        self.filter.tabs = [ft.Tab(label=cat) for cat in self.category]
        self.filter_tabs.length = len(self.filter.tabs)

        self.category_dropdown.options = [ft.dropdown.Option(cat) for cat in self.category]
        self.category_dropdown.update()

        self.delete_category_dropdown.options = [ft.dropdown.Option(cat) for cat in self.category]
        self.delete_category_dropdown.update()

    # обновляем категории в режиме редактирования у всех задач
        for task in self.tasks.controls:
            task.update_categories(self.category)

        self.update()


    def task_add(self, task_name, task_category="Все", completed=False):
        task = Task(
            task_name,
            self.task_delete,
            self.save,
            task_category,
            completed,
            self.get_category
        )
        self.tasks.controls.append(task)
        self.update()


def main(page: ft.Page):
    page.title = "VIP To-Do"
    page.fonts = {
        "cause-regular": "fonts/Cause-Regular.ttf"
    }
    page.add(VIPTodoApp())


ft.run(main)
