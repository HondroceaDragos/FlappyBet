import pygame
from ._abs_state import absState


class GameInProgressState(absState):
    def onEnter(self) -> None:
        self.master.sound.playMusic("gameLoop")

    def onExit(self):
        pass

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

    def _circle_circle_col(self, c1: pygame.Vector2, r1: float, c2: pygame.Vector2, r2: float) -> bool:
        dx = c1.x - c2.x
        dy = c1.y - c2.y
        return (dx * dx + dy * dy) < (r1 + r2) * (r1 + r2)

    def draw(self) -> None:
        self.master.screen.fill("white")

        self.master.player.draw()

        for obs in self.master.pipes:
            obs.draw()

        for coin in self.master.coins:
            coin.draw()

        font = pygame.font.Font(None, 42)
        s = font.render(f"Score: {self.master.score}", True, "black")
        sec = self.master.section_manager.getSectionName()
        tier = self.master.section_manager.getTier()
        t = font.render(f"Section: {sec} (tier {tier})", True, "black")
        self.master.screen.blit(s, (20, 18))
        self.master.screen.blit(t, (20, 55))

    def _updateEnv(self) -> None:
        self.master.engine.updateDt()
        dt = self.master.engine._dt

        self.master.engine.applyGravity(self.master.player)

        self.master.progression.update(dt)

        self.master.section_manager.update(dt)

        new_obs, new_coins = self.master.section_manager.maybe_spawn(
            hazard_intensity=self.master.progression.hazard_intensity
        )

        if new_obs:
            self.master.pipes.extend(new_obs)
        if new_coins:
            self.master.coins.extend(new_coins)

        alive_obs = []
        for obs in self.master.pipes:
            obs.update(dt)

            if not obs.shouldKill():
                alive_obs.append(obs)

            if self.master.engine.checkCollision(self.master.player, obs):
                # Walkable tunnel walls are non-lethal solids
                if hasattr(obs, "lethal") and obs.lethal is False:
                    self.master.engine.resolveSolidCircleRect(self.master.player, obs.getHitbox())
                else:
                    self.master.sound.playSfx("playerDeath")
                    # Store score later; for now just 0
                    self.master.lastScore = getattr(self.master, "score", 0)
                    self.master.switchGameState("gameOver")
                    return

        self.master.pipes = alive_obs

        playerCenter, playerRadius = self.master.player.getHitbox()
        alive_coins = []
        for coin in self.master.coins:
            coin.update(dt)
            if coin.shouldKill():
                continue

            coinCenter, coinRadius = coin.getHitbox()
            dx = playerCenter.x - coinCenter.x
            dy = playerCenter.y - coinCenter.y
            if (dx * dx + dy * dy) < (playerRadius + coinRadius) ** 2:
                coin.collected = True
                self.master.score += coin.value
                self.master.progression.addCoins(coin.value)
                continue

            alive_coins.append(coin)
        self.master.coins = alive_coins


    def _resetState(self) -> None:
        self.master.player.currPos = pygame.Vector2(
            self.master.screen.get_width() / 2, self.master.screen.get_height() / 2
        )
        self.master.player.velocity.y = 0

        self.master.pipes.clear()
        self.master.coins.clear()

        self.master.score = 0
        self.master.section_manager.reset()
        self.master.progression.reset()

        self.master.engine.resetClock()

    def _updatePlayer(self) -> None:
        self.master.player.decideState()
        self.master.player.animatePlayer()

    def update(self) -> None:
        if getattr(self.master, "isPaused", False):
            return
        self._updateEnv()
        self._updatePlayer()
        self.draw()
