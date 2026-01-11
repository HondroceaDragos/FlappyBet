import pygame
from debugger import Debugger


class MineCart:
    """
    Lethal obstacle that rides the tunnel floor and moves left toward the player.
    Rect hitbox so it works with existing circle-rect collision.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        velocity: float,
        sprite: pygame.Surface | None = None,
    ):
        self.screen = screen
        self.rect = rect
        self.velocity = float(velocity)

        # For GameInProgressState logic: lethal obstacles kill on contact
        self.lethal = True

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
            # fallback look: dark cart body + small highlight
            pygame.draw.rect(self.screen, "gray20", self.rect, border_radius=6)
            highlight = self.rect.inflate(-self.rect.width * 0.25, -self.rect.height * 0.45)
            pygame.draw.rect(self.screen, "gray35", highlight, border_radius=5)

        if Debugger.HITBOXES:
            pygame.draw.rect(self.screen, "red", self.rect, 2)
