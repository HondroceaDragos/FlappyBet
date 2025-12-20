import pygame
from enum import Enum

from debugger import Debugger

# ============================= #
############# TO DO #############
# ============================= #

# Add difficulty scalling
# Untine sprite scalling from hitbox


# 'Pipe' class declaration and definition
class Pipe:
    # Proportions constants
    class Proportions(Enum):
        WIDTH = 110
        HEIGHT = 125

    # Where pipes should spawn
    class RelativeOrientation(Enum):
        TOP = "top"
        BOT = "bottom"

    def __init__(
        self,
        screen: pygame.Surface,
        currPos: pygame.Vector2,
        velocity: float,
        orientation,
        sprite,
    ):
        self.screen = screen

        self.currPos = currPos
        self.velocity = velocity

        # Factory decides orientation
        self.orientation = orientation

        self.sprite = sprite

        # Rotate sprite to match orientation
        if self.orientation == "top":
            self.sprite = pygame.transform.flip(self.sprite, False, True)

    @property
    def _hitbox(self):
        return pygame.Rect(
            self.currPos.x,
            self.currPos.y,
            Pipe.Proportions.WIDTH.value,
            Pipe.Proportions.HEIGHT.value,
        )

    def getHitbox(self) -> pygame.Rect:
        return self._hitbox

    def update(self, dt: float) -> None:
        self.currPos.x -= self.velocity * dt

    def shouldKill(self) -> bool:
        return self.currPos.x + Pipe.Proportions.WIDTH.value <= 0

    # Display method
    def draw(self):
        # Draw hitbox
        if Debugger.HITBOXES:
            pygame.draw.rect(
                self.screen,
                "green",
                (
                    self.currPos.x,
                    self.currPos.y,
                    Pipe.Proportions.WIDTH.value,
                    Pipe.Proportions.HEIGHT.value,
                ),
                2,
            )

        # Draw sprite
        rect = self.sprite.get_rect(topleft=self.currPos)
        self.screen.blit(self.sprite, rect)
