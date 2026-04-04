from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

import flet as ft


@dataclass
class Task:
    title: str
    priority: str
    done: bool = False
    deadline: str | None = None
    notified: bool = False

    def deadline_date(self) -> date | None:
        if not self.deadline:
            return None
        try:
            return datetime.fromisoformat(self.deadline).date()
        except ValueError:
            return None

    def is_overdue(self) -> bool:
        deadline = self.deadline_date()
        if self.done or deadline is None:
            return False
        return date.today() > deadline


class TodoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "TODO Планировщик"
        self.page.window_width = 760
        self.page.window_height = 820
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO

        self.data_file = Path(__file__).with_name("tasks.json")
        self.tasks: list[Task] = []
        self.deadline_dialog: ft.AlertDialog | None = None

        self.load_tasks()
        self.build_ui()
        self.refresh_view()

        self.page.run_task(self.deadline_watcher)

    # интерфэйс
    def build_ui(self):
        self.task_input = ft.TextField(label="Задача", expand=True)

        self.priority = ft.Dropdown(
            label="Приоритет",
            width=160,
            options=[
                ft.dropdown.Option("Высокий"),
                ft.dropdown.Option("Средний"),
                ft.dropdown.Option("Низкий"),
            ],
        )

        self.deadline_input = ft.TextField(
            label="Дедлайн (ГГГГ-ММ-ДД)",
            width=220,
        )

        self.search_input = ft.TextField(
            label="Поиск задач",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.refresh_view(),
        )

        self.stats_text = ft.Text(size=14, weight=ft.FontWeight.W_500)
        self.file_info_text = ft.Text(size=12, color=ft.Colors.GREY_700)
        self.task_list = ft.Column(spacing=10)

        add_btn = ft.ElevatedButton("Добавить", icon=ft.Icons.ADD, on_click=self.add_task)
        save_btn = ft.OutlinedButton(
            "Сохранить в файл", icon=ft.Icons.SAVE, on_click=self.save_to_file_click
        )

        self.page.add(
            ft.Text("Планировщик задач", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Можно добавлять задачи, отмечать выполненные, искать, смотреть статистику и сохранять всё в JSON-файл.",
                size=13,
                color=ft.Colors.GREY_700,
            ),
            ft.Row([self.task_input, self.priority], spacing=10),
            ft.Row([self.deadline_input, add_btn, save_btn], spacing=10, wrap=True),
            self.search_input,
            ft.Container(
                content=ft.Column([self.stats_text, self.file_info_text], spacing=4),
                padding=12,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10,
            ),
            ft.Divider(),
            self.task_list,
        )

    #Работа с датой 
    def parse_deadline(self, value: str | None) -> datetime | None:
        if not value or not value.strip():
            return None

        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d")
        except ValueError:
            return None

    def format_deadline(self, deadline_str: str | None) -> str:
        if not deadline_str:
            return "Без дедлайна"

        try:
            deadline = datetime.fromisoformat(deadline_str)
            return deadline.strftime("%d.%m.%Y")
        except ValueError:
            return deadline_str

    #Загрузка / сохранение 
    def load_tasks(self):
        if not self.data_file.exists():
            self.tasks = []
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                self.tasks = []
                return

            loaded_tasks: list[Task] = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                loaded_tasks.append(
                    Task(
                        title=str(item.get("title", "")),
                        priority=str(item.get("priority", "")),
                        done=bool(item.get("done", False)),
                        deadline=item.get("deadline"),
                        notified=bool(item.get("notified", False)),
                    )
                )

            self.tasks = loaded_tasks

        except (json.JSONDecodeError, OSError):
            self.tasks = []

    def save_tasks(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump([asdict(task) for task in self.tasks], f, ensure_ascii=False, indent=2)

    def save_to_file_click(self, e):
        self.save_tasks()
        self.show_message(f"Задачи сохранены в файл: {self.data_file.name}")
        self.refresh_view(update_page=True)

    # Утилиты
    def show_message(self, text: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(text))
        self.page.snack_bar.open = True
        self.page.update()

    def refresh_view(self, update_page: bool = True):
        self.update_statistics()
        self.update_tasks()
        if update_page:
            self.page.update()

    def get_filtered_tasks(self):
        query = self.search_input.value.strip().lower() if self.search_input.value else ""

        result = []
        for index, task in enumerate(self.tasks):
            if not query:
                result.append((index, task))
                continue

            haystack = " ".join(
                [
                    task.title,
                    task.priority,
                    self.format_deadline(task.deadline),
                ]
            ).lower()

            if query in haystack:
                result.append((index, task))

        return result

    # Добавление
    def add_task(self, e):
        title = self.task_input.value.strip()
        priority = self.priority.value
        deadline_raw = self.deadline_input.value.strip() if self.deadline_input.value else ""

        if not title or not priority:
            self.show_message("Введите задачу и выберите приоритет.")
            return

        deadline = self.parse_deadline(deadline_raw)
        if deadline_raw and deadline is None:
            self.show_message("Неверный формат дедлайна. Используйте: ГГГГ-ММ-ДД")
            return

        task = Task(
            title=title,
            priority=priority,
            done=False,
            deadline=deadline.isoformat() if deadline else None,
            notified=False,
        )

        self.tasks.append(task)
        self.save_tasks()

        self.task_input.value = ""
        self.priority.value = None
        self.deadline_input.value = ""

        self.refresh_view()

    #Статистика
    def update_statistics(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.done)
        active = total - completed
        overdue = sum(1 for task in self.tasks if task.is_overdue())

        by_priority = {"Высокий": 0, "Средний": 0, "Низкий": 0}
        for task in self.tasks:
            if task.priority in by_priority:
                by_priority[task.priority] += 1

        self.stats_text.value = (
            f"Всего: {total} | Выполнено: {completed} | Активных: {active} | Просрочено: {overdue}"
        )
        self.file_info_text.value = (
            f"Высокий: {by_priority['Высокий']} | Средний: {by_priority['Средний']} | "
            f"Низкий: {by_priority['Низкий']} | Файл: {self.data_file.resolve()}"
        )

    #Отрисовка списка 
    def update_tasks(self):
        self.task_list.controls.clear()
        filtered = self.get_filtered_tasks()

        if not filtered:
            self.task_list.controls.append(
                ft.Text("Ничего не найдено.", color=ft.Colors.GREY_700)
            )
            return

        for real_index, task in filtered:
            color = ft.Colors.BLACK
            if task.priority == "Высокий":
                color = ft.Colors.RED
            elif task.priority == "Средний":
                color = ft.Colors.ORANGE
            elif task.priority == "Низкий":
                color = ft.Colors.GREEN

            is_done = task.done
            is_overdue = task.is_overdue()
            deadline_text = self.format_deadline(task.deadline)

            title_style = ft.TextStyle(
                size=16,
                color=ft.Colors.GREY_700 if is_done else color,
                decoration=ft.TextDecoration.LINE_THROUGH if is_done else ft.TextDecoration.NONE,
                weight=ft.FontWeight.W_600,
            )

            info_color = ft.Colors.RED if is_overdue else ft.Colors.GREY_700
            info_label = f"Приоритет: {task.priority} | Дедлайн: {deadline_text}"
            if is_overdue:
                info_label += " | ПРОСРОЧЕНО"
            if is_done:
                info_label += " | Выполнено"

            task_card = ft.Container(
                padding=12,
                border_radius=12,
                bgcolor=ft.Colors.GREY_50,
                border=ft.border.all(1, ft.Colors.GREY_300),
                content=ft.Row(
                    [
                        ft.Checkbox(
                            value=is_done,
                            on_change=lambda e, i=real_index: self.toggle_task(i, e.control.value),
                        ),
                        ft.Column(
                            [
                                ft.Text(task.title, style=title_style),
                                ft.Text(info_label, size=12, color=info_color),
                            ],
                            expand=True,
                            spacing=4,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Удалить",
                            on_click=lambda e, i=real_index: self.delete_task(i),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            )

            self.task_list.controls.append(task_card)

    #Изменение состояния
    def toggle_task(self, index: int, value: bool):
        self.tasks[index].done = bool(value)
        if value:
            self.tasks[index].notified = True
        self.save_tasks()
        self.refresh_view()

    def delete_task(self, index: int):
        self.tasks.pop(index)
        self.save_tasks()
        self.refresh_view()

    # Уведомление 
    def close_deadline_dialog(self, e=None):
        if self.deadline_dialog is not None:
            self.deadline_dialog.open = False
            self.page.update()

    def show_deadline_popup(self, task: Task):
        self.deadline_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Дедлайн истёк"),
            content=ft.Text(
                f"У задачи '{task.title}' истёк срок: {self.format_deadline(task.deadline)}"
            ),
            actions=[ft.TextButton("ОК", on_click=self.close_deadline_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(self.deadline_dialog)

    async def deadline_watcher(self):
        while True:
            if self.deadline_dialog is None or not self.deadline_dialog.open:
                for task in self.tasks:
                    if task.done or task.notified or task.deadline is None:
                        continue

                    if task.is_overdue():
                        task.notified = True
                        self.save_tasks()
                        self.show_deadline_popup(task)
                        self.refresh_view()
                        break

            await asyncio.sleep(30)


def main(page: ft.Page):
    TodoApp(page)


if __name__ == "__main__":
    ft.app(target=main)
