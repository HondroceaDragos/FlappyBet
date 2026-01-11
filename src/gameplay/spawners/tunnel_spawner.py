import random
import pygame
from entities import RectObstacle


class TunnelSpawner:
    """
    Walkable continuous tunnel:
    - spawns frequent thin wall slices (top + bottom) => continuous corridor
    - walls are SOLID but NOT lethal (player can touch/stand on them)
    - corridor center drifts smoothly (no abrupt jumps)
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.spawn_timer = 0.0
        self.slice_rate = 0.12      # dense => continuous tunnel look
        self.slice_width = 50       # small width => smooth corridor

        self.base_velocity = 520.0
        self.gap = 240              # generous early

        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

        self.target_timer = 0.0
        self.target_interval = 0.60  # how often we adjust direction
        self.follow = 0.10           # smoothing factor

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.target_timer = 0.0
        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))

        self.base_velocity = 520.0 + tier * 26.0
        self.slice_rate = max(0.09, 0.12 - tier * 0.003)
        self.gap = max(160, 240 - tier * 8)

        # slightly more motion later, but still smooth
        self.target_interval = max(0.42, 0.60 - tier * 0.01)
        self.follow = min(0.16, 0.10 + tier * 0.004)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        self.target_timer += dt

        H = self.screen.get_height()
        margin = 80

        # occasionally choose a new target center (bounded, non-abrupt)
        if self.target_timer >= self.target_interval:
            self.target_timer = 0.0

            min_c = margin + self.gap // 2
            max_c = (H - margin) - self.gap // 2

            # small step -> prevents teleporting the tunnel
            step = random.randint(-140, 140)
            self.target_center = max(min_c, min(max_c, self.target_center + step))

        # smooth drift
        self.gap_center = int(self.gap_center + (self.target_center - self.gap_center) * self.follow)

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.slice_rate

    def spawn(self, tier: int):
        self.setDifficultyTier(tier)

        W = self.screen.get_width()
        H = self.screen.get_height()
        x = W + 20

        top_h = max(0, self.gap_center - self.gap // 2)
        bot_y = self.gap_center + self.gap // 2
        bot_h = max(0, H - bot_y)

        # Non-lethal SOLID walls
        top_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, 0, self.slice_width, top_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )
        bottom_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, bot_y, self.slice_width, bot_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )

        self.spawn_timer = 0.0
        return [top_wall, bottom_wall], []
