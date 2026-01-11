import random
import pygame
from entities import RectObstacle, Coin


def _load_coin_sprite():
    try:
        return pygame.image.load("../assets/sprites/coins/coin.png").convert_alpha()
    except Exception:
        return None


class BeamsSpawner:
    """
    Mine support beams / frames:
    - spawns at spikes-like pacing (more spaced out)
    - leaves a clear opening (classic readable gameplay)
    - coin-light
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.coin_sprite = _load_coin_sprite()

        self.spawn_timer = 0.0

        self.spawn_rate = 1.20
        self.base_velocity = 500.0

        self.opening = 280

    def reset(self) -> None:
        self.spawn_timer = 0.0

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))

        self.base_velocity = 510.0 + tier * 28.0
        self.spawn_rate = max(0.55, 0.85 - tier * 0.03)
        self.opening = max(150, 240 - tier * 8)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.spawn_rate

    def spawn(self, tier: int):
        self.setDifficultyTier(tier)

        W = self.screen.get_width()
        H = self.screen.get_height()

        x = W + 20
        frame_w = 90
        beam_thick = 40

        margin = 120
        center = random.randint(margin, H - margin)

        opening_top = max(beam_thick, center - self.opening // 2)
        opening_bot = min(H - beam_thick, center + self.opening // 2)

        top = RectObstacle(
            self.screen,
            pygame.Rect(x, 0, frame_w, opening_top),
            velocity=self.base_velocity,
            color="sienna4",
        )
        bot = RectObstacle(
            self.screen,
            pygame.Rect(x, opening_bot, frame_w, H - opening_bot),
            velocity=self.base_velocity,
            color="sienna4",
        )

        obstacles = [top, bot]

        coins = []
        if random.random() < 0.35:
            mid_y = (opening_top + opening_bot) // 2
            coins.append(
                Coin(
                    screen=self.screen,
                    pos=pygame.Vector2(x + frame_w + 80, mid_y),
                    radius=13,
                    value=1,
                    velocity=self.base_velocity,
                    sprite=self.coin_sprite,
                )
            )

        self.spawn_timer = 0.0
        return obstacles, coins
