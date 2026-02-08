import random
class RussianRouletteDuel:
    def __init__(self):
        self.chambers = [0, 0, 0, 0, 0, 1]
        random.shuffle(self.chambers)
        self.current_index = 0
        self.players = []
        self.turn_index = 0
        self.is_active = True

    def add_player(self, user_id: int, name: str) -> bool:
        if any(p["id"] == user_id for p in self.players):
            return False
        if len(self.players) >= 2:
            return False
        self.players.append({"id": user_id, "name": name})
        return True

    def is_ready(self) -> bool:
        return len(self.players) == 2

    def current_player(self):
        if not self.is_ready():
            return None
        return self.players[self.turn_index % 2]

    def other_player(self):
        if not self.is_ready():
            return None
        return self.players[(self.turn_index + 1) % 2]

    def shoot(self, user_id: int) -> str:
        if not self.is_active:
            return "game_over"
        if not self.is_ready():
            return "not_ready"
        if not any(p["id"] == user_id for p in self.players):
            return "not_in_game"

        cur = self.current_player()
        if cur["id"] != user_id:
            return "not_your_turn"

        result = self.chambers[self.current_index]
        self.current_index += 1

        if result == 1:
            self.is_active = False
            return "boom"

        self.turn_index += 1
        return "click"

    def stop(self):
        self.is_active = False
