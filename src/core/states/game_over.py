import pygame
from ._abs_state import absState


class GameOverState(absState):
    def onEnter(self) -> None:
        # Stop gameplay
        self.master.isPaused = True
        self.master.engine.resetClock()
        self.master.sound.playMusic("mainMenu")

        # Placeholder score value (until you implement scoring)
        # If later you store it in master.score, use that.
        self._final_score = getattr(self.master, "lastScore", 0)

        # Optional: play music or death sting (you already play sfx on death)
        # self.master.sound.playMusic("mainMenu")  # or another track

    def onExit(self) -> None:
        pass

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Retry
                    self.master.resetRun()
                    self.master.switchGameState("gameInProgress")
                    return
                if event.key == pygame.K_ESCAPE:
                    self.master.isPaused = False
                    self.master.engine.resetClock()
                    self.master.switchGameState("mainMenu")
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if self._slots_rect.collidepoint(mx, my):
                    self.master.bank = getattr(self.master, "lastScore", 0)
                    # keep bet sane
                    self.master.bet = min(getattr(self.master, "bet", 10), self.master.bank)
                    self.master.switchGameState("slots")
                    return

                if self._retry_rect.collidepoint(mx, my):
                    self.master.isPaused = False
                    self.master.resetRun()
                    self.master.switchGameState("gameInProgress")
                    return

                if self._menu_rect.collidepoint(mx, my):
                    self.master.isPaused = False
                    self.master.engine.resetClock()
                    self.master.switchGameState("mainMenu")
                    return

    def update(self) -> None:
        # Static screen, no physics/spawns
        pass

    def draw(self) -> None:
        self.master.screen.fill((10, 10, 10))
        w, h = self.master.screen.get_size()

        title_font = pygame.font.Font(None, 110)
        text_font = pygame.font.Font(None, 52)

        title = title_font.render("GAME OVER", True, (240, 240, 240))
        self.master.screen.blit(title, ((w - title.get_width()) // 2, 80))

        score_text = text_font.render(f"Score: {self._final_score}", True, (210, 210, 210))
        self.master.screen.blit(score_text, ((w - score_text.get_width()) // 2, 220))

        # Buttons
        btn_w, btn_h = 340, 72
        x = (w - btn_w) // 2
        y0 = 320
        gap = 22

        self._slots_rect = pygame.Rect(x, y0, btn_w, btn_h)
        self._retry_rect = pygame.Rect(x, y0 + (btn_h + gap), btn_w, btn_h)
        self._menu_rect  = pygame.Rect(x, y0 + 2 * (btn_h + gap), btn_w, btn_h)

        mx, my = pygame.mouse.get_pos()

        def draw_btn(rect: pygame.Rect, label: str):
            hovered = rect.collidepoint(mx, my)
            fill = (60, 140, 255) if hovered else (70, 70, 80)

            pygame.draw.rect(self.master.screen, fill, rect, border_radius=14)
            pygame.draw.rect(self.master.screen, (220, 220, 220), rect, 3, border_radius=14)
            t = text_font.render(label, True, (240, 240, 240))
            self.master.screen.blit(
                t,
                (rect.x + (rect.w - t.get_width()) // 2,
                 rect.y + (rect.h - t.get_height()) // 2),
            )

        draw_btn(self._slots_rect, "Slots")
        draw_btn(self._retry_rect, "Retry (R)")
        draw_btn(self._menu_rect, "Main Menu (ESC)")

        hint_font = pygame.font.Font(None, 34)
        hint = hint_font.render("Tip: press R to retry", True, (160, 160, 160))
        self.master.screen.blit(hint, ((w - hint.get_width()) // 2, h - 70))
