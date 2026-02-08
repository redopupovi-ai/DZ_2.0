import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from core.roulette import RussianRouletteDuel

class BotHandlers:
    def __init__(self, bot):
        self.router = Router()
        self.bot = bot

        self.roulette_games = {}
        self.roulette_timers = {}
        self.TURN_SECONDS = 5

        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_command, Command("start"))
        self.router.message.register(self.start_roulette, Command("roulette"))
        self.router.message.register(self.shoot_roulette, Command("shoot"))
        self.router.message.register(self.stop_roulette, Command("stop"))

    async def start_command(self, message: types.Message):
        await message.answer(
            "Команды:\n"
            "/roulette — добавить игрока\n"
            "/shoot — выстрел\n"
            "/stop — остановить"
        )

    async def start_roulette(self, message: types.Message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        name = (message.from_user.full_name or "Игрок").strip()

        game = self.roulette_games.get(chat_id)
        if not game or not game.is_active:
            game = RussianRouletteDuel()
            self.roulette_games[chat_id] = game

        added = game.add_player(user_id, name)
        if not added:
            if any(p["id"] == user_id for p in game.players):
                await message.answer("Ты уже в игре. Жми /shoot когда твоя очередь.")
            else:
                await message.answer("Уже 2 игрока. /stop чтобы начать заново.")
            return

        if not game.is_ready():
            await message.answer(
                f"Игрок добавлен: {name}\n"
                "Ждём второго игрока: пусть напишет /roulette"
            )
            return

        cur = game.current_player()["name"]
        p1, p2 = game.players[0]["name"], game.players[1]["name"]

        await message.answer(
            f"Игра началась: {p1} vs {p2}\n"
            f"Ходит: {cur}\n"
            f"Время на выстрел: {self.TURN_SECONDS} сек\n"
            "Стрелять: /shoot"
        )
        await self._start_turn_timer(chat_id)

    async def shoot_roulette(self, message: types.Message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        game = self.roulette_games.get(chat_id)
        if not game or not game.is_active:
            await message.answer("Нет игры. /roulette")
            return

        if not game.is_ready():
            await message.answer("Нужно 2 игрока. Второй пишет /roulette")
            return

        await self._cancel_timer(chat_id)

        result = game.shoot(user_id)

        if result == "not_in_game":
            await message.answer("Ты не в игре. /stop и /roulette")
            await self._start_turn_timer(chat_id)
            return

        if result == "not_your_turn":
            cur = game.current_player()["name"]
            await message.answer(f"Не твой ход. Ходит: {cur}")
            await self._start_turn_timer(chat_id)
            return

        shooter = next(p["name"] for p in game.players if p["id"] == user_id)

        if result == "click":
            nxt = game.current_player()["name"]
            await message.answer(
                f"{shooter}: щёлк (пусто)\n"
                f"Следующий ход: {nxt} ({self.TURN_SECONDS} сек)"
            )
            await self._start_turn_timer(chat_id)
            return

        if result == "boom":
            winner = game.other_player()["name"]
            await message.answer(f"{shooter}: БАХ (патрон)\nПобедил: {winner}")
            await self._end_game(chat_id)
            return

        await message.answer("Ошибка состояния. /stop")
        await self._start_turn_timer(chat_id)

    async def stop_roulette(self, message: types.Message):
        chat_id = message.chat.id
        game = self.roulette_games.get(chat_id)

        if not game or not game.is_active:
            await message.answer("Игры нет.")
            return

        game.stop()
        await message.answer("Игра остановлена.")
        await self._end_game(chat_id)

    async def _cancel_timer(self, chat_id: int):
        task = self.roulette_timers.get(chat_id)
        if task and not task.done():
            task.cancel()
        self.roulette_timers.pop(chat_id, None)

    async def _start_turn_timer(self, chat_id: int):
        game = self.roulette_games.get(chat_id)
        if not game or not game.is_active or not game.is_ready():
            return

        await self._cancel_timer(chat_id)
        expected_turn = game.turn_index

        async def job():
            try:
                await asyncio.sleep(self.TURN_SECONDS)
                g = self.roulette_games.get(chat_id)
                if not g or not g.is_active or not g.is_ready():
                    return
                if g.turn_index != expected_turn:
                    return

                loser = g.current_player()["name"]
                winner = g.other_player()["name"]

                await self.bot.send_message(
                    chat_id,
                    f"Время вышло! Проиграл: {loser}. Победил: {winner}"
                )
                await self._end_game(chat_id)
            except asyncio.CancelledError:
                return

        self.roulette_timers[chat_id] = asyncio.create_task(job())

    async def _end_game(self, chat_id: int):
        await self._cancel_timer(chat_id)
        self.roulette_games.pop(chat_id, None)
