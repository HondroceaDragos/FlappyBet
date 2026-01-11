import pygame
from ._abs_state import absState


# 'GameInProgressState' class declaration and definition
class GameInProgressState(absState):
    def onEnter(self) -> None:
        self.master.sound.playMusic("gameLoop")

    def onExit(self):
        pygame.mixer.music.fadeout(500)

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        self.master.player.jumpPressed = True
                        self.master.engine.jump(self.master.player)
                        self.master.sound.playSfx("playerJump")
                    case pygame.K_ESCAPE:
                        self.master.switchGameState("pauseMenu")

            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.master.player.jumpPressed = False

    def draw(self) -> None:
        self.master.screen.fill("white")
        self.master.player.draw()
        for pipe in self.master.pipes:
            pipe.draw()

    def _updateEnv(self) -> None:
        self.master.engine.updateDt()
        self.master.engine.applyGravity(self.master.player)

        # Create new pipes as time passes
        self.master.factory.update(self.master.engine._dt)
        if self.master.factory.shouldSpawn():
            self.master.pipes.append(self.master.factory.spawn())

        # Update each new pipe
        alivePipes = []
        for pipe in self.master.pipes:
            pipe.update(self.master.engine._dt)

            if pipe.shouldKill() is False:
                alivePipes.append(pipe)

            if self.master.engine.checkCollision(self.master.player, pipe):
                self._resetState()
                self.master.sound.playSfx("playerDeath")
                return
        self.master.pipes = alivePipes

    # Start new game upon death
    def _resetState(self) -> None:
        self.master.player.currPos = pygame.Vector2(
            self.master.screen.get_width() / 2, self.master.screen.get_height() / 2
        )
        self.master.player.velocity.y = 0
        self.master.pipes.clear()

    # Call animation engine
    def _updatePlayer(self) -> None:
        self.master.player.decideState()
        self.master.player.animatePlayer()

    def update(self) -> None:
        if getattr(self.master, "isPaused", False):
            return
        self._updateEnv()
        self._updatePlayer()
        self.draw()
