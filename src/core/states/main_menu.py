import pygame
from ._abs_state import absState


# 'MainMenuState' class declaration and definition
class MainMenuState(absState):
    # @Override
    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.master.switchGameState("gameInProgress")

    # Reset gameplay parameters - acts as new game
    def _resetGame(self) -> None:
        self.master.player.currPos = pygame.Vector2(
            self.master.screen.get_width() / 2, self.master.screen.get_height() / 2
        )
        self.master.player.jumpPressed = False
        self.master.player.state = "IDLE"
        self.master.player.velocity = pygame.Vector2(0, 0)

        self.master.enemy.currPos = pygame.Vector2(
            self.master.screen.get_width() + 20, -20
        )

    def update(self) -> None:
        self._resetGame()

    # To be changed with interactible buttons
    def draw(self) -> None:
        self.master.screen.fill("white")

        mainMenuFont = pygame.font.Font(None, 128)

        mainMenuText = mainMenuFont.render("This will be the main menu!", True, "black")
        actionText = mainMenuFont.render("Press [SPACE] to start!", True, "black")

        self.master.screen.blit(mainMenuText, (0, 0))
        self.master.screen.blit(actionText, (0, 128))
