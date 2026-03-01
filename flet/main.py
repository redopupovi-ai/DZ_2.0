import flet

class EmployeeCatalogApp:
    def __init__(self, page: flet.Page):
        self.page = page
        self.page.title = 'Каталог сотрудников компании'
        self.page.window_width = 650
        self.page.window_height = 750
        self.page.padding = 20

        self.employees = []  

        self.build_ui()

    def build_ui(self):
        self.page.add(flet.Text("Каталог сотрудников компании", size=24, weight='bold'))

        self.first_name = flet.TextField(label="Имя сотрудника", width=400)
        self.last_name = flet.TextField(label='Фамилия', width=400)
        self.age = flet.TextField(label='Возраст', width=400, keyboard_type=flet.KeyboardType.NUMBER)
        
        self.position = flet.Dropdown(
            label='Должность',
            width=400,
            options=[
                flet.dropdown.Option("Разработчик"),
                flet.dropdown.Option("Дизайнер"),
                flet.dropdown.Option("Менеджер"),
                flet.dropdown.Option("Тестировщик"),
            ]
        )
        
        self.salary = flet.TextField(label='Зарплата (сом.)', width=400, keyboard_type=flet.KeyboardType.NUMBER)

        self.result_text = flet.Text(size=16)

        add_button = flet.FilledButton('Добавить сотрудника', on_click=self.add_employee)
        clear_button = flet.OutlinedButton('Очистить форму', on_click=self.clear_form)

        self.employees_list = flet.Column(
            scroll=flet.ScrollMode.AUTO,
            spacing=10,
            height=320
        )

        self.page.add(
            self.first_name,
            self.last_name,
            self.age,
            self.position,
            self.salary,
            add_button,
            clear_button,
            self.result_text,
            flet.Text("Список сотрудников (отсортировано по зарплате: от меньшей к большей)", 
                      size=18, weight='bold'),
            self.employees_list
        )

    def validate_data(self):
        if not all([
            self.first_name.value,
            self.last_name.value,
            self.age.value,
            self.position.value,
            self.salary.value
        ]):
            return "Не все поля заполнены!"

        try:
            age = int(self.age.value)
            if age <= 0:
                return "Возраст должен быть положительным числом!"
        except ValueError:
            return "Возраст должен быть числом!"

        try:
            salary = int(self.salary.value)
            if salary <= 0:
                return "Зарплата должна быть положительной!"
        except ValueError:
            return "Зарплата должна быть числом!"

        return None

    def add_employee(self, e):
        error = self.validate_data()

        if error:
            self.result_text.value = error
            self.result_text.color = 'red'
        else:
            employee = {
                "first_name": self.first_name.value.strip(),
                "last_name": self.last_name.value.strip(),
                "age": int(self.age.value),
                "position": self.position.value,
                "salary": int(self.salary.value)
            }

            self.employees.append(employee)
            self.update_employees_list()

            self.result_text.value = f'Сотрудник {employee["first_name"]} {employee["last_name"]} успешно добавлен!'
            self.result_text.color = 'green'

            self.clear_form(None)

        self.page.update()

    def update_employees_list(self):
        self.employees_list.controls.clear()

        sorted_employees = sorted(self.employees, key=lambda x: x["salary"])

        for emp in sorted_employees:
            is_high_salary = emp["salary"] > 100000
            salary_color = "red" if is_high_salary else "black"
            bg_color = "#ffe6e6" if is_high_salary else "white"

            row = flet.Row(
                controls=[
                    flet.Text(
                        f"{emp['first_name']} {emp['last_name']}, {emp['age']} лет, {emp['position']}",
                        size=16,
                        width=340,
                        color='black'
                    ),
                    flet.Text(
                        f"{emp['salary']} сом.",
                        size=16,
                        weight='bold',
                        color=salary_color
                    ),
                    flet.IconButton(
                        icon=flet.Icons.DELETE,
                        icon_color="red",
                        tooltip="Удалить сотрудника",
                        on_click=self.delete_employee(emp)
                    )
                ],
                alignment=flet.MainAxisAlignment.SPACE_BETWEEN
            )

            container = flet.Container(
                content=row,
                padding=12,
                border=flet.border.all(1, "grey"),
                border_radius=8,
                bgcolor=bg_color
            )

            self.employees_list.controls.append(container)

    def delete_employee(self, emp):
        def handler(e):
            self.employees.remove(emp)
            self.update_employees_list()
            self.result_text.value = "Сотрудник удалён"
            self.result_text.color = "orange"
            self.page.update()
        return handler

    def clear_form(self, e):
        self.first_name.value = ""
        self.last_name.value = ""
        self.age.value = ""
        self.salary.value = ""
        self.position.value = None
        self.result_text.value = ""
        self.page.update()


def main(page: flet.Page):
    EmployeeCatalogApp(page)


if __name__ == '__main__':
    flet.run(main)