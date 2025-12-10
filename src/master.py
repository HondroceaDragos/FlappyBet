import pygame

from player import Player
from enemy import Enemy
from engine import PhysicsEngine
from sound import SoundManager

# ======================= #
########## TO DO ##########
# ======================= #

# !!!!!! Add an array of pipes !!!!!!
# Generalize magic numbers

### Notes ###
# None methods could have a return type (error checking)

# 'GameMaster' class declaration and definition
class GameMaster:
    def __init__(self, screen = pygame.Surface,
                 player: Player = None,
                 engine: PhysicsEngine = None,
                 enemy: Enemy = None,
                 running: bool = False):
        self.screen = screen
        self.player = player
        self.engine = engine
        self.running = running
        self.dir = pygame.Vector2(0, 0)
        self.enemy = enemy

        self.music = SoundManager()
        self.music.playBgkMusic("./song.mp3")

    def _drawObjects(self) -> None:
        self.player.draw()
        self.enemy.draw()

    def _updateEnv(self) -> None:
        self.engine.updateDt()
        self.engine.applyGravity(self.player)
        self.enemy.update()

    # Call animation engine
    def _updatePlayer(self) -> None:
        self.player.decideState()
        self.player.animatePlayer()

    def _eventTracker(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.jumpPressed = True
                self.engine.jump(self.player)
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.player.jumpPressed = False
                
    # Interact with the env.
    def update(self):
        self._drawObjects()
        self._updatePlayer()
        self._updateEnv()
        self._eventTracker()

        # Sanity check for collision
        if self.engine.checkCollision(self.player, self.enemy):
            self.player.currPos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height())
            self.player.velocity.y = 0