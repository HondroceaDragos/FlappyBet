import pygame
from ._abs_state import absState


class MainMenuState(absState):
    def onEnter(self) -> None:
        self.master.isPaused = False
        self.master.engine.resetClock()
        self.master.sound.playMusic("mainMenu")

    def onExit(self):
        pygame.mixer.music.fadeout(500)

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.master.switchGameState("gameInProgress")
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # If draw() hasn't run yet, these rects may not exist
                if hasattr(self, "_start_rect") and self._start_rect.collidepoint(mx, my):
                    self.master.switchGameState("gameInProgress")
                    return

                if hasattr(self, "_help_rect") and self._help_rect.collidepoint(mx, my):
                    self.master.switchGameState("help")
                    return

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
        self.master.isPaused = False

        self.master.score = 0
        self.master.section_manager.reset()
        self.master.progression.reset()

        self.master.score = 0
        self.master.section_manager.reset()
        self.master.progression.reset()

    def update(self) -> None:
        self._resetGame()

    def draw(self) -> None:
        self.master.screen.fill((245, 245, 245))
        w, h = self.master.screen.get_size()

        title_font = pygame.font.Font(None, 140)
        btn_font = pygame.font.Font(None, 60)
        small_font = pygame.font.Font(None, 36)

        # Title
        title = title_font.render("FlappyBet", True, (20, 20, 20))
        self.master.screen.blit(title, ((w - title.get_width()) // 2, int(h * 0.22)))

        # Buttons
        btn_w, btn_h = 320, 78
        x = (w - btn_w) // 2
        y0 = int(h * 0.45)
        gap = 20

        self._start_rect = pygame.Rect(x, y0, btn_w, btn_h)
        self._help_rect = pygame.Rect(x, y0 + btn_h + gap, btn_w, btn_h)

        mx, my = pygame.mouse.get_pos()

        def draw_button(rect: pygame.Rect, label: str):
            hovered = rect.collidepoint(mx, my)
            fill = (60, 140, 255) if hovered else (70, 70, 80)

            pygame.draw.rect(self.master.screen, fill, rect, border_radius=16)
            pygame.draw.rect(self.master.screen, (30, 30, 30), rect, 3, border_radius=16)

            t = btn_font.render(label, True, (255, 255, 255))
            self.master.screen.blit(
                t,
                (rect.x + (rect.w - t.get_width()) // 2,
                 rect.y + (rect.h - t.get_height()) // 2),
            )

        draw_button(self._start_rect, "Start")
        draw_button(self._help_rect, "Help")

        hint = small_font.render("Tip: SPACE also starts", True, (90, 90, 90))
        self.master.screen.blit(hint, ((w - hint.get_width()) // 2, int(h * 0.80)))
        mainMenuFont = pygame.font.Font(None, 96)

        mainMenuText = mainMenuFont.render("FlappyBet Mine Escape", True, "black")
        actionText = mainMenuFont.render("Press [SPACE] to start!", True, "black")

        self.master.screen.blit(mainMenuText, (30, 60))
        self.master.screen.blit(actionText, (30, 170))
