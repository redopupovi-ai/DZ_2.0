import random


class Game:
    def __init__(self, chambers: int = 6, bullets_count: int = 2, max_lives: int = 3):
        self.chambers = chambers
        self.bullets_count = bullets_count
        self.max_lives = max_lives
        self.reset()

    def reset(self):
        self.current_position = 1
        self.lives = self.max_lives
        self.alive = True
        self.spin_drum()

    def spin_drum(self):
        self.bullet_positions = set(
            random.sample(range(1, self.chambers + 1), self.bullets_count)
        )

    def shot(self) -> dict:
        if not self.alive:
            return {
                "state": "game_over",
                "hit": False,
                "lives": self.lives,
                "position": self.current_position,
                "respun": False,
            }

        chamber = self.current_position
        hit = chamber in self.bullet_positions

        if hit:
            self.lives -= 1
            if self.lives <= 0:
                self.alive = False
                return {
                    "state": "dead",
                    "hit": True,
                    "lives": self.lives,
                    "position": chamber,
                    "respun": False,
                }
            state = "hit"
        else:
            state = "empty"

        self.current_position += 1
        respun = False

        if self.current_position > self.chambers:
            self.current_position = 1
            self.spin_drum()
            respun = True

        return {
            "state": state,
            "hit": hit,
            "lives": self.lives,
            "position": chamber,
            "respun": respun,
        }
