import pygame

from entities import Player

from core import PhysicsEngine
from core import MainMenuState
from core import GameInProgressState
from core import PauseMenuState
from core import GameOverState
from core import SlotsState

from sound import SoundManager
from config import SettingsManager

from gameplay.section_manager import SectionManager
from gameplay.progression import Progression


class GameMaster:
    def __init__(
        self,
        screen: pygame.Surface,
        engine: PhysicsEngine = None,
        player: Player = None,
        sound: SoundManager = None,
        running: bool = False,
    ):
        self.screen = screen
        self.engine = engine

        self.player = player
        self.sound = sound

        # Obstacles & collectibles
        self.pipes = []   # now: obstacles list (Pipe + RectObstacle)
        self.coins = []

        # Score is coin-based now
        self.score = 0

        # New systems
        self.section_manager = SectionManager(self.screen)
        self.progression = Progression(self.screen)

        self.running = running

        self.states = {
            "mainMenu": MainMenuState(self),
            "gameInProgress": GameInProgressState(self),
            "pauseMenu": PauseMenuState(self),
            "slots": SlotsState(self),
            "gameOver": GameOverState(self),
            
        }

        self._currState = None
        self.switchGameState("mainMenu")
        self.isPaused = False

    def switchGameState(self, state: str) -> None:
        if self._currState is self.states.get(state):
            return
        if self._currState:
            self._currState.onExit()
        self._currState = self.states[state]
        self._currState.onEnter()

    def resetRun(self) -> None:
        # Reset player
        self.player.currPos = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )
        self.player.jumpPressed = False
        self.player.state = "IDLE"
        self.player.velocity = pygame.Vector2(0, 0)

        # Reset score + collectibles
        self.score = 0
        self.coins.clear()

        # Reset obstacles
        self.pipes.clear()

        # Reset run systems (THIS is the "t = 0" equivalent now)
        self.section_manager.reset()
        self.progression.reset()

        # Reset time so dt doesn't spike
        self.engine.resetClock()

        # Unpause gameplay
        self.isPaused = False


    # Interact with the env.
    def update(self) -> None:
        events = pygame.event.get()

        self._currState.handler(events)
        self._currState.update()
        self._currState.draw()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_e:
                        self.sound.changeSfxVolume(0.2)
                        SettingsManager.setUserPreferences({"sfx": self.sound.sfxVolume})
                    case pygame.K_q:
                        self.sound.changeSfxVolume(-0.2)
                        SettingsManager.setUserPreferences({"sfx": self.sound.sfxVolume})
                    case pygame.K_d:
                        self.sound.changeMusicVolume(0.2)
                        SettingsManager.setUserPreferences({"music": self.sound.musicVolume})
                    case pygame.K_a:
                        self.sound.changeMusicVolume(-0.2)
                        SettingsManager.setUserPreferences({"music": self.sound.musicVolume})
