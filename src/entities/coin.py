import pygame
from debugger import Debugger


class Coin:
    def __init__(
        self,
        screen: pygame.Surface,
        pos: pygame.Vector2,
        radius: int = 14,
        value: int = 1,
        velocity: float = 500.0,
        sprite: pygame.Surface | None = None,
    ):
        self.screen = screen
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.value = value
        self.velocity = velocity
        self.collected = False

        self.sprite = sprite
        if self.sprite is not None:
            self.sprite = pygame.transform.smoothscale(
                self.sprite, (2 * self.radius, 2 * self.radius)
            )

    def update(self, dt: float) -> None:
        self.pos.x -= self.velocity * dt

    def shouldKill(self) -> bool:
        return self.pos.x + self.radius <= 0 or self.collected

    def getHitbox(self):
        return self.pos, float(self.radius)

    def draw(self) -> None:
        if self.collected:
            return

        if self.sprite is not None:
            rect = self.sprite.get_rect(center=self.pos)
            self.screen.blit(self.sprite, rect)
        else:
            pygame.draw.circle(self.screen, "gold", self.pos, self.radius)

        if Debugger.HITBOXES:
            pygame.draw.circle(self.screen, "orange", self.pos, self.radius, 2)