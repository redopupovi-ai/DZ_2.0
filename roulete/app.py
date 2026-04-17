import asyncio
from pathlib import Path

import flet as ft

from game import Game
from ui import UI

try:
    import flet_audio as fta
except ImportError:
    fta = None


class RouletteApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Русская рулетка"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.padding = 0

        if self.page.window is not None:
            self.page.window.width = 520
            self.page.window.height = 760
            self.page.window.resizable = False

        self.game = Game(chambers=6, bullets_count=2, max_lives=3)
        self.ui = UI(max_lives=self.game.max_lives, bullets_count=self.game.bullets_count)
        self._busy = False

        self.shot_audio = None
        self._setup_audio()
        self.bind_events()
        self.refresh_ui()
        self.page.add(self.ui.build())

    def _setup_audio(self):
        if fta is None:
            self.ui.note.value = "Для звука установи пакет: pip install flet-audio"
            return

        sound_path = Path(__file__).parent / "assets" / "sounds" / "shot.wav"
        if not sound_path.exists():
            self.ui.note.value = "Файл sounds/shot.wav не найден"
            return

        self.shot_audio = fta.Audio(src="sounds/shot.wav", autoplay=False, volume=1.0)
        self.page.services.append(self.shot_audio)
        self.ui.note.value = "Звук выстрела активен"

    def bind_events(self):
        self.ui.shoot_btn.on_click = self.shoot
        self.ui.reset_btn.on_click = self.restart

    def refresh_ui(self):
        self.ui.round.value = f"Следующая камера: {self.game.current_position} / {self.game.chambers}"
        self.ui.update_lives(self.game.lives)
        self.ui.update_bullets()
        self.ui.shoot_btn.disabled = not self.game.alive or self._busy

    async def play_shot_sound(self):
        if self.shot_audio is None:
            return
        try:
            await self.shot_audio.play()
        except Exception:
            self.ui.note.value = "Не удалось воспроизвести звук. Проверь flet-audio и локальный аудиофайл."
            self.page.update()

    async def animate_shot(self, hit: bool):
        self._busy = True
        self.refresh_ui()
        self.page.update()

        animation_steps = [0.2, 0.55, 0.95, 1.35]
        scales = [1.05, 1.12, 1.18, 1.06]

        for index, angle in enumerate(animation_steps):
            self.ui.hero_container.rotate = ft.Rotate(angle=angle, alignment=ft.Alignment.CENTER)
            self.ui.hero_container.scale = scales[index]
            self.page.update()

            if index == 1:
                await self.play_shot_sound()

            await asyncio.sleep(0.08)

        self.ui.set_main_image("images/fire.png" if hit else "images/smoke.png")
        self.ui.hero_container.scale = 1.22 if hit else 1.12
        self.page.update()
        await asyncio.sleep(0.14)

        self.ui.set_main_image("images/revolver.png")
        self.ui.hero_container.rotate = ft.Rotate(angle=0, alignment=ft.Alignment.CENTER)
        self.ui.hero_container.scale = 1
        self._busy = False
        self.refresh_ui()
        self.page.update()

    async def shoot(self, e):
        if not self.game.alive or self._busy:
            return

        result = self.game.shot()
        await self.animate_shot(hit=result["hit"])

        if result["state"] == "dead":
            self.ui.status.value = "BOOM! Жизни закончились"
            self.ui.status.color = ft.Colors.RED_400
            self.refresh_ui()
            self.page.update()
            self.show_dialog("Игра окончена", "Ты проиграл. Нажми «Перезарядка», чтобы начать заново.")
            return

        if result["state"] == "hit":
            text = f"Попадание! Осталось жизней: {self.game.lives}"
            color = ft.Colors.ORANGE_300
        else:
            text = "Щелчок... пусто. Повезло!"
            color = ft.Colors.GREEN_300

        if result["respun"]:
            text += " Барабан прокручен заново."

        self.ui.status.value = text
        self.ui.status.color = color
        self.refresh_ui()
        self.page.update()

    async def restart(self, e):
        if self._busy:
            return

        self.game.reset()
        self.ui.status.value = "Нажми «Выстрел», чтобы начать"
        self.ui.status.color = ft.Colors.WHITE
        self.ui.set_main_image("images/revolver.png")
        self.ui.hero_container.rotate = ft.Rotate(angle=0, alignment=ft.Alignment.CENTER)
        self.ui.hero_container.scale = 1
        self.refresh_ui()
        self.page.update()

    def show_dialog(self, title: str, message: str):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
