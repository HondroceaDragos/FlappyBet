import pygame

from entities import Player
from entities import Enemy

from core import PhysicsEngine

# ======================= #
########## TO DO ##########
# ======================= #

# !!!!!! Add an array of pipes !!!!!!
# Generalize magic numbers

### Notes ###
# None methods could have a return type (error checking)

def loadStates():
    states = {}

    states["mainMenu"] = "mainMenu"
    states["gameInProgress"] = "gameInProgress"

    return states

# 'GameMaster' class declaration and definition
class GameMaster:
    def __init__(self, screen = pygame.Surface,
                 player: Player = None,
                 engine: PhysicsEngine = None,
                 enemy: Enemy = None,
                 running: bool = False):
        self.screen = screen
        self.engine = engine


        self.running = running

        self.player = player
        self.enemy = enemy

        # Load all possible states into the master
        self.states = loadStates()
        self.currState = self.states["mainMenu"]

    # Action may cause game switches
    def _switchGameState(self, state: str) -> None:
        self.currState = self.states[state]

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

    # Reset game when state switching
    def _resetGame(self) -> None:
        self.player.currPos = pygame.Vector2(
                self.screen.get_width() / 2,
                self.screen.get_height() / 2
                )
        self.player.jumpPressed = False
        self.player.state = "IDLE"
        self.player.velocity = pygame.Vector2(0, 0)

        self.enemy.currPos = pygame.Vector2(self.screen.get_width() + 20, -20)

    # Updated event tracker - takes into account states
    def _eventTracker(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.currState == "mainMenu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self._switchGameState("gameInProgress")

            if self.currState == "gameInProgress":
                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_SPACE:
                            self.player.jumpPressed = True
                            self.engine.jump(self.player)
                        case pygame.K_ESCAPE:
                            self._switchGameState("mainMenu")

                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    self.player.jumpPressed = False
                
    # Interact with the env.
    def update(self):
        self._eventTracker()

        match self.currState:
            case "mainMenu":
                self._resetGame()

                self.screen.fill("white")
                mainMenuFont = pygame.font.Font(None, 128)
                mainMenuText = mainMenuFont.render("This will be the main menu!", True, "black")
                actionText = mainMenuFont.render("Press [SPACE] to start!", True, "black")
                self.screen.blit(mainMenuText, (0, 0))
                self.screen.blit(actionText, (0, 128))

            case "gameInProgress":
                self.screen.fill("white")

                # DO NOT REMOVE - important for state switching
                self.engine._clock.tick()

                self._updateEnv()
                self._updatePlayer()
                self._drawObjects()

                # Sanity check for collision
                if self.engine.checkCollision(self.player, self.enemy):
                    self.player.currPos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height())
                    self.player.velocity.y = 0