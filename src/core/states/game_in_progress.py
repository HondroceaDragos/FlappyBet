import pygame
from ._abs_state import absState

# 'GameInProgressState' class declaration and definition
class GameInProgressState(absState):
    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        self.master.player.jumpPressed = True
                        self.master.engine.jump(self.master.player)
                    case pygame.K_ESCAPE:
                        self.master.switchGameState("mainMenu")
            
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    self.master.player.jumpPressed = False

    def draw(self) -> None:
        self.master.screen.fill("white")
        self.master.player.draw()
        self.master.enemy.draw()

    def _updateEnv(self) -> None:
        self.master.engine.updateDt()
        self.master.engine.applyGravity(self.master.player)
        self.master.enemy.update()

    # Call animation engine
    def _updatePlayer(self) -> None:
        self.master.player.decideState()
        self.master.player.animatePlayer()

    def update(self) -> None:
        self.master.engine._clock.tick()

        self._updateEnv()
        self._updatePlayer()
        self.draw()

        # Sanity check for collision - will be moved
        if self.master.engine.checkCollision(self.master.player, self.master.enemy):
            self.master.player.currPos = pygame.Vector2(self.master.screen.get_width() / 2, self.master.screen.get_height())
            self.master.player.velocity.y = 0
