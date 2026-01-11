import pygame
from ._abs_state import absState


class MainMenuState(absState):
    def onEnter(self) -> None:
        self.master.sound.playMusic("mainMenu")

    def onExit(self):
        pygame.mixer.music.fadeout(500)

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.master.switchGameState("gameInProgress")

    def _resetGame(self) -> None:
        self.master.player.currPos = pygame.Vector2(
            self.master.screen.get_width() / 2, self.master.screen.get_height() / 2
        )
        self.master.player.jumpPressed = False
        self.master.player.state = "IDLE"
        self.master.player.velocity = pygame.Vector2(0, 0)

        self.master.pipes.clear()
        self.master.coins.clear()

        self.master.engine.resetClock()

        self.master.score = 0
        self.master.section_manager.reset()
        self.master.progression.reset()

    def update(self) -> None:
        self._resetGame()

    def draw(self) -> None:
        self.master.screen.fill("white")

        mainMenuFont = pygame.font.Font(None, 96)

        mainMenuText = mainMenuFont.render("FlappyBet Mine Escape", True, "black")
        actionText = mainMenuFont.render("Press [SPACE] to start!", True, "black")

        self.master.screen.blit(mainMenuText, (30, 60))
        self.master.screen.blit(actionText, (30, 170))
