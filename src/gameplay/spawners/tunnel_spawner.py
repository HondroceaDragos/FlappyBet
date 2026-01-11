import random
import pygame
from entities import RectObstacle


class TunnelSpawner:
    """
    Walkable continuous tunnel:
    - spawns wide overlapping wall segments => solid look
    - walls are SOLID but NOT lethal (walkable)
    - corridor center drifts smoothly (no abrupt jumps)
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.spawn_timer = 0.0

        self.base_velocity = 520.0
        self.gap = 240

        # Wider panels to look solid
        self.panel_width = 160
        self.overlap_px = 3  # overlap to hide seams
        self.panel_rate = 0.20  # chosen so panels overlap at typical speed

        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

        self.target_timer = 0.0
        self.target_interval = 0.60
        self.follow = 0.10

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.target_timer = 0.0
        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))

        self.base_velocity = 520.0 + tier * 26.0
        self.gap = max(160, 240 - tier * 8)

        # keep it solid-looking at higher speeds: spawn a bit faster
        self.panel_rate = max(0.14, 0.20 - tier * 0.004)

        self.target_interval = max(0.42, 0.60 - tier * 0.01)
        self.follow = min(0.16, 0.10 + tier * 0.004)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        self.target_timer += dt

        H = self.screen.get_height()
        margin = 80

        if self.target_timer >= self.target_interval:
            self.target_timer = 0.0

            min_c = margin + self.gap // 2
            max_c = (H - margin) - self.gap // 2

            step = random.randint(-140, 140)
            self.target_center = max(min_c, min(max_c, self.target_center + step))

        self.gap_center = int(self.gap_center + (self.target_center - self.gap_center) * self.follow)

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.panel_rate

    def spawn(self, tier: int):
        self.setDifficultyTier(tier)

        W = self.screen.get_width()
        H = self.screen.get_height()

        # overlap the next segment slightly so it looks continuous
        x = W + 20 - self.overlap_px

        top_h = max(0, self.gap_center - self.gap // 2)
        bot_y = self.gap_center + self.gap // 2
        bot_h = max(0, H - bot_y)

        top_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, 0, self.panel_width + self.overlap_px, top_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )
        bottom_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, bot_y, self.panel_width + self.overlap_px, bot_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )

        self.spawn_timer = 0.0
        return [top_wall, bottom_wall], []
