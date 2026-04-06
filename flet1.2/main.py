import flet as ft
import sqlite3

def init_db():
    conn = sqlite3.connect("employees.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def main(page: ft.Page):
    page.title = "Учет сотрудников"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE 

    conn = init_db()

    name_input = ft.TextField(label="ФИО", width=250)
    position_input = ft.TextField(label="Должность", width=200)
    dept_input = ft.TextField(label="Отдел", width=200)

    search_input = ft.TextField(
        label="Поиск по ФИО", 
        width=300, 
        prefix_icon="search",
        on_change=lambda e: update_table()
    )
    
    sort_dropdown = ft.Dropdown(
        label="Сортировать по",
        width=200,
        options=[
            ft.dropdown.Option("name", "Имени (А-Я)"),
            ft.dropdown.Option("position", "Должности"),
            ft.dropdown.Option("department", "Отделу"),
        ],
        value="name"
    )
    sort_dropdown.on_change = lambda e: update_table()

    employees_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("ФИО")),
            ft.DataColumn(ft.Text("Должность")),
            ft.DataColumn(ft.Text("Отдел")),
        ],
        rows=[]
    )

    def update_table():
        """Обновляет данные в таблице с учетом поиска и сортировки"""
        search_query = search_input.value
        sort_by = sort_dropdown.value

        valid_sort_columns = {"name", "position", "department"}
        if sort_by not in valid_sort_columns:
            sort_by = "name"

        cursor = conn.cursor()
        query = f"SELECT * FROM employees WHERE name LIKE ? ORDER BY {sort_by}"
        cursor.execute(query, (f'%{search_query}%',))
        rows = cursor.fetchall()

        employees_table.rows.clear()
        for row in rows:
            employees_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(row[3])),
                    ]
                )
            )
        page.update()

    def add_employee(e):
        """Добавляет сотрудника в БД и обновляет интерфейс"""
        if not name_input.value or not position_input.value or not dept_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Пожалуйста, заполните все поля!"))
            page.snack_bar.open = True
            page.update()
            return

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, position, department) VALUES (?, ?, ?)",
            (name_input.value, position_input.value, dept_input.value)
        )
        conn.commit()

        name_input.value = ""
        position_input.value = ""
        dept_input.value = ""
        
        update_table()

    add_btn = ft.ElevatedButton("Добавить сотрудника", icon="add", on_click=add_employee)

    page.add(
        ft.Text("Регистрация нового сотрудника", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([name_input, position_input, dept_input, add_btn], wrap=True),
        
        ft.Divider(height=30, thickness=2),
        
        ft.Text("База сотрудников", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([search_input, sort_dropdown], wrap=True),
        employees_table
    )

    update_table()

ft.run(main)
