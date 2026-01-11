import pygame
from ._abs_state import absState


class SlotsState(absState):
    def onEnter(self) -> None:
        # Future: initialize slot machine UI / RNG / animations
        pass

    def onExit(self) -> None:
        pass

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Go back to game over screen
                self.master.switchGameState("gameOver")
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Placeholder: a simple Back button
                if self._back_rect.collidepoint(mx, my):
                    self.master.switchGameState("gameOver")
                    return

    def update(self) -> None:
        # Future: animate reels, handle bets
        pass

    def draw(self) -> None:
        self.master.screen.fill((15, 15, 20))

        w, h = self.master.screen.get_size()
        title_font = pygame.font.Font(None, 90)
        text_font = pygame.font.Font(None, 44)

        title = title_font.render("SLOTS (WIP)", True, (240, 240, 240))
        self.master.screen.blit(title, ((w - title.get_width()) // 2, 80))

        msg = text_font.render("Press ESC or click Back", True, (200, 200, 200))
        self.master.screen.blit(msg, ((w - msg.get_width()) // 2, 180))

        # Back button
        btn_w, btn_h = 260, 70
        btn_x = (w - btn_w) // 2
        btn_y = h - btn_h - 90
        self._back_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        pygame.draw.rect(self.master.screen, (80, 80, 90), self._back_rect, border_radius=14)
        pygame.draw.rect(self.master.screen, (220, 220, 220), self._back_rect, 3, border_radius=14)

        label = text_font.render("Back", True, (240, 240, 240))
        self.master.screen.blit(
            label,
            (btn_x + (btn_w - label.get_width()) // 2, btn_y + (btn_h - label.get_height()) // 2),
        )
