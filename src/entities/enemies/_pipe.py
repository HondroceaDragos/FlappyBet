import pygame
from enum import Enum

from debugger import Debugger


class Pipe:
    class Proportions(Enum):
        WIDTH = 110
        BASE_HEIGHT = 125

    class Orientation(Enum):
        TOP = "top"
        BOTTOM = "bottom"

    def __init__(
        self,
        screen: pygame.Surface,
        velocity: float,
        orientation: str,
        sprite: pygame.Surface,
        curr_pos: pygame.Vector2 | None = None,
        currPos: pygame.Vector2 | None = None,
        height: int | None = None,
        width: int | None = None,
    ):
        self.screen = screen
        self.velocity = float(velocity)

        pos = curr_pos if curr_pos is not None else currPos
        if pos is None:
            raise TypeError(
                "Pipe requires a position: pass curr_pos=... (or legacy currPos=...)"
            )
        self.curr_pos = pygame.Vector2(pos)

        if isinstance(orientation, Pipe.Orientation):
            self.orientation = orientation.value
        else:
            self.orientation = str(orientation).lower()

        self.width = int(width) if width is not None else Pipe.Proportions.WIDTH.value
        self.height = (
            int(height) if height is not None else Pipe.Proportions.BASE_HEIGHT.value
        )

        self.passed = False

        self.sprite = pygame.transform.smoothscale(sprite, (self.width, self.height))
        if self.orientation == Pipe.Orientation.TOP.value:
            self.sprite = pygame.transform.flip(self.sprite, False, True)

    def getHitbox(self) -> pygame.Rect:
        hitbox_scale_x = 0.55   # 75% of sprite width
        hitbox_scale_y = 0.90   # 90% of sprite heigh5

        hb_w = int(self.width * hitbox_scale_x)
        hb_h = int(self.height * hitbox_scale_y)

        offset_x = (self.width - hb_w) // 2
        offset_y = (self.height - hb_h) // 2

        return pygame.Rect(
            self.curr_pos.x + offset_x,
            self.curr_pos.y + offset_y,
            hb_w,
            hb_h,
        )

    def update(self, dt: float) -> None:
        self.curr_pos.x -= self.velocity * dt

    def shouldKill(self) -> bool:
        return self.curr_pos.x + self.width <= 0

    def draw(self) -> None:
        if Debugger.HITBOXES:
            pygame.draw.rect(self.screen, "green", self.getHitbox(), 2)

        rect = self.sprite.get_rect(topleft=self.curr_pos)
        self.screen.blit(self.sprite, rect)
