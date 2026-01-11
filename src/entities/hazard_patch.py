import pygame
from debugger import Debugger


class HazardPatch:
    """
    A moving rectangular kill-zone (e.g. lava patch on the floor).
    Treated like an obstacle: moves left, collides via rect hitbox.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        velocity: float,
        color: str = "orangered3",
    ):
        self.screen = screen
        self.rect = rect
        self.velocity = float(velocity)
        self.color = color

    def update(self, dt: float) -> None:
        self.rect.x -= int(self.velocity * dt)

    def shouldKill(self) -> bool:
        return self.rect.right <= 0

    def getHitbox(self) -> pygame.Rect:
        return self.rect

    def draw(self) -> None:
        pygame.draw.rect(self.screen, self.color, self.rect)
        if Debugger.HITBOXES:
            pygame.draw.rect(self.screen, "yellow", self.rect, 2)
