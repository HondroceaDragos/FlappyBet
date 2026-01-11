import pygame
from debugger import Debugger


class RectObstacle:
    """
    Moving rectangle obstacle.

    lethal=True  -> touching kills (spikes, lava, beams)
    lethal=False -> solid surface (tunnel walls you can rest against)
    """
    def __init__(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        velocity: float = 500.0,
        color: str = "gray25",
        sprite: pygame.Surface | None = None,
        lethal: bool = True,
    ):
        self.screen = screen
        self.rect = rect
        self.velocity = float(velocity)
        self.color = color
        self.sprite = sprite
        self.lethal = bool(lethal)

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
            # green = lethal, blue = walkable solid
            outline = "green" if self.lethal else "dodgerblue"
            pygame.draw.rect(self.screen, outline, self.rect, 2)
