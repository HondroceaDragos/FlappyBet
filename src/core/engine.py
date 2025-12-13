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

    # Private method for gravity simulation
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
    def _circToRectCol(self, circleBox: pygame.Vector2,
                       radius: float,
                       rect: pygame.Rect) -> bool:
        dx = circleBox.x - max(rect.left, min(circleBox.x, rect.right))
        dy = circleBox.y - max(rect.top, min(circleBox.y, rect.bottom))

        return (dx * dx + dy * dy) < (radius * radius)

    # Handle collisions
    def checkCollision(self, player: Player, enemy: Enemy) -> bool:
        # With an enemy - pipe
        enemyHitbox = pygame.Rect(enemy.currPos.x, enemy.currPos.y, 70, 200)

        # 'Player' hitbox
        return self._circToRectCol(player.currPos, player._radius, enemyHitbox)
