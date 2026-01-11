import random
import pygame
from entities import RectObstacle, Coin


def _load_coin_sprite():
    try:
        return pygame.image.load("../assets/sprites/coins/coin.png").convert_alpha()
    except Exception:
        return None


class TunnelSpawner:
    """
    Classic Flappy-style tunnel:
    - spawns TOP+BOTTOM walls as a pair at pipe-like intervals
    - the gap center varies gradually (like Flappy Bird)
    - coins lightly guide the middle
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.coin_sprite = _load_coin_sprite()

        self.spawn_timer = 0.0
        self.spawn_rate = 0.85

        self.base_velocity = 520.0
        self.gap = 220

        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

        # smoothing factor (0..1): higher = follows target faster
        self.center_smoothing = 0.25

    def reset(self) -> None:
        self.spawn_timer = 0.0
        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))
        self.base_velocity = 520.0 + tier * 30.0
        self.spawn_rate = max(0.55, 0.85 - tier * 0.02)
        self.gap = max(140, 220 - tier * 10)

        # slightly faster tracking at higher difficulty
        self.center_smoothing = min(0.40, 0.25 + tier * 0.01)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.spawn_rate

    def _pick_next_center(self):
        H = self.screen.get_height()
        margin = 100
        min_c = margin + self.gap // 2
        max_c = (H - margin) - self.gap // 2

        # Flappy-like variation: don't teleport the gap too far
        step = random.randint(-140, 140)
        new_target = int(self.target_center + step)
        self.target_center = max(min_c, min(max_c, new_target))

        # Smoothly move current center toward target
        self.gap_center = int(
            self.gap_center + (self.target_center - self.gap_center) * self.center_smoothing
        )

    def spawn(self, tier: int) -> tuple[list[RectObstacle], list[Coin]]:
        self.setDifficultyTier(tier)
        self._pick_next_center()

        W = self.screen.get_width()
        H = self.screen.get_height()

        x = W + 20
        seg_w = 110  # pipe-like width; looks/feels like Flappy

        top_h = max(0, self.gap_center - self.gap // 2)
        bot_y = self.gap_center + self.gap // 2
        bot_h = max(0, H - bot_y)

        obstacles = [
            RectObstacle(
                self.screen,
                pygame.Rect(x, 0, seg_w, top_h),
                velocity=self.base_velocity,
                color="slategray4",
            ),
            RectObstacle(
                self.screen,
                pygame.Rect(x, bot_y, seg_w, bot_h),
                velocity=self.base_velocity,
                color="slategray4",
            ),
        ]

        coins: list[Coin] = []
        # Keep tunnel coins sparse and readable: 25% chance, 1 coin in the center
        if random.random() < 0.25:
            coins.append(
                Coin(
                    screen=self.screen,
                    pos=pygame.Vector2(x + seg_w + 85, self.gap_center),
                    radius=13,
                    value=1,
                    velocity=self.base_velocity,
                    sprite=self.coin_sprite,
                )
            )

        self.spawn_timer = 0.0
        return obstacles, coins
