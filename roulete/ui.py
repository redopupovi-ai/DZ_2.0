import flet as ft


class UI:
    def __init__(self, max_lives: int, bullets_count: int):
        self.max_lives = max_lives
        self.bullets_count = bullets_count

        self.title = ft.Text(
            "Русская рулетка",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )

        self.subtitle = ft.Text(
            "Картинки вместо эмодзи, жизни, несколько пуль и плавная async-анимация",
            size=13,
            color=ft.Colors.WHITE70,
            text_align=ft.TextAlign.CENTER,
        )

        self.main_image = ft.Image(
            src="images/revolver.png",
            width=220,
            height=220,
            fit=ft.ImageFit.CONTAIN,
            border_radius=18,
        )

        self.hero_container = ft.Container(
            content=self.main_image,
            width=260,
            height=260,
            alignment=ft.Alignment.CENTER,
            bgcolor="#1B1B26",
            border_radius=22,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=25,
                color="#00000055",
                offset=ft.Offset(0, 8),
            ),
            rotate=ft.Rotate(angle=0, alignment=ft.Alignment.CENTER),
            scale=1,
            animate_rotation=ft.Animation(duration=160, curve=ft.AnimationCurve.EASE_IN_OUT),
            animate_scale=ft.Animation(duration=140, curve=ft.AnimationCurve.EASE_IN_OUT),
        )

        self.status = ft.Text(
            "Нажми «Выстрел», чтобы начать",
            size=20,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )

        self.round = ft.Text(
            "Следующая камера: 1 / 6",
            size=16,
            color=ft.Colors.WHITE70,
        )

        self.bullets_label = ft.Text(
            "Заряжено патронов",
            size=16,
            color=ft.Colors.WHITE70,
        )

        self.hearts_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8)
        self.bullets_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        self.shoot_btn = ft.ElevatedButton(
            "Выстрел",
            width=180,
            height=48,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_700,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

        self.reset_btn = ft.OutlinedButton(
            "Перезарядка",
            width=180,
            height=48,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                side=ft.BorderSide(1, ft.Colors.WHITE30),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

        self.note = ft.Text(
            "Звук выстрела включён, если установлен пакет flet-audio",
            size=12,
            color=ft.Colors.WHITE54,
            text_align=ft.TextAlign.CENTER,
        )

        self.update_lives(self.max_lives)
        self.update_bullets()

    def _image(self, src: str, width: int = 36, height: int = 36):
        return ft.Image(src=src, width=width, height=height, fit=ft.ImageFit.CONTAIN)

    def update_lives(self, lives: int):
        self.hearts_row.controls = [
            self._image(
                "images/heart_full.png" if i < lives else "images/heart_empty.png",
                width=38,
                height=38,
            )
            for i in range(self.max_lives)
        ]

    def update_bullets(self):
        self.bullets_row.controls = [
            self._image("images/bullet.png", width=34, height=34)
            for _ in range(self.bullets_count)
        ]

    def set_main_image(self, src: str):
        self.main_image.src = src

    def build(self):
        return ft.Container(
            expand=True,
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#10131A", "#181C24", "#0D0F14"],
            ),
            content=ft.SafeArea(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=18,
                    controls=[
                        self.title,
                        self.subtitle,
                        self.hero_container,
                        self.status,
                        self.round,
                        ft.Text("Жизни", size=16, color=ft.Colors.WHITE70),
                        self.hearts_row,
                        self.bullets_label,
                        self.bullets_row,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=12,
                            controls=[self.shoot_btn, self.reset_btn],
                        ),
                        self.note,
                    ],
                )
            ),
        )
