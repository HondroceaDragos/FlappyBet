import pygame
from debugger import Debugger


class MineCart:
    """
    Lethal obstacle that rides the tunnel floor using gravity + floor constraint.
    Additionally, detects step-ups ahead and "crashes" (despawns) instead of phasing.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        velocity: float,
        sprite: pygame.Surface | None = None,
        gravity: float = 2200.0,  # px/s^2
    ):
        self.screen = screen
        self.rect = rect

        # Horizontal speed (px/s). May be > tunnel speed.
        self.vx = float(velocity)

        # Vertical physics
        self.vy = 0.0
        self.gravity = float(gravity)

        # Contract used by GameInProgressState: lethal => death on collision
        self.lethal = True

        # Injected floor field (TunnelField)
        self.floor_field = None

        # If ground in front rises too sharply, cart cannot climb => despawn/crash
        self.dead = False
        self.step_threshold = 10  # pixels of rise between center and front considered a "wall"

        self.sprite = sprite
        if self.sprite is not None:
            self.sprite = pygame.transform.smoothscale(
                self.sprite, (self.rect.width, self.rect.height)
            )

    def attach_floor_field(self, field) -> None:
        self.floor_field = field

    def _floor_y(self) -> float | None:
        if self.floor_field is None:
            return None
        return float(self.floor_field.floor_y_at(self.rect.centerx))

    def update(self, dt: float) -> None:
        if self.dead:
            return

        # Move left
        self.rect.x -= int(self.vx * dt)

        # Apply vertical physics
        self.vy += self.gravity * dt
        self.rect.y += int(self.vy * dt)

        if self.floor_field is None:
            return

        # Constrain to floor (ride it)
        fy = float(self.floor_field.floor_y_at(self.rect.centerx))
        if self.rect.bottom > fy:
            self.rect.bottom = int(fy)
            self.vy = 0.0

        # Step-ahead detection: if the floor in front is higher than current by threshold, crash/despawn
        fy_center = float(self.floor_field.floor_y_at(self.rect.centerx))
        fy_front = float(self.floor_field.floor_y_at(self.rect.right))

        # floor_y smaller => higher ground
        if (fy_center - fy_front) > self.step_threshold:
            self.dead = True

    def shouldKill(self) -> bool:
        return self.dead or (self.rect.right <= 0)

    def getHitbox(self) -> pygame.Rect:
        return self.rect

    def draw(self) -> None:
        if self.sprite is not None:
            self.screen.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(self.screen, "gray20", self.rect, border_radius=6)
            highlight = self.rect.inflate(
                -self.rect.width * 0.25, -self.rect.height * 0.45
            )
            pygame.draw.rect(self.screen, "gray35", highlight, border_radius=5)

        if Debugger.HITBOXES:
            pygame.draw.rect(self.screen, "red", self.rect, 2)
