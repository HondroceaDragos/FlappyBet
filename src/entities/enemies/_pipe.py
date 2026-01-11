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
        BASE_HEIGHT = 125

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
        height=None
    ):
        self.screen = screen
        self.currPos = currPos
        self.velocity = velocity
        self.orientation = orientation

        self.width = Pipe.Proportions.WIDTH.value
        self.height = height if height is not None else Pipe.Proportions.BASE_HEIGHT.value

        self.sprite = pygame.transform.smoothscale(sprite, (self.width, self.height))

        if self.orientation == "top":
            self.sprite = pygame.transform.flip(self.sprite, False, True)

        self.passed = False

    @property
    def _hitbox(self):
        return pygame.Rect(
            self.currPos.x,
            self.currPos.y,
            self.width,
            self.height
        )

    def getHitbox(self) -> pygame.Rect:
        return self._hitbox

    def update(self, dt: float) -> None:
        self.currPos.x -= self.velocity * dt

    def shouldKill(self) -> bool:
        return self.currPos.x + self.width <= 0

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
