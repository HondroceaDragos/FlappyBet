import pygame

from entities import Player
from entities import PipeFactory

from core import PhysicsEngine
from core import MainMenuState
from core import GameInProgressState


# 'GameMaster' class declaration and definition
class GameMaster:
    def __init__(
        self,
        screen: pygame.Surface,
        engine: PhysicsEngine = None,
        player: Player = None,
        factory: PipeFactory = None,
        running: bool = False,
    ):
        self.screen = screen
        self.engine = engine

        self.player = player
        self.factory = factory
        self.pipes = []

        self.running = running

        # Load all possible states into the master
        self.states = {
            "mainMenu": MainMenuState(self),
            "gameInProgress": GameInProgressState(self),
        }

        # Start from main menu
        self._currState = self.states["mainMenu"]

    # Action may cause game switches
    def switchGameState(self, state: str) -> None:
        self._currState = self.states[state]

    # Interact with the env.
    def update(self) -> None:
        events = pygame.event.get()

        self._currState.handler(events)
        self._currState.draw()
        self._currState.update()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
