import pygame
from debugger import Debugger


class RectObstacle:
    """
    Simple moving rectangle obstacle (for tunnel walls, beams, etc.)
    """
    def __init__(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        velocity: float = 500.0,
        color: str = "gray25",
        sprite: pygame.Surface | None = None,
    ):
        self.screen = screen
        self.rect = rect
        self.velocity = velocity
        self.color = color
        self.sprite = sprite
        if self.sprite is not None:
            self.sprite = pygame.transform.smoothscale(
                self.sprite, (self.rect.width, self.rect.height)
            )

    def update(self, dt: float) -> None:
        self.rect.x -= int(self.velocity * dt)

    def shouldKill(self) -> bool:
        return self.rect.right <= 0

    def getHitbox(self) -> pygame.Rect:
        return self.rect

    def draw(self) -> None:
        if self.sprite is not None:
            self.screen.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(self.screen, self.color, self.rect)

        if Debugger.HITBOXES:
            pygame.draw.rect(self.screen, "green", self.rect, 2)
