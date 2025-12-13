import pygame

# ======================= #
########## TO DO ##########
# ======================= #

# Generalize magic numbers
# Get the flying feeling just right

### Notes ###
# 'draw' method could have a return type (error checking)

from entities import Player
from entities import Enemy

# 'Engine' declaration and definition
class PhysicsEngine:
    # Fields specifically declared for access modifiers (private)
    _dt: float = 0
    _clock = pygame.time.Clock()

    def __init__(self, screen = pygame.Surface,
                 dt: float = 0,
                 frameRate: int = 0):
        self.screen = screen
        self._dt = dt
        self._frameRate = frameRate

    # Game is capped at 60 fps
    def updateDt(self) -> None:
        self._dt = self._clock.tick(self._frameRate) / 1000

    # Private method for out of bounds resets
    def _clampPlayer(self, player: Player) -> None:
        player.currPos.y = round(player.currPos.y)

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
    def _circToRectCol(self, circleCenter: pygame.Vector2,
                       circleRadius: float,
                       rect: pygame.Rect) -> bool:
        dx = circleCenter.x - max(rect.left, min(circleCenter.x, rect.right))
        dy = circleCenter.y - max(rect.top, min(circleCenter.y, rect.bottom))

        return (dx * dx + dy * dy) < (circleRadius * circleRadius)

    # Handle collisions - should we store hitboxes in the class?
    def checkCollision(self, player: Player, enemy: Enemy) -> bool:
        # Player 'hitbox'
        playerCenter, playerRadius = player.getHitbox()

        # Enemy 'hitbox'
        enemyHitbox = enemy.getHitbox()

        return self._circToRectCol(playerCenter, playerRadius, enemyHitbox)
