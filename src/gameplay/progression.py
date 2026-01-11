import math
import pygame


class Progression:
    """
    Global progression:
    - increases hazard intensity over time + coins
    - spawners use intensity to spawn more lava patches, etc.
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.time_alive = 0.0
        self.coins_collected = 0

        # 0..1
        self.hazard_intensity = 0.0

    def reset(self) -> None:
        self.time_alive = 0.0
        self.coins_collected = 0
        self.hazard_intensity = 0.0

    def addCoins(self, n: int) -> None:
        self.coins_collected += int(n)

    def update(self, dt: float) -> None:
        self.time_alive += dt

        # Smooth ramp based on time; coins accelerate slightly
        accel = min(0.6, self.coins_collected / 120.0)
        t = (self.time_alive / 55.0) * (1.0 + accel)

        # hazard_intensity goes 0 -> ~1 smoothly
        self.hazard_intensity = 1.0 - math.exp(-t)
        self.hazard_intensity = max(0.0, min(1.0, self.hazard_intensity))
