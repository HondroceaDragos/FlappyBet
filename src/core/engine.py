import pygame

# ======================= #
########## TO DO ##########
# ======================= #

# Generalize magic numbers
# Get the flying feeling just right

### Notes ###
# 'draw' method could have a return type (error checking)

from entities import Player
from entities import Pipe


# 'Engine' declaration and definition
class PhysicsEngine:
    # Fields specifically declared for access modifiers (private)
    _dt: float = 0
    _clock = pygame.time.Clock()

    def __init__(self, screen=pygame.Surface, dt: float = 0):
        self.screen = screen
        self._dt = dt

    # Game is capped at 60 fps
    def updateDt(self) -> None:
        self._dt = self._clock.tick() / 1000

    def resetClock(self) -> None:
        self._clock.tick()
        self._dt = 0

    # Private method for out of bounds resets
    def _clampPlayer(self, player: Player) -> None:
        # player.currPos.y = round(player.currPos.y)

        # Down
        if player.currPos.y > self.screen.get_height() - player._radius:
            player.currPos.y = self.screen.get_height() - player._radius
            if player.velocity.y > 0:
                player.velocity.y = 0
        # Up
        if player.currPos.y < player._radius:
            player.currPos.y = player._radius
            if player.velocity.y < 0:
                player.velocity.y = 0

    # Public* method for gravity simulation
    def applyGravity(self, player: Player) -> None:
        if player.currPos.y != self.screen.get_height() + player._radius:
            player.velocity.y += 9.81 * self._dt * 95
            player.currPos.y += player.velocity.y * self._dt * 2
        self._clampPlayer(player)

    # Flight simulation
    def jump(self, player: Player) -> None:
        player.velocity.y = -355
        self._clampPlayer(player)

    # Define a collision method for circle - to - rectangle
    def _circToRectCol(
        self, circleCenter: pygame.Vector2, circleRadius: float, rect: pygame.Rect
    ) -> bool:
        dx = circleCenter.x - max(rect.left, min(circleCenter.x, rect.right))
        dy = circleCenter.y - max(rect.top, min(circleCenter.y, rect.bottom))

        return (dx * dx + dy * dy) < (circleRadius * circleRadius)

    def resolveSolidCircleRect(self, player: Player, rect: pygame.Rect) -> None:
        """
        Resolve collision between player's circle and a solid rectangle.
        Used for walkable tunnel surfaces (non-lethal walls).
        We push the player out along the shallow axis.
        """
        center, radius = player.getHitbox()

        # Find closest point on rect to circle center
        closest_x = max(rect.left, min(center.x, rect.right))
        closest_y = max(rect.top, min(center.y, rect.bottom))

        dx = center.x - closest_x
        dy = center.y - closest_y
        dist2 = dx * dx + dy * dy

        if dist2 >= radius * radius:
            return  # no overlap

        # If exactly inside edge (dx=dy=0), choose a direction based on proximity
        if dx == 0 and dy == 0:
            # push vertically by default (tunnel surfaces are vertical blocks)
            if center.y < rect.centery:
                dy = -1
            else:
                dy = 1

        # Determine whether to resolve vertically or horizontally
        # Prefer vertical resolution (feels like "standing" on surfaces)
        # but still handle side impacts.
        overlap_x = radius - abs(dx) if dx != 0 else radius
        overlap_y = radius - abs(dy) if dy != 0 else radius

        if overlap_y <= overlap_x:
            # Resolve vertically
            if center.y < rect.centery:
                # player above rect -> push up
                player.currPos.y = rect.top - radius
                if player.velocity.y > 0:
                    player.velocity.y = 0
            else:
                # player below rect -> push down
                player.currPos.y = rect.bottom + radius
                if player.velocity.y < 0:
                    player.velocity.y = 0
        else:
            # Resolve horizontally
            if center.x < rect.centerx:
                player.currPos.x = rect.left - radius
            else:
                player.currPos.x = rect.right + radius
            # (we don't track player x-velocity in your game; keep as positional correction)

    # Handle collisions - should we store hitboxes in the class?
    def checkCollision(self, player: Player, enemy: Pipe) -> bool:
        # Player 'hitbox'
        playerCenter, playerRadius = player.getHitbox()

        # Enemy 'hitbox'
        enemyHitbox = enemy.getHitbox()

        return self._circToRectCol(playerCenter, playerRadius, enemyHitbox)
